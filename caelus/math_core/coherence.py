from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .fields import Array
from .operators import grad, curl


@dataclass
class CoherenceContract:
    """Concrete coherence functionals for v1 + spectral Γ upgrade.

    - C[ψ]: Dirichlet energy of the complex field ψ.
    - gamma(u): finite-difference Γ using curl and grad(u).
    - gamma_spectral_2d(u): FFT-based Γ for 2D fields.
    """

    kappa: float = 0.618
    epsilon: float = 1e-4

    def C(self, psi: Array) -> float:
        g_real = grad(psi.real)
        g_imag = grad(psi.imag)
        energy = 0.0
        for g in g_real + g_imag:
            energy += float(np.sum(g**2))
        return energy

    def dC_dpsi_star(self, psi: Array) -> Array:
        g_real = grad(psi.real)
        g_imag = grad(psi.imag)
        lap_real = sum(np.gradient(g)[i] for i, g in enumerate(g_real))
        lap_imag = sum(np.gradient(g)[i] for i, g in enumerate(g_imag))
        return -(lap_real + 1j * lap_imag)

    def gamma(self, u: Array) -> float:
        """Finite-difference Γ based on Beltrami defect."""
        u = np.asarray(u)
        if u.shape[-1] == 2:
            ux, uy = np.moveaxis(u, -1, 0)
            uz = np.zeros_like(ux)
            u = np.stack([ux, uy, uz], axis=-1)

        omega = curl(u)

        u_flat = u.reshape(-1, 3)
        om_flat = omega.reshape(-1, 3)

        num_lam = float(np.sum(om_flat * u_flat))
        den_lam = float(np.sum(u_flat * u_flat)) or 1.0
        lam = num_lam / den_lam

        defect = omega - lam * u
        num = float(np.sum(defect**2))

        grads = []
        for comp in np.moveaxis(u, -1, 0):
            grads.extend(np.gradient(comp))
        den = sum(float(np.sum(g**2)) for g in grads) or 1.0

        gamma = den / (den + num)
        return gamma

    def gamma_spectral_2d(self, u: Array) -> float:
        """Spectral Γ for 2D vector fields using FFT.

        u: shape (nx, ny, 2 or 3). Only x/y components are used.
        Assumes periodic boundaries.
        """
        u = np.asarray(u, float)
        if u.ndim != 3:
            raise ValueError("u must have shape (nx, ny, 2 or 3)")
        nx, ny, comp = u.shape
        if comp not in (2, 3):
            raise ValueError("u must have 2 or 3 components in last axis")

        ux = u[..., 0]
        uy = u[..., 1]

        kx = np.fft.fftfreq(nx) * 2.0 * np.pi
        ky = np.fft.fftfreq(ny) * 2.0 * np.pi
        kx_grid, ky_grid = np.meshgrid(kx, ky, indexing="ij")

        Ux_hat = np.fft.fftn(ux)
        Uy_hat = np.fft.fftn(uy)

        # Vorticity ω_z = ∂u_x/∂y - ∂u_y/∂x
        dUy_dx_hat = 1j * kx_grid * Uy_hat
        dUx_dy_hat = 1j * ky_grid * Ux_hat
        dUy_dx = np.fft.ifftn(dUy_dx_hat).real
        dUx_dy = np.fft.ifftn(dUx_dy_hat).real
        omega_z = dUx_dy - dUy_dx

        zeros = np.zeros_like(omega_z)
        omega = np.stack([zeros, zeros, omega_z], axis=-1)
        u3 = np.stack([ux, uy, np.zeros_like(ux)], axis=-1)

        u_flat = u3.reshape(-1, 3)
        om_flat = omega.reshape(-1, 3)

        num_lam = float(np.sum(om_flat * u_flat))
        den_lam = float(np.sum(u_flat * u_flat)) or 1.0
        lam = num_lam / den_lam

        defect = omega - lam * u3
        num = float(np.sum(defect**2))

        # Spectral gradients of u
        dUx_dx_hat = 1j * kx_grid * Ux_hat
        dUx_dy_hat = 1j * ky_grid * Ux_hat
        dUy_dx_hat = 1j * kx_grid * Uy_hat
        dUy_dy_hat = 1j * ky_grid * Uy_hat

        dUx_dx = np.fft.ifftn(dUx_dx_hat).real
        dUx_dy = np.fft.ifftn(dUx_dy_hat).real
        dUy_dx = np.fft.ifftn(dUy_dx_hat).real
        dUy_dy = np.fft.ifftn(dUy_dy_hat).real

        den = float(
            np.sum(dUx_dx**2 + dUx_dy**2 + dUy_dx**2 + dUy_dy**2)
        ) or 1.0

        gamma = den / (den + num)
        return gamma

    def gamma_spectral_3d(self, u: Array) -> float:
        """Spectral Γ for 3D vector fields using FFT.

        u: shape (nx, ny, nz, 3), periodic in all three directions.

        For an exact Beltrami field with curl(u) = λ u, this yields Γ ≈ 1.
        """
        u = np.asarray(u, float)
        if u.ndim != 4 or u.shape[-1] != 3:
            raise ValueError("u must have shape (nx, ny, nz, 3)")

        nx, ny, nz, _ = u.shape
        ux = u[..., 0]
        uy = u[..., 1]
        uz = u[..., 2]

        # Wave numbers (periodic domain [0, 2π]) – scaling cancels in the ratio.
        kx = np.fft.fftfreq(nx) * 2.0 * np.pi * nx
        ky = np.fft.fftfreq(ny) * 2.0 * np.pi * ny
        kz = np.fft.fftfreq(nz) * 2.0 * np.pi * nz
        kx_grid, ky_grid, kz_grid = np.meshgrid(kx, ky, kz, indexing="ij")

        # Fourier transforms
        Ux_hat = np.fft.fftn(ux)
        Uy_hat = np.fft.fftn(uy)
        Uz_hat = np.fft.fftn(uz)

        # Spectral derivatives
        dUx_dx_hat = 1j * kx_grid * Ux_hat
        dUx_dy_hat = 1j * ky_grid * Ux_hat
        dUx_dz_hat = 1j * kz_grid * Ux_hat

        dUy_dx_hat = 1j * kx_grid * Uy_hat
        dUy_dy_hat = 1j * ky_grid * Uy_hat
        dUy_dz_hat = 1j * kz_grid * Uy_hat

        dUz_dx_hat = 1j * kx_grid * Uz_hat
        dUz_dy_hat = 1j * ky_grid * Uz_hat
        dUz_dz_hat = 1j * kz_grid * Uz_hat

        dUx_dx = np.fft.ifftn(dUx_dx_hat).real
        dUx_dy = np.fft.ifftn(dUx_dy_hat).real
        dUx_dz = np.fft.ifftn(dUx_dz_hat).real

        dUy_dx = np.fft.ifftn(dUy_dx_hat).real
        dUy_dy = np.fft.ifftn(dUy_dy_hat).real
        dUy_dz = np.fft.ifftn(dUy_dz_hat).real

        dUz_dx = np.fft.ifftn(dUz_dx_hat).real
        dUz_dy = np.fft.ifftn(dUz_dy_hat).real
        dUz_dz = np.fft.ifftn(dUz_dz_hat).real

        # Curl(u) = ∇ × u
        wx = dUz_dy - dUy_dz
        wy = dUx_dz - dUz_dx
        wz = dUy_dx - dUx_dy
        omega = np.stack([wx, wy, wz], axis=-1)

        # Global best-fit λ in ω ≈ λ u
        u_flat = u.reshape(-1, 3)
        om_flat = omega.reshape(-1, 3)

        num_lam = float(np.sum(om_flat * u_flat))
        den_lam = float(np.sum(u_flat * u_flat)) or 1.0
        lam = num_lam / den_lam

        defect = omega - lam * u
        num = float(np.sum(defect**2))

        # Gradient energy denominator: sum of all partial derivatives squared
        den = float(
            np.sum(
                dUx_dx**2
                + dUx_dy**2
                + dUx_dz**2
                + dUy_dx**2
                + dUy_dy**2
                + dUy_dz**2
                + dUz_dx**2
                + dUz_dy**2
                + dUz_dz**2
            )
        ) or 1.0

        gamma = 1.0 - num / den
        if gamma < 0.0:
            gamma = 0.0
        elif gamma > 1.0:
            gamma = 1.0
        return gamma
