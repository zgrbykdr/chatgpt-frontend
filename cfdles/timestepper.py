"""Projection timestepper for incompressible LES."""

from __future__ import annotations

from pathlib import Path
import numpy as np

from .bc import apply_pressure_bcs, apply_velocity_bcs
from .config import SolverConfig
from .diagnostics import append_log, compute_diagnostics
from .io_vtk import write_vtk_rectilinear
from .mesh import StructuredMesh, generate_mesh
from .operators import divergence, gradient, laplacian
from .pressure import solve_pressure
from .sgs import smagorinsky_lilly


def _alloc_field(mesh: StructuredMesh) -> np.ndarray:
    return np.zeros((mesh.nx + 2, mesh.ny + 2, mesh.nz + 2), dtype=float)


def _advective_term(phi: np.ndarray, u: np.ndarray, v: np.ndarray, w: np.ndarray, mesh: StructuredMesh, scheme: str, blend: float) -> np.ndarray:
    gx, gy, gz = gradient(phi, mesh)
    central = u * gx + v * gy + w * gz
    if scheme == "upwind":
        out = np.zeros_like(phi)
        dx = mesh.dx[:, None, None]
        dy = mesh.dy[None, :, None]
        dz = mesh.dz[None, None, :]
        dxb = (phi[1:-1, 1:-1, 1:-1] - phi[:-2, 1:-1, 1:-1]) / dx
        dxf = (phi[2:, 1:-1, 1:-1] - phi[1:-1, 1:-1, 1:-1]) / dx
        dyb = (phi[1:-1, 1:-1, 1:-1] - phi[1:-1, :-2, 1:-1]) / dy
        dyf = (phi[1:-1, 2:, 1:-1] - phi[1:-1, 1:-1, 1:-1]) / dy
        dzb = (phi[1:-1, 1:-1, 1:-1] - phi[1:-1, 1:-1, :-2]) / dz
        dzf = (phi[1:-1, 1:-1, 2:] - phi[1:-1, 1:-1, 1:-1]) / dz
        out[1:-1, 1:-1, 1:-1] = (
            np.where(u[1:-1, 1:-1, 1:-1] >= 0.0, u[1:-1, 1:-1, 1:-1] * dxb, u[1:-1, 1:-1, 1:-1] * dxf)
            + np.where(v[1:-1, 1:-1, 1:-1] >= 0.0, v[1:-1, 1:-1, 1:-1] * dyb, v[1:-1, 1:-1, 1:-1] * dyf)
            + np.where(w[1:-1, 1:-1, 1:-1] >= 0.0, w[1:-1, 1:-1, 1:-1] * dzb, w[1:-1, 1:-1, 1:-1] * dzf)
        )
        return out
    return (1.0 - blend) * central + blend * 0.5 * np.sign(central) * np.abs(central)


def _effective_laplacian(phi: np.ndarray, nu_eff: np.ndarray, mesh: StructuredMesh) -> np.ndarray:
    return nu_eff * laplacian(phi, mesh)


def _compute_dt(cfg: SolverConfig, mesh: StructuredMesh, u: np.ndarray, v: np.ndarray, w: np.ndarray, nu_eff_max: float) -> float:
    if cfg.time.dt is not None:
        return cfg.time.dt
    ui, vi, wi = u[1:-1, 1:-1, 1:-1], v[1:-1, 1:-1, 1:-1], w[1:-1, 1:-1, 1:-1]
    speed_max = np.max(np.sqrt(ui**2 + vi**2 + wi**2)) + 1e-8
    hmin = min(np.min(mesh.dx), np.min(mesh.dy), np.min(mesh.dz))
    dt_cfl = cfg.time.cfl_target * hmin / speed_max
    dt_diff = 0.25 * hmin**2 / max(nu_eff_max, 1e-10)
    return float(min(dt_cfl, dt_diff))


def _add_brinkman_penalization(rhs: np.ndarray, phi: np.ndarray, mesh: StructuredMesh, cfg: SolverConfig) -> None:
    if cfg.domain != "sphere":
        return
    eta = float(cfg.sphere.get("eta", 5e-4))
    rhs[1:-1, 1:-1, 1:-1] += -(mesh.mask_solid / eta) * phi[1:-1, 1:-1, 1:-1]


