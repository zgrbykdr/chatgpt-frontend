"""Diagnostics and lightweight logging."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np

from .mesh import StructuredMesh
from .operators import divergence, vorticity_magnitude


@dataclass
class StepDiagnostics:
    kinetic_energy: float
    div_l2: float
    nu_t_mean: float
    cfl: float
    pressure_residual: float


def compute_diagnostics(
    u: np.ndarray,
    v: np.ndarray,
    w: np.ndarray,
    nu_t: np.ndarray,
    mesh: StructuredMesh,
    dt: float,
    pressure_residual: float,
) -> StepDiagnostics:
    ui, vi, wi = u[1:-1, 1:-1, 1:-1], v[1:-1, 1:-1, 1:-1], w[1:-1, 1:-1, 1:-1]
    ke = 0.5 * np.sum((ui**2 + vi**2 + wi**2) * mesh.vol) / np.sum(mesh.vol)
    div = divergence(u, v, w, mesh)[1:-1, 1:-1, 1:-1]
    div_l2 = float(np.sqrt(np.mean(div**2)))
    speed = np.sqrt(ui**2 + vi**2 + wi**2)
    min_h = min(np.min(mesh.dx), np.min(mesh.dy), np.min(mesh.dz))
    cfl = float(np.max(speed) * dt / max(min_h, 1e-12))
    return StepDiagnostics(float(ke), div_l2, float(np.mean(nu_t)), cfl, pressure_residual)


def append_log(path: Path, step: int, time: float, dt: float, d: StepDiagnostics) -> None:
    if not path.exists():
        path.write_text("step,time,dt,cfl,pressure_residual,kinetic_energy,div_l2,nu_t_mean\n")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{step},{time:.8e},{dt:.8e},{d.cfl:.5f},{d.pressure_residual:.5e},{d.kinetic_energy:.8e},{d.div_l2:.8e},{d.nu_t_mean:.8e}\n")


def vorticity_slice(u: np.ndarray, v: np.ndarray, w: np.ndarray, mesh: StructuredMesh, k: int | None = None) -> np.ndarray:
    om = vorticity_magnitude(u, v, w, mesh)[1:-1, 1:-1, 1:-1]
    kk = om.shape[2] // 2 if k is None else k
    return om[:, :, kk]
