from __future__ import annotations

import numpy as np

from caelus.cace.cam import cam_matmul, CAMConfig


def test_cam_matmul_shapes_and_receipt() -> None:
    rng = np.random.default_rng(0)
    d_in = 10
    d_out = 6
    B = 4

    W = rng.normal(size=(d_out, d_in))
    X = rng.normal(size=(d_in, B))

    cfg = CAMConfig(alpha=0.7, tau_high=0.6, tau_mid=0.3, rank_max=4)
    Y, rec = cam_matmul(W, X, layer_id="L0", cfg=cfg)

    assert Y.shape == (d_out, B)
    assert rec["op"] == "CAM"
    assert rec["layer_id"] == "L0"
    assert "coherence" in rec
    assert "flux" in rec
    assert "residual" in rec

    coh = rec["coherence"]
    assert 0.0 <= coh["c_W"] <= 1.0
    assert 0.0 <= coh["c_X"] <= 1.0
    assert 0.0 <= coh["c_in"] <= 1.0
    assert 0.0 <= coh["c_out"] <= 1.0


def test_cam_low_rank_path_triggered() -> None:
    # Use a strongly coherent W (rank-1) to trigger low-rank branch
    rng = np.random.default_rng(1)
    d_in = 12
    d_out = 9
    B = 5

    v = rng.normal(size=(d_in,))
    u = rng.normal(size=(d_out,))
    W = np.outer(u, v)  # rank-1
    X = rng.normal(size=(d_in, B))

    cfg = CAMConfig(alpha=0.9, tau_high=0.5, tau_mid=0.2, rank_max=3)
    Y, rec = cam_matmul(W, X, layer_id="L_coherent", cfg=cfg)

    # Check that at least one block used low-rank approx (rank_used > 0)
    rank_used = rec["approx"]["rank_used"]
    assert any(r > 0 for r in rank_used.values())
