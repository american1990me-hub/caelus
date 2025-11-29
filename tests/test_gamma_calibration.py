from __future__ import annotations

import numpy as np

from caelus.math_core.coherence import CoherenceContract
from caelus.math_core.test_fields import make_swirl_field, make_random_field, add_galilean_boost


def test_spectral_gamma_swirl_and_random_are_distinct_and_bounded() -> None:
    """Spectral Γ should be bounded and distinguish swirl from random.

    We don't enforce an ordering between swirl and random for the same
    reason as in the finite-difference case: Γ measures Beltrami-style
    alignment, not "visual swirliness".
    """
    contract = CoherenceContract()
    n = 64
    swirl = make_swirl_field(n)
    rand = make_random_field(n, seed=123)
    rand /= np.linalg.norm(rand, axis=-1, keepdims=True)

    gamma_swirl = contract.gamma_spectral_2d(swirl)
    gamma_rand = contract.gamma_spectral_2d(rand)

    assert 0.0 <= gamma_swirl <= 1.0
    assert 0.0 <= gamma_rand <= 1.0
    assert abs(gamma_swirl - gamma_rand) > 1e-3

def test_spectral_gamma_galilean_invariance() -> None:
    contract = CoherenceContract()
    n = 64
    swirl = make_swirl_field(n)
    swirl_boost = add_galilean_boost(swirl, vx=0.5, vy=-0.3)

    g0 = contract.gamma_spectral_2d(swirl)
    g1 = contract.gamma_spectral_2d(swirl_boost)

    assert abs(g0 - g1) < 0.02


def test_spectral_gamma_resolution_stability() -> None:
    contract = CoherenceContract()
    n1 = 32
    n2 = 64

    swirl1 = make_swirl_field(n1)
    swirl2 = make_swirl_field(n2)

    g1 = contract.gamma_spectral_2d(swirl1)
    g2 = contract.gamma_spectral_2d(swirl2)

    assert 0.0 <= g1 <= 1.0
    assert 0.0 <= g2 <= 1.0
    assert abs(g1 - g2) < 0.05
