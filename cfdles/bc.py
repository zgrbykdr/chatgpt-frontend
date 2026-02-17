"""Boundary-condition application for velocity and pressure."""

from __future__ import annotations

import numpy as np

from .config import SolverConfig


def _periodic_copy(phi: np.ndarray, axis: int) -> None:
    if axis == 0:
        phi[0, :, :] = phi[-2, :, :]
        phi[-1, :, :] = phi[1, :, :]
    elif axis == 1:
        phi[:, 0, :] = phi[:, -2, :]
        phi[:, -1, :] = phi[:, 1, :]
    else:
        phi[:, :, 0] = phi[:, :, -2]
        phi[:, :, -1] = phi[:, :, 1]


def apply_velocity_bcs(u: np.ndarray, v: np.ndarray, w: np.ndarray, cfg: SolverConfig) -> None:
    """Apply boundary conditions on ghost cells."""
    bc = cfg.bcs
    periodic = bc.get("periodic", [])
    if "x" in periodic:
        _periodic_copy(u, 0)
        _periodic_copy(v, 0)
        _periodic_copy(w, 0)
    else:
        u[0, :, :] = -u[1, :, :]
        u[-1, :, :] = -u[-2, :, :]
        v[0, :, :] = -v[1, :, :]
        v[-1, :, :] = -v[-2, :, :]
        w[0, :, :] = -w[1, :, :]
        w[-1, :, :] = -w[-2, :, :]

    if "y" in periodic:
        _periodic_copy(u, 1)
        _periodic_copy(v, 1)
        _periodic_copy(w, 1)
    else:
        u[:, 0, :] = -u[:, 1, :]
        v[:, 0, :] = -v[:, 1, :]
        w[:, 0, :] = -w[:, 1, :]
        top_u = float(bc.get("moving_wall", {}).get("u", 0.0))
        u[:, -1, :] = 2.0 * top_u - u[:, -2, :]
        v[:, -1, :] = -v[:, -2, :]
        w[:, -1, :] = -w[:, -2, :]

    if "z" in periodic:
        _periodic_copy(u, 2)
        _periodic_copy(v, 2)
        _periodic_copy(w, 2)
    else:
        inflow = bc.get("inflow", {})
        if inflow.get("at") == "zmin":
            val = inflow.get("velocity", [1.0, 0.0, 0.0])
            u[:, :, 0] = 2.0 * val[0] - u[:, :, 1]
            v[:, :, 0] = 2.0 * val[1] - v[:, :, 1]
            w[:, :, 0] = 2.0 * val[2] - w[:, :, 1]
        else:
            u[:, :, 0] = -u[:, :, 1]
            v[:, :, 0] = -v[:, :, 1]
            w[:, :, 0] = -w[:, :, 1]

        if bc.get("outflow", {}).get("at") == "zmax":
            u[:, :, -1] = u[:, :, -2]
            v[:, :, -1] = v[:, :, -2]
            w[:, :, -1] = w[:, :, -2]
        else:
            u[:, :, -1] = -u[:, :, -2]
            v[:, :, -1] = -v[:, :, -2]
            w[:, :, -1] = -w[:, :, -2]


def apply_pressure_bcs(p: np.ndarray, cfg: SolverConfig) -> None:
    bc = cfg.bcs
    periodic = bc.get("periodic", [])
    if "x" in periodic:
        _periodic_copy(p, 0)
    else:
        p[0, :, :] = p[1, :, :]
        p[-1, :, :] = p[-2, :, :]

    if "y" in periodic:
        _periodic_copy(p, 1)
    else:
        p[:, 0, :] = p[:, 1, :]
        p[:, -1, :] = p[:, -2, :]

    if "z" in periodic:
        _periodic_copy(p, 2)
    else:
        p[:, :, 0] = p[:, :, 1]
        p[:, :, -1] = p[:, :, -2]

    ref = cfg.pressure_reference
    p[ref] = 0.0
