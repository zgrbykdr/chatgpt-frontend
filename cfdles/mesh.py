"""Automatic structured hexahedral mesh generation."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .config import SolverConfig


@dataclass
class StructuredMesh:
    nx: int
    ny: int
    nz: int
    x_edges: np.ndarray
    y_edges: np.ndarray
    z_edges: np.ndarray
    xc: np.ndarray
    yc: np.ndarray
    zc: np.ndarray
    dx: np.ndarray
    dy: np.ndarray
    dz: np.ndarray
    vol: np.ndarray
    delta: np.ndarray
    mask_solid: np.ndarray


def _build_axis_edges(n: int, length: float, stretching: dict, axis: str, zones: list[dict]) -> np.ndarray:
    weights = np.ones(n, dtype=float)
    for zone in zones:
        zmin, zmax = zone["min"], zone["max"]
        factor = float(zone.get("factor", 2.0))
        amin = float(zmin[{"x": 0, "y": 1, "z": 2}[axis]])
        amax = float(zmax[{"x": 0, "y": 1, "z": 2}[axis]])
        left = int(np.clip(np.floor(amin / length * n), 0, n - 1))
        right = int(np.clip(np.ceil(amax / length * n), 1, n))
        weights[left:right] /= factor

    if stretching.get("axis") == axis:
        kind = stretching.get("type", "tanh")
        strength = float(stretching.get("strength", 1.8))
        s = (np.arange(n) + 0.5) / n
        if kind == "tanh":
            prof = 1.0 - 0.6 * np.tanh(strength * (2.0 * np.abs(s - 0.5)))
        else:
            prof = np.exp(-strength * np.abs(s - 0.5))
        weights *= np.clip(prof, 0.08, None)

    widths = weights / np.sum(weights) * length
    edges = np.zeros(n + 1)
    edges[1:] = np.cumsum(widths)
    return edges


def _sphere_mask(cfg: SolverConfig, xc: np.ndarray, yc: np.ndarray, zc: np.ndarray) -> np.ndarray:
    if cfg.domain != "sphere":
        return np.zeros((cfg.mesh.nx, cfg.mesh.ny, cfg.mesh.nz), dtype=float)
    center = cfg.sphere.get("center", [0.4 * cfg.mesh.lengths[0], 0.5 * cfg.mesh.lengths[1], 0.5 * cfg.mesh.lengths[2]])
    radius = float(cfg.sphere.get("radius", 0.1 * min(cfg.mesh.lengths)))
    X, Y, Z = np.meshgrid(xc, yc, zc, indexing="ij")
    r2 = (X - center[0]) ** 2 + (Y - center[1]) ** 2 + (Z - center[2]) ** 2
    return (r2 <= radius**2).astype(float)


def generate_mesh(cfg: SolverConfig) -> StructuredMesh:
    """Generate a nonuniform structured mesh and solid indicator mask."""
    nx, ny, nz = cfg.mesh.nx, cfg.mesh.ny, cfg.mesh.nz
    lx, ly, lz = cfg.mesh.lengths
    zones = cfg.mesh.refinement_zones
    stretch = cfg.mesh.near_wall_stretching

    x_edges = _build_axis_edges(nx, lx, stretch, "x", zones)
    y_edges = _build_axis_edges(ny, ly, stretch, "y", zones)
    z_edges = _build_axis_edges(nz, lz, stretch, "z", zones)

    xc = 0.5 * (x_edges[:-1] + x_edges[1:])
    yc = 0.5 * (y_edges[:-1] + y_edges[1:])
    zc = 0.5 * (z_edges[:-1] + z_edges[1:])
    dx = np.diff(x_edges)
    dy = np.diff(y_edges)
    dz = np.diff(z_edges)

    vol = dx[:, None, None] * dy[None, :, None] * dz[None, None, :]
    delta = np.cbrt(vol)
    mask_solid = _sphere_mask(cfg, xc, yc, zc)

    return StructuredMesh(nx, ny, nz, x_edges, y_edges, z_edges, xc, yc, zc, dx, dy, dz, vol, delta, mask_solid)


def mesh_density_slice(mesh: StructuredMesh, axis: str = "y") -> tuple[np.ndarray, np.ndarray]:
    """Return slice coordinates and reciprocal spacing for quick plotting."""
    if axis == "x":
        return mesh.xc, 1.0 / mesh.dx
    if axis == "z":
        return mesh.zc, 1.0 / mesh.dz
    return mesh.yc, 1.0 / mesh.dy
