from __future__ import annotations

import numpy as np

from caelus.math_core.coherence import CoherenceContract
from caelus.math_core.diagnostics import compute_diagnostics
from caelus.math_core.test_fields import make_swirl_field


def test_diagnostics_returns_finite_values() -> None:
    contract = CoherenceContract()
    n = 32

    phase = np.random.randn(n, n)
    psi = np.exp(1j * phase)
    u = make_swirl_field(n)

    diag = compute_diagnostics(psi, u, contract)

    assert diag.C > 0.0
    assert 0.0 <= diag.gamma_fd <= 1.0
    if diag.gamma_spec is not None:
        assert 0.0 <= diag.gamma_spec <= 1.0
    assert diag.l2_psi > 0.0
    assert diag.l2_u > 0.0
