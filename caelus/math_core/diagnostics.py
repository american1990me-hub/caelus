from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .fields import Array
from .coherence import CoherenceContract


@dataclass
class CoherenceDiagnostics:
    C: float
    gamma_fd: float
    gamma_spec: float | None
    l2_psi: float
    l2_u: float


def compute_diagnostics(
    psi: Array,
    u: Array,
    contract: CoherenceContract,
    use_spectral: bool = True,
) -> CoherenceDiagnostics:
    """Compute a bundle of coherence-related scalars from ψ and u."""
    C_val = contract.C(psi)
    gamma_fd = contract.gamma(u)

    gamma_spec: float | None = None
    if (
        use_spectral
        and psi.ndim == 2
        and u.ndim == 3
        and u.shape[-1] in (2, 3)
    ):
        gamma_spec = contract.gamma_spectral_2d(u)

    l2_psi = float(np.linalg.norm(psi))
    l2_u = float(np.linalg.norm(u))

    return CoherenceDiagnostics(
        C=C_val,
        gamma_fd=gamma_fd,
        gamma_spec=gamma_spec,
        l2_psi=l2_psi,
        l2_u=l2_u,
    )
