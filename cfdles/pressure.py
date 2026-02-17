"""Pressure Poisson solvers (CG and BiCGSTAB) with Jacobi preconditioning."""

from __future__ import annotations

import numpy as np

from .bc import apply_pressure_bcs
from .config import SolverConfig
from .mesh import StructuredMesh
from .operators import laplacian


def _apply_a(phi: np.ndarray, mesh: StructuredMesh, cfg: SolverConfig) -> np.ndarray:
    out = laplacian(phi, mesh)
    out[1:-1, 1:-1, 1:-1] *= (1.0 - mesh.mask_solid)
    apply_pressure_bcs(out, cfg)
    return out


def _diag(mesh: StructuredMesh) -> np.ndarray:
    dx2 = mesh.dx[:, None, None] ** 2
    dy2 = mesh.dy[None, :, None] ** 2
    dz2 = mesh.dz[None, None, :] ** 2
    return -2.0 * (1.0 / dx2 + 1.0 / dy2 + 1.0 / dz2)


def solve_pressure(p: np.ndarray, rhs: np.ndarray, mesh: StructuredMesh, cfg: SolverConfig) -> tuple[np.ndarray, float, int]:
    b = np.zeros_like(p)
    b[1:-1, 1:-1, 1:-1] = rhs
    if set(cfg.bcs.get("periodic", [])) >= {"x", "z"}:
        b[1:-1, 1:-1, 1:-1] -= np.mean(rhs)

    if cfg.pressure_solver == "bicgstab":
        return _bicgstab(p, b, mesh, cfg)
    return _cg(p, b, mesh, cfg)


def _cg(p: np.ndarray, b: np.ndarray, mesh: StructuredMesh, cfg: SolverConfig) -> tuple[np.ndarray, float, int]:
    d = _diag(mesh)
    x = p.copy()
    apply_pressure_bcs(x, cfg)
    r = b - _apply_a(x, mesh, cfg)
    z = np.zeros_like(x)
    z[1:-1, 1:-1, 1:-1] = r[1:-1, 1:-1, 1:-1] / np.where(np.abs(d) > 1e-12, d, -1.0)
    pvec = z.copy()
    rz_old = np.sum(r[1:-1, 1:-1, 1:-1] * z[1:-1, 1:-1, 1:-1])
    bnorm = np.linalg.norm(b[1:-1, 1:-1, 1:-1]) + 1e-30
    res = 1.0
    for it in range(1, cfg.pressure_max_iter + 1):
        ap = _apply_a(pvec, mesh, cfg)
        alpha = rz_old / (np.sum(pvec[1:-1, 1:-1, 1:-1] * ap[1:-1, 1:-1, 1:-1]) + 1e-30)
        x[1:-1, 1:-1, 1:-1] += alpha * pvec[1:-1, 1:-1, 1:-1]
        r[1:-1, 1:-1, 1:-1] -= alpha * ap[1:-1, 1:-1, 1:-1]
        apply_pressure_bcs(x, cfg)
        res = np.linalg.norm(r[1:-1, 1:-1, 1:-1]) / bnorm
        if res < cfg.pressure_tol:
            return x, res, it
        z[1:-1, 1:-1, 1:-1] = r[1:-1, 1:-1, 1:-1] / np.where(np.abs(d) > 1e-12, d, -1.0)
        rz_new = np.sum(r[1:-1, 1:-1, 1:-1] * z[1:-1, 1:-1, 1:-1])
        beta = rz_new / (rz_old + 1e-30)
        pvec[1:-1, 1:-1, 1:-1] = z[1:-1, 1:-1, 1:-1] + beta * pvec[1:-1, 1:-1, 1:-1]
        rz_old = rz_new
    return x, res, cfg.pressure_max_iter


def _bicgstab(p: np.ndarray, b: np.ndarray, mesh: StructuredMesh, cfg: SolverConfig) -> tuple[np.ndarray, float, int]:
    d = _diag(mesh)
    x = p.copy()
    apply_pressure_bcs(x, cfg)
    r = b - _apply_a(x, mesh, cfg)
    r0 = r.copy()
    v = np.zeros_like(r)
    pvec = np.zeros_like(r)
    alpha = omega = rho_old = 1.0
    bnorm = np.linalg.norm(b[1:-1, 1:-1, 1:-1]) + 1e-30
    res = 1.0
    for it in range(1, cfg.pressure_max_iter + 1):
        rho = np.sum(r0[1:-1, 1:-1, 1:-1] * r[1:-1, 1:-1, 1:-1])
        beta = (rho / (rho_old + 1e-30)) * (alpha / (omega + 1e-30))
        pvec[1:-1, 1:-1, 1:-1] = r[1:-1, 1:-1, 1:-1] + beta * (pvec[1:-1, 1:-1, 1:-1] - omega * v[1:-1, 1:-1, 1:-1])
        phat = np.zeros_like(r)
        phat[1:-1, 1:-1, 1:-1] = pvec[1:-1, 1:-1, 1:-1] / np.where(np.abs(d) > 1e-12, d, -1.0)
        v = _apply_a(phat, mesh, cfg)
        alpha = rho / (np.sum(r0[1:-1, 1:-1, 1:-1] * v[1:-1, 1:-1, 1:-1]) + 1e-30)
        s = r.copy()
        s[1:-1, 1:-1, 1:-1] -= alpha * v[1:-1, 1:-1, 1:-1]
        shat = np.zeros_like(r)
        shat[1:-1, 1:-1, 1:-1] = s[1:-1, 1:-1, 1:-1] / np.where(np.abs(d) > 1e-12, d, -1.0)
        t = _apply_a(shat, mesh, cfg)
        omega = np.sum(t[1:-1, 1:-1, 1:-1] * s[1:-1, 1:-1, 1:-1]) / (np.sum(t[1:-1, 1:-1, 1:-1] ** 2) + 1e-30)
        x[1:-1, 1:-1, 1:-1] += alpha * phat[1:-1, 1:-1, 1:-1] + omega * shat[1:-1, 1:-1, 1:-1]
        r = s.copy()
        r[1:-1, 1:-1, 1:-1] -= omega * t[1:-1, 1:-1, 1:-1]
        apply_pressure_bcs(x, cfg)
        res = np.linalg.norm(r[1:-1, 1:-1, 1:-1]) / bnorm
        if res < cfg.pressure_tol:
            return x, res, it
        rho_old = rho
    return x, res, cfg.pressure_max_iter
