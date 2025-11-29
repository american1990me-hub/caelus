from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List, Dict, Any

import numpy as np

from .engine import DenseLayerParams, CACEConfig, CACEEngine
from .cam import CAMConfig
from .text_embed import embed_text_to_vec

Array = np.ndarray


@dataclass
class CACETextModelConfig:
    embed_dim: int = 32
    hidden_dim: int = 32
    output_dim: int = 16
    seed: int = 0  # controls deterministic weight initialization
    rank_max: int = 8
    tau_high: float = 0.7
    tau_mid: float = 0.3


def build_cace_text_engine(cfg: CACETextModelConfig) -> CACEEngine:
    """Construct a small 2-layer CACEEngine with deterministic weights."""
    rng = np.random.default_rng(cfg.seed)

    W1 = rng.normal(size=(cfg.hidden_dim, cfg.embed_dim))
    b1 = rng.normal(size=(cfg.hidden_dim,))
    W2 = rng.normal(size=(cfg.output_dim, cfg.hidden_dim))
    b2 = rng.normal(size=(cfg.output_dim,))

    layers = [
        DenseLayerParams(W=W1, b=b1, layer_id="cace_text_L1", activation="relu"),
        DenseLayerParams(W=W2, b=b2, layer_id="cace_text_L2", activation="none"),
    ]

    cam_cfg = CAMConfig(
        alpha=0.7,
        tau_high=cfg.tau_high,
        tau_mid=cfg.tau_mid,
        rank_max=cfg.rank_max,
        block_rows=3,
        block_cols=3,
        S_c_model=0.0,
    )
    cace_cfg = CACEConfig(cam_config=cam_cfg)
    return CACEEngine(layers, config=cace_cfg)


@dataclass
class ComputeCoherenceSnapshot:
    """Aggregated compute coherence stats over a CACE forward pass."""

    mean_c_in: float
    mean_c_out: float
    max_abs_R_c: float
    num_layers: int


def run_cace_for_text(
    text: str,
    model_cfg: CACETextModelConfig,
) -> Tuple[Array, List[Dict[str, Any]], ComputeCoherenceSnapshot]:
    """Embed text, run through CACE engine, and summarize coherence.

    Returns:
      y: output embedding (B=1, d_out)
      receipts: list of per-layer CAM receipts
      snapshot: aggregated coherence stats
    """
    engine = build_cace_text_engine(model_cfg)

    v = embed_text_to_vec(text, dim=model_cfg.embed_dim, seed=model_cfg.seed)
    x = v.reshape(1, -1)

    y, receipts = engine.forward(x)

    if not receipts:
        snap = ComputeCoherenceSnapshot(
            mean_c_in=0.0,
            mean_c_out=0.0,
            max_abs_R_c=0.0,
            num_layers=0,
        )
        return y, receipts, snap

    c_in_vals = [r["coherence"]["c_in"] for r in receipts]
    c_out_vals = [r["coherence"]["c_out"] for r in receipts]
    R_vals = [abs(r["residual"]["R_c"]) for r in receipts]

    snap = ComputeCoherenceSnapshot(
        mean_c_in=float(sum(c_in_vals) / len(c_in_vals)),
        mean_c_out=float(sum(c_out_vals) / len(c_out_vals)),
        max_abs_R_c=float(max(R_vals)),
        num_layers=len(receipts),
    )
    return y, receipts, snap
