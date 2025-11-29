from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

import numpy as np

from .cam import cam_matmul, CAMConfig

Array = np.ndarray


@dataclass
class DenseLayerParams:
    """Parameters for a single dense layer used by CACEEngine."""

    W: Array
    b: Array | None
    layer_id: str
    activation: str = "relu"  # "relu", "tanh", or "none"


@dataclass
class CACEConfig:
    cam_config: CAMConfig


class CACEEngine:
    """Coherence-Aware Compute Engine using CAM for dense layers.

    This is a simple forward-only engine: given an input batch x, it applies
    a sequence of dense layers, each using cam_matmul, and returns the final
    activations plus a list of per-layer receipts.
    """

    def __init__(self, layers: List[DenseLayerParams], config: CACEConfig | None = None):
        if not layers:
            raise ValueError("CACEEngine requires at least one layer")
        self.layers = layers
        self.config = config or CACEConfig(cam_config=CAMConfig())

    def _apply_activation(self, z: Array, kind: str) -> Array:
        if kind == "relu":
            return np.maximum(z, 0.0)
        if kind == "tanh":
            return np.tanh(z)
        return z  # "none" or unknown

    def forward(self, x: Array) -> tuple[Array, List[Dict[str, Any]]]:
        """Run a forward pass through all layers.

        Args:
            x: input array of shape (B, d_in).

        Returns:
            (y, receipts):
              - y: output array of shape (B, d_out_last).
              - receipts: list of per-layer CAM receipts.
        """
        X = np.asarray(x, dtype=float)
        if X.ndim != 2:
            raise ValueError(f"CACEEngine.forward expects 2D input, got {X.shape}")

        B, d_in = X.shape
        receipts: List[Dict[str, Any]] = []

        for layer in self.layers:
            W = np.asarray(layer.W, dtype=float)
            if W.ndim != 2:
                raise ValueError(f"Layer {layer.layer_id}: W must be 2D, got {W.shape}")
            d_out, d_in_W = W.shape
            if d_in_W != d_in:
                raise ValueError(
                    f"Layer {layer.layer_id}: input dim mismatch: W {W.shape}, X {X.shape}"
                )

            # X: (B, d_in) -> (d_in, B) for CAM
            X_T = X.T
            Y_T, rec = cam_matmul(
                W,
                X_T,
                layer_id=layer.layer_id,
                cfg=self.config.cam_config,
            )

            # Add bias if present
            if layer.b is not None:
                b = np.asarray(layer.b, dtype=float).reshape(-1)
                if b.shape[0] != d_out:
                    raise ValueError(
                        f"Layer {layer.layer_id}: bias dim {b.shape[0]} != d_out {d_out}"
                    )
                Y_T = Y_T + b[:, None]

            # Back to (B, d_out)
            X = Y_T.T
            X = self._apply_activation(X, layer.activation)

            # Update for next layer
            B, d_in = X.shape

            receipts.append(rec)

        return X, receipts
