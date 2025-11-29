from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

Array = np.ndarray


def _as_2d(x: Array) -> Array:
    """Return x as a 2D array (m, n) by flattening leading dims.

    If x is 1D, treat it as (1, n).
    """
    if x.ndim == 1:
        return x.reshape(1, -1)
    if x.ndim == 2:
        return x
    # Collapse all but last dim into row dimension
    m = int(np.prod(x.shape[:-1]))
    return x.reshape(m, x.shape[-1])


def spectral_coherence(x: Array, rank_max: int | None = None) -> float:
    """Compute spectral coherence c_spec(x) in [0, 1].

    Steps:
      - View x as 2D (m, n).
      - Compute singular values σ_i.
      - Let p_i = σ_i^2 / Σ σ_j^2.
      - Spectral entropy S = -Σ p_i log(p_i).
      - Normalize: c_spec = 1 - S / log(r), where r = # singular values used.

    Degenerate cases (all zeros, NaNs/Infs) yield 0.0.
    """
    mat = _as_2d(np.asarray(x, dtype=float))
    m, n = mat.shape
    if m == 0 or n == 0:
        return 0.0

    # Handle exact zeros: no structure
    if not np.isfinite(mat).all():
        return 0.0
    if np.allclose(mat, 0.0):
        return 0.0

    # Full SVD for v1 (small matrices); can be optimized/truncated later.
    try:
        # full_matrices=False gives min(m, n) singular values
        _, s, _ = np.linalg.svd(mat, full_matrices=False)
    except np.linalg.LinAlgError:
        return 0.0

    # Limit rank if requested
    if rank_max is not None and rank_max > 0:
        s = s[: min(rank_max, s.shape[0])]

    s2 = s * s
    E = float(np.sum(s2))
    if E <= 0.0 or not np.isfinite(E):
        return 0.0

    p = s2 / E
    # Guard against log(0)
    p = np.clip(p, 1e-12, 1.0)
    S = float(-np.sum(p * np.log(p)))

    r = p.shape[0]
    if r <= 1:
        return 1.0  # single-mode, maximal coherence

    S_max = np.log(r)
    if S_max <= 0.0:
        return 0.0

    c_spec = 1.0 - S / S_max
    # Clamp to [0,1]
    return float(max(0.0, min(1.0, c_spec)))


def _split_indices(n: int, blocks: int) -> list[Tuple[int, int]]:
    """Split [0, n) into `blocks` contiguous segments.

    Returns list of (start, end) indices covering [0, n) without overlap.
    """
    if blocks <= 1 or n <= 1:
        return [(0, n)]

    base = n // blocks
    rem = n % blocks
    segments = []
    start = 0
    for i in range(blocks):
        size = base + (1 if i < rem else 0)
        end = start + size
        segments.append((start, end))
        start = end
    return segments


def block_coherence(x: Array, block_rows: int = 3, block_cols: int = 3) -> float:
    """Compute block-structure coherence c_block(x) in [0,1].

    Heuristic:
      - View x as 2D (m, n).
      - Partition rows into block_rows segments, cols into block_cols.
      - For each block, flatten to vector and L2-normalize.
      - Compute cosine similarity for all distinct pairs of blocks.
      - Let Ā = mean cosine similarity.
      - Map cos in [-1,1] to [0,1] via (Ā + 1)/2.

    Empty or degenerate inputs yield 0.0.
    """
    mat = _as_2d(np.asarray(x, dtype=float))
    m, n = mat.shape
    if m == 0 or n == 0:
        return 0.0
    if not np.isfinite(mat).all():
        return 0.0

    row_segments = _split_indices(m, block_rows)
    col_segments = _split_indices(n, block_cols)

    # Collect block vectors
    blocks: list[Array] = []
    for rs in row_segments:
        r0, r1 = rs
        for cs in col_segments:
            c0, c1 = cs
            block = mat[r0:r1, c0:c1]
            if block.size == 0:
                continue
            v = block.reshape(-1)
            # Normalize
            norm = np.linalg.norm(v)
            if norm == 0.0 or not np.isfinite(norm):
                continue
            blocks.append(v / norm)

    if len(blocks) < 2:
        return 0.0

    # Pad blocks to the same size to handle non-uniform block dimensions.
    max_len = max(v.size for v in blocks)
    padded_blocks: list[Array] = []
    for v in blocks:
        if v.size < max_len:
            # Pad with zeros to the right
            padded_v = np.pad(v, (0, max_len - v.size), "constant")
            padded_blocks.append(padded_v)
        else:
            padded_blocks.append(v)


    # Compute pairwise cosine similarities
    sims: list[float] = []
    for i in range(len(padded_blocks)):
        vi = padded_blocks[i]
        for j in range(i + 1, len(padded_blocks)):
            vj = padded_blocks[j]
            dot = float(np.dot(vi, vj))
            # Numerical guard
            if not np.isfinite(dot):
                continue
            # Clip to [-1,1]
            dot = max(-1.0, min(1.0, dot))
            sims.append(dot)

    if not sims:
        return 0.0

    A_bar = float(np.mean(sims))
    # Map [-1,1] → [0,1]
    c_block = 0.5 * (A_bar + 1.0)
    return float(max(0.0, min(1.0, c_block)))


@dataclass
class TensorCoherenceConfig:
    alpha: float = 0.7
    block_rows: int = 3
    block_cols: int = 3
    rank_max: int | None = None


def tensor_coherence(x: Array, cfg: TensorCoherenceConfig | None = None) -> float:
    """Combined tensor coherence c(x) = α c_spec + (1-α) c_block in [0,1]."""
    if cfg is None:
        cfg = TensorCoherenceConfig()

    c_spec = spectral_coherence(x, rank_max=cfg.rank_max)
    c_blk = block_coherence(x, block_rows=cfg.block_rows, block_cols=cfg.block_cols)

    alpha = max(0.0, min(1.0, cfg.alpha))
    c = alpha * c_spec + (1.0 - alpha) * c_blk
    return float(max(0.0, min(1.0, c)))


def coherence_flux(c_val: float, tensor: Array) -> float:
    """Simple coherence flux J_c = c(x) * ||x||_F.

    Used to approximate how much coherent "mass" flows through a layer.
    """
    norm = float(np.linalg.norm(tensor))
    if not np.isfinite(norm):
        return 0.0
    return float(max(0.0, c_val) * norm)
