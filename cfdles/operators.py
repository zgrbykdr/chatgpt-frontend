"""Discrete differential operators on ghosted cell-centered arrays."""

from __future__ import annotations

import numpy as np

from .mesh import StructuredMesh


Interior = tuple[slice, slice, slice]


def interior_slices() -> Interior:
    return (slice(1, -1), slice(1, -1), slice(1, -1))


def _cell_centers_from_widths(d: np.ndarray) -> np.ndarray:
    return np.cumsum(d) - 0.5 * d


def d_dx(phi: np.ndarray, dx: np.ndarray) -> np.ndarray:
    out = np.zeros_like(phi)
    x = _cell_centers_from_widths(dx)
    out[1:-1, 1:-1, 1:-1] = np.gradient(phi[1:-1, 1:-1, 1:-1], x, axis=0, edge_order=2)
    return out


def d_dy(phi: np.ndarray, dy: np.ndarray) -> np.ndarray:
    out = np.zeros_like(phi)
    y = _cell_centers_from_widths(dy)
    out[1:-1, 1:-1, 1:-1] = np.gradient(phi[1:-1, 1:-1, 1:-1], y, axis=1, edge_order=2)
    return out


def d_dz(phi: np.ndarray, dz: np.ndarray) -> np.ndarray:
    out = np.zeros_like(phi)
    z = _cell_centers_from_widths(dz)
    out[1:-1, 1:-1, 1:-1] = np.gradient(phi[1:-1, 1:-1, 1:-1], z, axis=2, edge_order=2)
    return out


def gradient(phi: np.ndarray, mesh: StructuredMesh) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return d_dx(phi, mesh.dx), d_dy(phi, mesh.dy), d_dz(phi, mesh.dz)


def divergence(u: np.ndarray, v: np.ndarray, w: np.ndarray, mesh: StructuredMesh) -> np.ndarray:
    return d_dx(u, mesh.dx) + d_dy(v, mesh.dy) + d_dz(w, mesh.dz)


def laplacian(phi: np.ndarray, mesh: StructuredMesh) -> np.ndarray:
    out = np.zeros_like(phi)
    x = _cell_centers_from_widths(mesh.dx)
    y = _cell_centers_from_widths(mesh.dy)
    z = _cell_centers_from_widths(mesh.dz)
    core = phi[1:-1, 1:-1, 1:-1]
    d2x = np.gradient(np.gradient(core, x, axis=0, edge_order=2), x, axis=0, edge_order=2)
    d2y = np.gradient(np.gradient(core, y, axis=1, edge_order=2), y, axis=1, edge_order=2)
    d2z = np.gradient(np.gradient(core, z, axis=2, edge_order=2), z, axis=2, edge_order=2)
    out[1:-1, 1:-1, 1:-1] = d2x + d2y + d2z
    return out


def strain_rate(u: np.ndarray, v: np.ndarray, w: np.ndarray, mesh: StructuredMesh) -> tuple[np.ndarray, np.ndarray]:
    dudx, dudy, dudz = gradient(u, mesh)
    dvdx, dvdy, dvdz = gradient(v, mesh)
    dwdx, dwdy, dwdz = gradient(w, mesh)
    s2 = (
        dudx**2 + dvdy**2 + dwdz**2
        + 2.0 * (0.5 * (dudy + dvdx)) ** 2
        + 2.0 * (0.5 * (dudz + dwdx)) ** 2
        + 2.0 * (0.5 * (dvdz + dwdy)) ** 2
    )
    mag_s = np.sqrt(2.0 * s2)
    return mag_s, s2


def vorticity_magnitude(u: np.ndarray, v: np.ndarray, w: np.ndarray, mesh: StructuredMesh) -> np.ndarray:
    _, dudy, dudz = gradient(u, mesh)
    dvdx, _, dvdz = gradient(v, mesh)
    dwdx, dwdy, _ = gradient(w, mesh)
    wx = dwdy - dvdz
    wy = dudz - dwdx
    wz = dvdx - dudy
    return np.sqrt(wx**2 + wy**2 + wz**2)
