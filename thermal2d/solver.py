from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from .mesher import MeshResult
from .models import BoundaryCondition, Project


@dataclass
class SolverResult:
    temperature: np.ndarray
    history: List[Tuple[float, np.ndarray]]
    probe_history: Dict[str, List[Tuple[float, float]]]


class HeatSolver:
    def __init__(self, project: Project, mesh: MeshResult):
        self.project = project
        self.mesh = mesh

    def _cell_capacity(self, t: np.ndarray) -> np.ndarray:
        cap = np.zeros_like(t)
        for midx, mat in self.mesh.material_map.items():
            m = self.mesh.material_index == midx
            cap[m] = mat.volumetric_capacity(float(np.mean(t[m])))
        return cap

    def _cell_conductivity(self, t: np.ndarray) -> np.ndarray:
        k = np.zeros_like(t)
        for midx, mat in self.mesh.material_map.items():
            m = self.mesh.material_index == midx
            k[m] = mat.k(float(np.mean(t[m])))
        return k

    def _apply_bc(self, t: np.ndarray, tcur: float) -> None:
        ny, nx = t.shape
        dt = self.project.solver.dt or 1.0
        for bc in self.project.boundaries:
            val = bc.schedule.eval(tcur)
            if bc.side == "left":
                if bc.type == "fixed_temp":
                    t[:, 0] = val
                elif bc.type == "flux":
                    t[:, 0] += val * dt / 10000.0
                elif bc.type == "convective":
                    h_eff = bc.h if bc.h > 0 else (1.0 / max(bc.resistance, 1e-9))
                    t[:, 0] += 0.001 * h_eff * (val - t[:, 0])
            if bc.side == "right":
                if bc.type == "fixed_temp":
                    t[:, nx - 1] = val
                elif bc.type == "flux":
                    t[:, nx - 1] += val * dt / 10000.0
                elif bc.type == "convective":
                    h_eff = bc.h if bc.h > 0 else (1.0 / max(bc.resistance, 1e-9))
                    t[:, nx - 1] += 0.001 * h_eff * (val - t[:, nx - 1])
            if bc.side == "top":
                if bc.type == "fixed_temp":
                    t[0, :] = val
                elif bc.type == "flux":
                    t[0, :] += val * dt / 10000.0
                elif bc.type == "convective":
                    h_eff = bc.h if bc.h > 0 else (1.0 / max(bc.resistance, 1e-9))
                    t[0, :] += 0.001 * h_eff * (val - t[0, :])
            if bc.side == "bottom":
                if bc.type == "fixed_temp":
                    t[ny - 1, :] = val
                elif bc.type == "flux":
                    t[ny - 1, :] += val * dt / 10000.0
                elif bc.type == "convective":
                    h_eff = bc.h if bc.h > 0 else (1.0 / max(bc.resistance, 1e-9))
                    t[ny - 1, :] += 0.001 * h_eff * (val - t[ny - 1, :])

    def stable_dt(self, t: np.ndarray) -> float:
        k = self._cell_conductivity(t)
        c = self._cell_capacity(t)
        dx_min = np.min(self.mesh.dx)
        dy_min = np.min(self.mesh.dy)
        alpha = np.max(k / np.maximum(c, 1e-12))
        return 0.5 / (alpha * ((1 / dx_min**2) + (1 / dy_min**2)) + 1e-12)

    def solve_transient(self) -> SolverResult:
        ny, nx = self.mesh.material_index.shape
        t = np.full((ny, nx), self.project.initial_temperature, dtype=float)
        dt = self.project.solver.dt or self.stable_dt(t) * 0.9
        self.project.solver.dt = dt
        out_dt = self.project.solver.output_interval
        tcur = 0.0
        next_out = 0.0
        history: List[Tuple[float, np.ndarray]] = []
        probe_history: Dict[str, List[Tuple[float, float]]] = {p.id: [] for p in self.project.probes}

        while tcur <= self.project.solver.t_end + 1e-9:
            k = self._cell_conductivity(t)
            c = self._cell_capacity(t)
            t_new = t.copy()
            for j in range(1, ny - 1):
                for i in range(1, nx - 1):
                    ke = 2 * k[j, i] * k[j, i + 1] / (k[j, i] + k[j, i + 1] + 1e-12)
                    kw = 2 * k[j, i] * k[j, i - 1] / (k[j, i] + k[j, i - 1] + 1e-12)
                    kn = 2 * k[j, i] * k[j - 1, i] / (k[j, i] + k[j - 1, i] + 1e-12)
                    ks = 2 * k[j, i] * k[j + 1, i] / (k[j, i] + k[j + 1, i] + 1e-12)
                    dx = self.mesh.dx[i]
                    dy = self.mesh.dy[j]
                    lap = (
                        ke * (t[j, i + 1] - t[j, i]) / dx**2
                        - kw * (t[j, i] - t[j, i - 1]) / dx**2
                        + ks * (t[j + 1, i] - t[j, i]) / dy**2
                        - kn * (t[j, i] - t[j - 1, i]) / dy**2
                    )
                    t_new[j, i] = t[j, i] + dt * (lap + self.mesh.source[j, i]) / max(c[j, i], 1e-9)
            self._apply_bc(t_new, tcur)
            t = t_new
            if tcur >= next_out - 1e-9:
                history.append((tcur, t.copy()))
                for p in self.project.probes:
                    i = min(np.searchsorted(self.mesh.x, p.x) - 1, nx - 1)
                    j = min(np.searchsorted(self.mesh.y, p.y) - 1, ny - 1)
                    i = max(i, 0)
                    j = max(j, 0)
                    probe_history[p.id].append((tcur, float(t[j, i])))
                next_out += out_dt
            tcur += dt
        return SolverResult(temperature=t, history=history, probe_history=probe_history)

    def solve_steady(self) -> SolverResult:
        ny, nx = self.mesh.material_index.shape
        t = np.full((ny, nx), self.project.initial_temperature, dtype=float)
        k = self._cell_conductivity(t)
        omega = self.project.solver.sor_omega
        tol = self.project.solver.sor_tol

        for _ in range(self.project.solver.sor_max_iter):
            max_delta = 0.0
            for j in range(1, ny - 1):
                for i in range(1, nx - 1):
                    ke = 2 * k[j, i] * k[j, i + 1] / (k[j, i] + k[j, i + 1] + 1e-12)
                    kw = 2 * k[j, i] * k[j, i - 1] / (k[j, i] + k[j, i - 1] + 1e-12)
                    kn = 2 * k[j, i] * k[j - 1, i] / (k[j, i] + k[j - 1, i] + 1e-12)
                    ks = 2 * k[j, i] * k[j + 1, i] / (k[j, i] + k[j + 1, i] + 1e-12)
                    denom = ke + kw + kn + ks + 1e-12
                    t_star = (
                        ke * t[j, i + 1]
                        + kw * t[j, i - 1]
                        + kn * t[j - 1, i]
                        + ks * t[j + 1, i]
                        + self.mesh.source[j, i]
                    ) / denom
                    new_t = (1 - omega) * t[j, i] + omega * t_star
                    max_delta = max(max_delta, abs(new_t - t[j, i]))
                    t[j, i] = new_t
            self._apply_bc(t, 0.0)
            if max_delta < tol:
                break
        return SolverResult(temperature=t, history=[(0.0, t.copy())], probe_history={})
