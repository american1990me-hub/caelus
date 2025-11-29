
from __future__ import annotations

import threading
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np

from ..math_core.coherence import CoherenceContract
from ..math_core.ufe import UFEStepper
from ..agent.loops import CaelusInnerLoop, make_initial_state
from ..ledger.signed_ledger import SignedOmegaLedger
from ..response.engine import build_response_from_sensory_with_context
from ..context.dialogue import load_context, save_context, DialogueContext
from ..cace.runtime_model import CACETextModelConfig, run_cace_for_text, ComputeCoherenceSnapshot
from ..cace.omega_bridge import (
    append_cace_receipts_to_ledger,
    append_compute_snapshot_to_ledger,
)
from ..context.policy import PolicyContext, load_policy_context, save_policy_context


def set_global_seeds(seed: int) -> None:
    """Set seeds for Python, NumPy, and (optionally) other RNGs."""
    random.seed(seed)
    np.random.seed(seed)


@dataclass
class CaelusRuntimeConfig:
    grid_size: int = 64
    steps: int = 3
    seed: int = 1234
    ledger_path: Path = Path("omega_signed.log")
    time_source: Callable[[], float] = time.time
    context_path: Path | None = None  # new
    policy_path: Path | None = None # new


def _default_context_path() -> Path:
    import os

    home = Path(os.path.expanduser("~"))
    return home / ".caelus" / "context.json"


def _default_policy_path() -> Path:
    import os

    home = Path(os.path.expanduser("~"))
    return home / ".caelus" / "policy.json"


class CaelusRuntime:
    def __init__(self, config: CaelusRuntimeConfig):
        self.config = config
        self._lock = threading.Lock()
        self.last_reply: str | None = None
        self.last_compute_snapshot: ComputeCoherenceSnapshot | None = None
        self.last_policy_record: dict | None = None  # NEW

    def run_session(self, sensory_text: str) -> str:
        """Run a Caelus session and return the generated reply text."""
        with self._lock:
            return self._run_session_locked(sensory_text)

    def _run_session_locked(self, sensory_text: str) -> str:
        set_global_seeds(self.config.seed)

        context_path = self.config.context_path or _default_context_path()
        ctx = load_context(context_path)

        policy_path = self.config.policy_path or _default_policy_path()
        policy_ctx = load_policy_context(policy_path)

        # --- Pre-computation policy update from dialogue ---
        policy_ctx.update_from_dialogue(ctx)

        contract = CoherenceContract()
        stepper = UFEStepper(contract)
        ledger = SignedOmegaLedger(
            self.config.ledger_path, time_source=self.config.time_source
        )
        inner = CaelusInnerLoop(stepper=stepper, contract=contract, ledger=ledger)

        state = make_initial_state(
            (self.config.grid_size, self.config.grid_size), contract
        )

        ledger.append(
            {
                "type": "session_start",
                "seed": self.config.seed,
                "grid_size": self.config.grid_size,
                "steps": self.config.steps,
                "sensory_preview": sensory_text[:64],
                "context": ctx.to_dict(),
            }
        )

        # UFE inner loop (existing)
        for _ in range(self.config.steps):
            state = inner.tick(state, sensory_raw={"text": sensory_text})

        ledger.append(
            {
                "type": "session_end",
                "C_final": state.C,
                "gamma_final": state.gamma,
            }
        )

        # --- CACE compute coherence for the input text with policy-controlled config ---
        cace_model_cfg = CACETextModelConfig(
            embed_dim=32,
            hidden_dim=32,
            output_dim=16,
            seed=self.config.seed,
            rank_max=policy_ctx.rank_max,
            tau_high=policy_ctx.tau_high,
            tau_mid=policy_ctx.tau_mid,
        )

        y_cace, receipts, snap = run_cace_for_text(sensory_text, cace_model_cfg)
        self.last_compute_snapshot = snap

        append_cace_receipts_to_ledger(
            ledger=ledger,
            engine_name="cace_text",
            receipts=receipts,
        )
        append_compute_snapshot_to_ledger(
            ledger=ledger,
            engine_name="cace_text",
            snap=snap,
        )

        # --- Policy update from coherence stats ---
        policy_record = policy_ctx.update_from_stats(
            field_gamma=state.gamma, snapshot=snap
        )
        self.last_policy_record = policy_record

        ledger.append(
            {
                "type": "cace_policy_update",
                "policy": policy_record,
            }
        )

        # --- Existing reply building logic with context ---
        if inner.last_sensory is not None:

            # Generate reply *before* updating context with new intent
            resp = build_response_from_sensory_with_context(inner.last_sensory, ctx)
            reply_text = resp["reply_text"]
            self.last_reply = reply_text

            # Update dialogue context *after* generating reply
            ctx.apply_intent(inner.last_sensory.utterance.intent)

            ledger.append(
                {
                    "type": "reply",
                    "reply_text": reply_text,
                    "plan": resp["plan"],
                    "context_after": ctx.to_dict(),
                    "compute_coherence_summary": {
                        "mean_c_in": snap.mean_c_in,
                        "mean_c_out": snap.mean_c_out,
                        "max_abs_R_c": snap.max_abs_R_c,
                        "num_layers": snap.num_layers,
                    },
                    "policy_after": policy_ctx.to_dict(),
                }
            )
        else:
            reply_text = "I did not receive any sensory input to respond to."
            self.last_reply = reply_text

        save_context(context_path, ctx)
        save_policy_context(policy_path, policy_ctx)
        return reply_text
