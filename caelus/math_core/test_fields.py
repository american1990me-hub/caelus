from __future__ import annotations

import numpy as np
from .fields import Array


def make_swirl_field(n: int) -> Array:
    """Create a simple 2D swirl vector field u = (-y, x, 0) normalized by radius."""
    x = np.linspace(-1.0, 1.0, n)
    y = np.linspace(-1.0, 1.0, n)
    X, Y = np.meshgrid(x, y, indexing="ij")

    ux = -Y
    uy = X
    uz = np.zeros_like(ux)

    r = np.sqrt(X**2 + Y**2) + 1e-9
    ux = ux / r
    uy = uy / r

    return np.stack([ux, uy, uz], axis=-1)


def make_random_field(n: int, seed: int = 0, scale: float = 1.0) -> Array:
    """Random 3-component vector field of shape (n, n, 3)."""
    rng = np.random.default_rng(seed)
    u = rng.standard_normal((n, n, 3))
    return scale * u


def add_galilean_boost(u: Array, vx: float, vy: float, vz: float = 0.0) -> Array:
    """Add a constant velocity vector (vx, vy, vz) to all grid points."""
    boost = np.array([vx, vy, vz], dtype=u.dtype)
    return u + boost

# --- 3D Beltrami test fields (Step 2.5) ---


def make_abc_flow_3d(
    nx: int,
    ny: int,
    nz: int,
    A: float = 1.0,
    B: float = 1.0,
    C: float = 1.0,
) -> Array:
    """Arnold–Beltrami–Childress (ABC) flow on a 3D periodic grid.

    For A = B = C = 1, this satisfies curl(u) = u in the continuum, i.e.
    an exact Beltrami field on [0, 2π]^3.
    """
    x = np.linspace(0.0, 2.0 * np.pi, nx, endpoint=False)
    y = np.linspace(0.0, 2.0 * np.pi, ny, endpoint=False)
    z = np.linspace(0.0, 2.0 * np.pi, nz, endpoint=False)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    ux = A * np.sin(Z) + C * np.cos(Y)
    uy = B * np.sin(X) + A * np.cos(Z)
    uz = C * np.sin(Y) + B * np.cos(X)

    return np.stack([ux, uy, uz], axis=-1)


def make_random_field_3d(
    nx: int,
    ny: int,
    nz: int,
    seed: int = 0,
    scale: float = 1.0,
) -> Array:
    """Random 3D vector field of shape (nx, ny, nz, 3)."""
    rng = np.random.default_rng(seed)
    u = rng.standard_normal((nx, ny, nz, 3))
    return scale * u
