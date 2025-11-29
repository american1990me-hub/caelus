from __future__ import annotations

import numpy as np

from caelus.math_core.coherence import CoherenceContract


def test_gamma_zero_field_is_one() -> None:
    contract = CoherenceContract()
    u = np.zeros((16, 16, 3), dtype=float)
    gamma_val = contract.gamma(u)
    assert abs(gamma_val - 1.0) < 1e-9


def test_gamma_random_field_in_0_1() -> None:
    contract = CoherenceContract()
    rng = np.random.default_rng(1234)
    u = rng.random((32, 32, 3)) - 0.5
    gamma_val = contract.gamma(u)
    assert 0.0 <= gamma_val <= 1.0
    assert gamma_val < 0.9


def test_gamma_swirl_and_random_are_distinct_and_bounded() -> None:
    """Swirl and random fields should yield bounded but distinct Γ values.

    We do NOT assert swirl > random, because Γ is defined via Beltrami
    defect (ω ≈ λ u), and a non-Beltrami swirl can have worse alignment
    than a particular random field.
    """
    contract = CoherenceContract()
    n = 32
    x = np.linspace(-1.0, 1.0, n)
    y = np.linspace(-1.0, 1.0, n)
    X, Y = np.meshgrid(x, y, indexing="ij")

    ux = -Y
    uy = X
    uz = np.zeros_like(ux)
    u_swirl = np.stack([ux, uy, uz], axis=-1)
    mag = np.sqrt(ux**2 + uy**2) + 1e-9
    u_swirl = u_swirl / mag[..., None]

    rng = np.random.default_rng(42)
    u_rand = rng.random((n, n, 3)) - 0.5
    u_rand /= np.linalg.norm(u_rand, axis=-1, keepdims=True)

    gamma_swirl = contract.gamma(u_swirl)
    gamma_rand = contract.gamma(u_rand)

    # Boundedness
    assert 0.0 <= gamma_swirl <= 1.0
    assert 0.0 <= gamma_rand <= 1.0

    # Sensitivity: they should not collapse to the same value
    assert abs(gamma_swirl - gamma_rand) > 1e-3
