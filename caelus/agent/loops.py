from __future__ import annotations

from dataclasses import dataclass, asdict
import numpy as np
from typing import Any

from ..math_core.fields import Array, make_random_psi
from ..math_core.coherence import CoherenceContract
from ..math_core.ufe import UFEStepper
from ..math_core.diagnostics import compute_diagnostics
from ..ledger.signed_ledger import SignedOmegaLedger
from .sensory import parse_sensory_input, ParsedSensory


@dataclass
class InnerLoopState:
    psi: Array
    u: Array
    C: float
    gamma: float


@dataclass
class CaelusInnerLoop:
    stepper: UFEStepper
    contract: CoherenceContract
    ledger: SignedOmegaLedger
    last_sensory: ParsedSensory | None = None

    def tick(self, state: InnerLoopState, sensory_raw: dict[str, Any]) -> InnerLoopState:
        """One cognitive tick: sensory → update ψ → recompute Γ → log Ω entry."""
        sensory = parse_sensory_input(sensory_raw)
        self.last_sensory = sensory

        psi_new, _C_new, dt_used = self.stepper.step(state.psi)

        # derive a toy velocity field from phase gradient
        theta = np.angle(psi_new)
        vx, vy = np.gradient(theta)
        u_new = np.stack([vx, vy, np.zeros_like(vx)], axis=-1)

        diag = compute_diagnostics(psi_new, u_new, self.contract)

        payload = {
            "type": "inner_tick",
            "C_old": state.C,
            "C_new": diag.C,
            "gamma_old": state.gamma,
            "gamma_new": diag.gamma_fd,
            "dt": dt_used,
            "sensory": sensory.to_dict(),
            "diagnostics": asdict(diag),
        }
        self.ledger.append(payload)

        return InnerLoopState(
            psi=psi_new,
            u=u_new,
            C=diag.C,
            gamma=diag.gamma_fd,
        )


def make_initial_state(shape: tuple[int, int], contract: CoherenceContract) -> InnerLoopState:
    psi0 = make_random_psi(shape)
    vx0 = np.zeros(shape)
    vy0 = np.zeros(shape)
    u0 = np.stack([vx0, vy0, np.zeros_like(vx0)], axis=-1)
    C0 = contract.C(psi0)
    gamma0 = contract.gamma(u0)
    return InnerLoopState(psi=psi0, u=u0, C=C0, gamma=gamma0)
