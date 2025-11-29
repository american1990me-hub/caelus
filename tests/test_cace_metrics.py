from __future__ import annotations

import numpy as np

from caelus.cace.metrics import spectral_coherence, block_coherence, tensor_coherence, TensorCoherenceConfig


def test_spectral_coherence_in_range() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=(16, 8))
    c = spectral_coherence(x)
    assert 0.0 <= c <= 1.0


def test_block_coherence_in_range() -> None:
    rng = np.random.default_rng(1)
    x = rng.normal(size=(16, 16))
    c = block_coherence(x, block_rows=4, block_cols=4)
    assert 0.0 <= c <= 1.0


def test_tensor_coherence_swirl_higher_than_random() -> None:
    # Construct a simple coherent field (swirl-like pattern)
    n = 32
    x = np.linspace(-1.0, 1.0, n)
    y = np.linspace(-1.0, 1.0, n)
    X, Y = np.meshgrid(x, y, indexing="ij")
    swirl = -Y + 0.1 * X  # some structured pattern

    rng = np.random.default_rng(2)
    rand = rng.normal(size=swirl.shape)

    cfg = TensorCoherenceConfig(alpha=0.7, block_rows=4, block_cols=4)
    c_swirl = tensor_coherence(swirl, cfg)
    c_rand = tensor_coherence(rand, cfg)

    assert 0.0 <= c_swirl <= 1.0
    assert 0.0 <= c_rand <= 1.0
    assert c_swirl > c_rand