def run_simulation(cfg: SolverConfig) -> None:
    """Run full LES simulation from config."""
    mesh = generate_mesh(cfg)
    out_dir = Path(cfg.output.directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / f"{cfg.output.prefix}_log.csv"

    u, v, w, p = (_alloc_field(mesh) for _ in range(4))
    apply_velocity_bcs(u, v, w, cfg)
    apply_pressure_bcs(p, cfg)

    t = 0.0
    for step in range(1, cfg.time.max_steps + 1):
        nu_t, mag_s = smagorinsky_lilly(u, v, w, mesh, cfg)
        nu_eff = cfg.nu + nu_t
        dt = _compute_dt(cfg, mesh, u, v, w, float(np.max(nu_eff)))
        if t + dt > cfg.time.t_end:
            dt = cfg.time.t_end - t

        adv_u = _advective_term(u, u, v, w, mesh, cfg.convection_scheme, cfg.central_blend)
        adv_v = _advective_term(v, u, v, w, mesh, cfg.convection_scheme, cfg.central_blend)
        adv_w = _advective_term(w, u, v, w, mesh, cfg.convection_scheme, cfg.central_blend)

        u_star, v_star, w_star = u.copy(), v.copy(), w.copy()
        lap_u = _effective_laplacian(u, cfg.nu + nu_t.mean(), mesh)
        lap_v = _effective_laplacian(v, cfg.nu + nu_t.mean(), mesh)
        lap_w = _effective_laplacian(w, cfg.nu + nu_t.mean(), mesh)

        fx, fy, fz = cfg.body_force
        u_star[1:-1, 1:-1, 1:-1] += dt * (-adv_u[1:-1, 1:-1, 1:-1] + lap_u[1:-1, 1:-1, 1:-1] + fx)
        v_star[1:-1, 1:-1, 1:-1] += dt * (-adv_v[1:-1, 1:-1, 1:-1] + lap_v[1:-1, 1:-1, 1:-1] + fy)
        w_star[1:-1, 1:-1, 1:-1] += dt * (-adv_w[1:-1, 1:-1, 1:-1] + lap_w[1:-1, 1:-1, 1:-1] + fz)

        _add_brinkman_penalization(u_star, u, mesh, cfg)
        _add_brinkman_penalization(v_star, v, mesh, cfg)
        _add_brinkman_penalization(w_star, w, mesh, cfg)

        apply_velocity_bcs(u_star, v_star, w_star, cfg)

        div_star = divergence(u_star, v_star, w_star, mesh)[1:-1, 1:-1, 1:-1]
        rhs = (cfg.rho / max(dt, 1e-12)) * div_star
        p, pres_res, _ = solve_pressure(p, rhs, mesh, cfg)
        dpx, dpy, dpz = gradient(p, mesh)

        u[1:-1, 1:-1, 1:-1] = u_star[1:-1, 1:-1, 1:-1] - dt / cfg.rho * dpx[1:-1, 1:-1, 1:-1]
        v[1:-1, 1:-1, 1:-1] = v_star[1:-1, 1:-1, 1:-1] - dt / cfg.rho * dpy[1:-1, 1:-1, 1:-1]
        w[1:-1, 1:-1, 1:-1] = w_star[1:-1, 1:-1, 1:-1] - dt / cfg.rho * dpz[1:-1, 1:-1, 1:-1]
        apply_velocity_bcs(u, v, w, cfg)
        apply_pressure_bcs(p, cfg)

        t += dt
        diag = compute_diagnostics(u, v, w, nu_t, mesh, dt, pres_res)
        append_log(log_path, step, t, dt, diag)

        if step % cfg.output.interval == 0 or t >= cfg.time.t_end or step == 1:
            div = divergence(u, v, w, mesh)[1:-1, 1:-1, 1:-1]
            write_vtk_rectilinear(
                out_dir / f"{cfg.output.prefix}_{step:05d}.vtk",
                mesh,
                {
                    "u": u[1:-1, 1:-1, 1:-1],
                    "v": v[1:-1, 1:-1, 1:-1],
                    "w": w[1:-1, 1:-1, 1:-1],
                    "p": p[1:-1, 1:-1, 1:-1],
                    "nu_t": nu_t,
                    "S_mag": mag_s,
                    "divergence": div,
                },
            )

        if t >= cfg.time.t_end or dt <= 1e-12:
            break
