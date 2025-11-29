
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .dialogue import DialogueContext
from ..cace.runtime_model import ComputeCoherenceSnapshot
from ..policy.eldritch import EldritchState, state_from_stats, policy_from_eldritch_state


@dataclass
class PolicyContext:
    """Persistent policy state for CACE.

    Fields:
      - eldritch_state: [a, b, c] in Z3^3.
      - rank_max, tau_high, tau_mid: parameters fed into CAMConfig.
      - history: optional log of previous states/policies.
    """

    eldritch_state: List[int] = field(default_factory=lambda: [1, 1, 1])
    rank_max: int = 8
    tau_high: float = 0.7
    tau_mid: float = 0.3
    history: List[Dict[str, Any]] = field(default_factory=list)

    # ---- Derived helpers ----

    def eldritch(self) -> EldritchState:
        a, b, c = (self.eldritch_state + [1, 1, 1])[:3]
        return EldritchState(a=int(a), b=int(b), c=int(c))

    # ---- Update from dialogue ----

    def update_from_dialogue(self, dialogue: DialogueContext) -> Dict[str, Any]:
        """Update policy parameters based on dialogue context.

        This is a v1 heuristic to bump rigor.

        Returns a dict of the new policy parameters for logging.
        """
        if not dialogue.wants_more_rigor:
            return {}

        self.tau_high = min(0.9, self.tau_high + 0.1)
        self.tau_mid = min(0.5, self.tau_mid + 0.1)

        record = {
            "tau_high": self.tau_high,
            "tau_mid": self.tau_mid,
        }
        return record

    # ---- Update from coherence stats ----

    def update_from_stats(
        self,
        field_gamma: float,
        snapshot: ComputeCoherenceSnapshot,
    ) -> Dict[str, Any]:
        """Update eldritch_state and policy parameters based on coherence stats.

        Returns a dict of the new policy parameters for logging.
        """
        # Build state from current stats
        s_raw = state_from_stats(
            field_gamma=field_gamma,
            mean_c_out=snapshot.mean_c_out,
            concentration_proxy=snapshot.max_abs_R_c,
        )

        # Optionally apply one eldritch_step for memory
        s_prev = self.eldritch()
        s_next = s_raw
        # We could also mix s_prev and s_raw via eldritch_step, but v1 keeps it simple.
        # s_next = eldritch_step(s_prev)

        # Derive new policy from state, using current values as base
        params = policy_from_eldritch_state(
            state=s_next,
            base_rank_max=self.rank_max,
            base_tau_high=self.tau_high,
            base_tau_mid=self.tau_mid,
        )

        self.eldritch_state = [s_next.a, s_next.b, s_next.c]
        self.rank_max = int(params["rank_max"])
        self.tau_high = float(params["tau_high"])
        self.tau_mid = float(params["tau_mid"])

        record = {
            "eldritch_state": self.eldritch_state,
            "rank_max": self.rank_max,
            "tau_high": self.tau_high,
            "tau_mid": self.tau_mid,
            "field_gamma": float(field_gamma),
            "mean_c_out": float(snapshot.mean_c_out),
            "max_abs_R_c": float(snapshot.max_abs_R_c),
        }
        self.history.append(record)
        return record

    # ---- Serialization ----

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eldritch_state": list(self.eldritch_state),
            "rank_max": int(self.rank_max),
            "tau_high": float(self.tau_high),
            "tau_mid": float(self.tau_mid),
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyContext":
        return cls(
            eldritch_state=list(data.get("eldritch_state", [1, 1, 1])),
            rank_max=int(data.get("rank_max", 8)),
            tau_high=float(data.get("tau_high", 0.7)),
            tau_mid=float(data.get("tau_mid", 0.3)),
            history=list(data.get("history", [])),
        )


def load_policy_context(path: Path) -> PolicyContext:
    if not path.exists():
        return PolicyContext()
    import json
    raw = json.loads(path.read_text(encoding="utf-8"))
    return PolicyContext.from_dict(raw)


def save_policy_context(path: Path, ctx: PolicyContext) -> None:
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(ctx.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
