"""Subgrid scale models."""

from __future__ import annotations

import numpy as np

from .config import SolverConfig
from .mesh import StructuredMesh
from .operators import strain_rate


def _wall_distance(mesh: StructuredMesh, cfg: SolverConfig) -> np.ndarray:
    y = mesh.yc
    ly = cfg.mesh.lengths[1]
    d = np.minimum(y, ly - y)
    return np.maximum(d[None, :, None], 1e-8)


def smagorinsky_lilly(
    u: np.ndarray,
    v: np.ndarray,
    w: np.ndarray,
    mesh: StructuredMesh,
    cfg: SolverConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (nu_t, |S|) using Smagorinsky-Lilly and optional Van Driest damping."""
    mag_s, _ = strain_rate(u, v, w, mesh)
    cs = cfg.les.cs
    nu_t = (cs * mesh.delta) ** 2 * mag_s[1:-1, 1:-1, 1:-1]

    if cfg.les.wall_damping:
        d = _wall_distance(mesh, cfg)
        nu = cfg.nu
        u_tau = max(np.sqrt(nu * np.max(np.abs(u[1:-1, 1:-1, 1:-1])) / max(cfg.mesh.lengths[1], 1e-8)), 1e-6)
        y_plus = d * u_tau / nu
        damp = (1.0 - np.exp(-y_plus / cfg.les.van_driest_a_plus)) ** 2
        nu_t *= damp

    nu_t *= (1.0 - mesh.mask_solid)
    return nu_t, mag_s[1:-1, 1:-1, 1:-1]
