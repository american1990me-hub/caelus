from __future__ import annotations

import numpy as np
from .fields import Array


def grad(f: Array) -> list[Array]:
    """Computes the gradient of a scalar field f(x, y, ...)."""
    return list(np.gradient(f))


def curl(u: Array) -> Array:
    """
    Computes the curl of a 3D vector field on a 2D grid.
    u: shape (nx, ny, 3)
    """
    if not (u.ndim == 3 and u.shape[-1] == 3):
        raise ValueError("Input array must be a 3D vector field on a 2D grid, shape (nx, ny, 3).")

    ux, uy, uz = u[..., 0], u[..., 1], u[..., 2]

    # Gradient with respect to x (axis 1) and y (axis 0)
    duy_dx = np.gradient(uy, axis=1)
    dux_dy = np.gradient(ux, axis=0)
    duz_dx = np.gradient(uz, axis=1)
    duz_dy = np.gradient(uz, axis=0)

    # No variation in z, so d/dz terms are 0
    curl_x = duz_dy - 0
    curl_y = 0 - duz_dx
    curl_z = dux_dy - duy_dx

    return np.stack([curl_x, curl_y, curl_z], axis=-1)

def laplacian(f: Array) -> Array:
    """Computes the Laplacian of a scalar field."""
    gy, gx = np.gradient(f)
    _, d2f_dx2 = np.gradient(gx)
    d2f_dy2, _ = np.gradient(gy)
    return d2f_dx2 + d2f_dy2
