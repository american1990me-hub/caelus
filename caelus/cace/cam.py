from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Any

import numpy as np

from .metrics import TensorCoherenceConfig, tensor_coherence, coherence_flux

Array = np.ndarray


@dataclass
class CAMConfig:
    alpha: float = 0.7
    tau_high: float = 0.75
    tau_mid: float = 0.4
    rank_max: int = 16
    block_rows: int = 3
    block_cols: int = 3
    S_c_model: float = 0.0  # expected coherence source term per layer


def _block_slices(n: int, blocks: int) -> list[Tuple[int, int]]:
    """Split dimension n into `blocks` contiguous segments."""
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


def cam_matmul(
    W: Array,
    X: Array,
    layer_id: str,
    cfg: CAMConfig | None = None,
) -> tuple[Array, Dict[str, Any]]:
    """Coherence-aware matmul Y = W @ X with per-layer CACE receipt.

    Shapes:
      - W: (d_out, d_in)
      - X: (d_in, B)
      - Y: (d_out, B)

    Strategy:
      - Compute global coherence for W and X.
      - Partition W (rows) and X (cols) into 3 segments each → 9 blocks.
      - For each (i, j):
          - Estimate local coherence from W_block and X_block.
          - If high coherence: use low-rank approximation for W_block.
          - Else: full matmul.
      - Aggregate coherence and flux metrics into a receipt.
    """
    if cfg is None:
        cfg = CAMConfig()

    W = np.asarray(W, dtype=float)
    X = np.asarray(X, dtype=float)

    d_out, d_in = W.shape
    d_in2, B = X.shape
    if d_in2 != d_in:
        raise ValueError(f"cam_matmul: shape mismatch W {W.shape}, X {X.shape}")

    # Global coherence
    tc_cfg = TensorCoherenceConfig(
        alpha=cfg.alpha,
        block_rows=cfg.block_rows,
        block_cols=cfg.block_cols,
        rank_max=None,
    )
    c_W = tensor_coherence(W, tc_cfg)
    c_X = tensor_coherence(X, tc_cfg)
    c_in = 0.5 * (c_W + c_X)

    # Prepare output
    Y = np.zeros((d_out, B), dtype=float)

    row_segs = _block_slices(d_out, cfg.block_rows)
    col_segs = _block_slices(B, cfg.block_cols)

    rank_used: Dict[str, int] = {}
    total_flops_full = 2.0 * d_out * d_in * B
    approx_flops = 0.0

    for i, (r0, r1) in enumerate(row_segs):
        W_block = W[r0:r1, :]
        for j, (c0, c1) in enumerate(col_segs):
            X_block = X[:, c0:c1]
            key = f"({i},{j})"

            # Local coherence estimate (simple: product of W and X coherence)
            c_local_W = tensor_coherence(W_block, tc_cfg)
            c_local_X = tensor_coherence(X_block, tc_cfg)
            c_local = 0.5 * (c_local_W + c_local_X)

            if c_local >= cfg.tau_high:
                # Low-rank approximation of W_block
                # W_block ≈ U_r diag(s_r) V_r^T, with r <= rank_max
                try:
                    U, s, Vt = np.linalg.svd(W_block, full_matrices=False)
                except np.linalg.LinAlgError:
                    # Fallback to full matmul if SVD fails
                    Y_block = W_block @ X_block
                    Y[r0:r1, c0:c1] = Y_block
                    rank_used[key] = 0
                    approx_flops += 2.0 * W_block.shape[0] * W_block.shape[1] * X_block.shape[1]
                    continue

                r = min(cfg.rank_max, s.shape[0])
                if r <= 0:
                    Y_block = W_block @ X_block
                    rank_used[key] = 0
                    approx_flops += 2.0 * W_block.shape[0] * W_block.shape[1] * X_block.shape[1]
                else:
                    U_r = U[:, :r]
                    s_r = s[:r]
                    Vt_r = Vt[:r, :]

                    # Y_block = U_r diag(s_r) Vt_r @ X_block
                    # Compute in two steps: Z = Vt_r @ X_block, then scale by s_r, then U_r @ Z
                    Z = Vt_r @ X_block  # (r, in_block_cols)
                    # Multiply rows of Z by s_r
                    Z *= s_r[:, None]
                    Y_block = U_r @ Z

                    rank_used[key] = r
                    # Approx FLOPs: U_r@Z (2*m*r*k) + Vt_r@X_block (2*r*n*k)
                    m_block = W_block.shape[0]
                    n_block = W_block.shape[1]
                    k_block = X_block.shape[1]
                    approx_flops += 2.0 * r * (n_block * k_block + m_block * k_block)

                Y[r0:r1, c0:c1] = Y_block

            else:
                # Full matmul
                Y_block = W_block @ X_block
                Y[r0:r1, c0:c1] = Y_block
                rank_used[key] = 0
                approx_flops += 2.0 * W_block.shape[0] * W_block.shape[1] * X_block.shape[1]

    # Coherence out
    c_out = tensor_coherence(Y, tc_cfg)
    delta_c = c_out - c_in

    # Flux metrics
    J_c_in = coherence_flux(c_in, X)
    J_c_out = coherence_flux(c_out, Y)
    div_J_c = J_c_in - J_c_out

    # Residual
    R_c = (delta_c + div_J_c) - cfg.S_c_model

    approx_fraction = 0.0
    if total_flops_full > 0.0:
        approx_fraction = approx_flops / total_flops_full

    receipt: Dict[str, Any] = {
        "op": "CAM",
        "layer_id": layer_id,
        "shapes": {"W": list(W.shape), "X": list(X.shape)},
        "coherence": {
            "c_W": c_W,
            "c_X": c_X,
            "c_in": c_in,
            "c_out": c_out,
            "Delta_c": delta_c,
        },
        "flux": {
            "J_c_in": J_c_in,
            "J_c_out": J_c_out,
            "div_J_c": div_J_c,
        },
        "model": {
            "S_c_model": cfg.S_c_model,
            "policy": {
                "alpha": cfg.alpha,
                "tau_high": cfg.tau_high,
                "tau_mid": cfg.tau_mid,
                "rank_max": cfg.rank_max,
            },
        },
        "residual": {
            "R_c": R_c,
        },
        "approx": {
            "rank_used": rank_used,
            "approx_fraction_flops": approx_fraction,
        },
    }

    return Y, receipt
