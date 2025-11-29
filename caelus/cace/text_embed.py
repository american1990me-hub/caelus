from __future__ import annotations

from typing import List

import numpy as np

Array = np.ndarray


def _text_to_ints(text: str) -> List[int]:
    """Map text to a list of integer codes in a deterministic way.

    - Lowercase
    - Keep only a–z, digits, '_', '-', and space
    - Map others to 0
    """
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789_- "
    mapping = {ch: i + 1 for i, ch in enumerate(allowed)}  # codes 1..len(allowed)
    out: List[int] = []
    for ch in text.lower():
        out.append(mapping.get(ch, 0))
    return out


def embed_text_to_vec(text: str, dim: int = 32, seed: int = 0) -> Array:
    """Deterministically embed text into R^dim.

    Strategy:
      - Convert text to ints.
      - Normalize ints to a unit vector.
      - Seed a PRNG with (seed XOR sum(ints)).
      - Sample a Gaussian projection matrix W ∈ R^{dim × L}.
      - v = W @ x, then L2-normalize v.
    """
    ints = _text_to_ints(text)
    if not ints:
        return np.zeros((dim,), dtype=float)

    x = np.array(ints, dtype=float)
    norm = np.linalg.norm(x)
    if norm > 0.0:
        x = x / norm

    effective_seed = int(seed) ^ int(sum(ints) & 0xFFFFFFFF)
    rng = np.random.default_rng(effective_seed)

    W = rng.normal(size=(dim, x.shape[0]))
    v = W @ x

    v_norm = np.linalg.norm(v)
    if v_norm > 0.0:
        v = v / v_norm
    return v
