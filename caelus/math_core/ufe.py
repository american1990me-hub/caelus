from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .fields import Array
from .coherence import CoherenceContract


@dataclass
class UFEStepper:
    """Minimal Unruh-Fulling effect simulator via phase field evolution."""

    contract: CoherenceContract
    dt: float = 0.01

    def step(self, psi: Array) -> tuple[Array, float, float]:
        """Single step of the phase-only Cahn-Hilliard equation."""
        dC_dpsi_star = self.contract.dC_dpsi_star(psi)
        psi_new = psi - self.dt * dC_dpsi_star

        # Project back to the unit circle (phase-only constraint)
        psi_new /= np.abs(psi_new) + 1e-9

        C_new = self.contract.C(psi_new)
        return psi_new, C_new, self.dt
