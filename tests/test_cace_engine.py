from __future__ import annotations

import numpy as np

from caelus.cace.engine import DenseLayerParams, CACEConfig, CACEEngine
from caelus.cace.cam import CAMConfig


def test_cace_engine_forward_deterministic() -> None:
    rng = np.random.default_rng(0)
    B = 3
    d_in = 5
    d_hid = 7
    d_out = 2

    W1 = rng.normal(size=(d_hid, d_in))
    b1 = rng.normal(size=(d_hid,))
    W2 = rng.normal(size=(d_out, d_hid))
    b2 = rng.normal(size=(d_out,))

    layers = [
        DenseLayerParams(W=W1, b=b1, layer_id="L1", activation="relu"),
        DenseLayerParams(W=W2, b=b2, layer_id="L2", activation="none"),
    ]

    cfg = CACEConfig(cam_config=CAMConfig(alpha=0.7, tau_high=0.7, tau_mid=0.3, rank_max=4))
    engine = CACEEngine(layers, config=cfg)

    x = rng.normal(size=(B, d_in))

    y1, receipts1 = engine.forward(x)
    y2, receipts2 = engine.forward(x)

    # Deterministic
    assert np.allclose(y1, y2)
    assert len(receipts1) == len(receipts2) == 2


def test_cace_engine_output_shape() -> None:
    rng = np.random.default_rng(1)
    B = 4
    d_in = 8
    d_out = 3

    W = rng.normal(size=(d_out, d_in))
    b = rng.normal(size=(d_out,))

    layers = [DenseLayerParams(W=W, b=b, layer_id="L", activation="none")]
    engine = CACEEngine(layers, config=None)

    x = rng.normal(size=(B, d_in))
    y, receipts = engine.forward(x)

    assert y.shape == (B, d_out)
    assert len(receipts) == 1
