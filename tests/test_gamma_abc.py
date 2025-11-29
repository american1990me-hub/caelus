from __future__ import annotations

from caelus.math_core.coherence import CoherenceContract
from caelus.math_core.test_fields import make_abc_flow_3d, make_random_field_3d


def test_spectral_gamma_abc_near_one() -> None:
    """On an ABC Beltrami flow (curl(u) = u), the 3D spectral Γ should be ~1."""
    contract = CoherenceContract()
    n = 16  # small grid is enough; FFT matches the continuum exactly here

    u_abc = make_abc_flow_3d(n, n, n, A=1.0, B=1.0, C=1.0)
    gamma_abc = contract.gamma_spectral_3d(u_abc)

    # Very tight bound: we expect essentially exact 1.0
    assert 0.99 <= gamma_abc <= 1.001


def test_spectral_gamma_abc_greater_than_random() -> None:
    """ABC Beltrami flow should appear more coherent than a random 3D field."""
    contract = CoherenceContract()
    n = 16

    u_abc = make_abc_flow_3d(n, n, n, A=1.0, B=1.0, C=1.0)
    u_rand = make_random_field_3d(n, n, n, seed=123)

    gamma_abc = contract.gamma_spectral_3d(u_abc)
    gamma_rand = contract.gamma_spectral_3d(u_rand)

    assert 0.0 <= gamma_rand <= 1.0
    assert 0.99 <= gamma_abc <= 1.001
    assert gamma_abc > gamma_rand
