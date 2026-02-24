from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple


@dataclass
class PropertyCurve:
    points: List[Tuple[float, float]]

    def eval(self, t: float) -> float:
        pts = sorted(self.points)
        if not pts:
            raise ValueError("Property curve has no points")
        if t <= pts[0][0]:
            return pts[0][1]
        if t >= pts[-1][0]:
            return pts[-1][1]
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            if x0 <= t <= x1:
                if x1 == x0:
                    return y0
                a = (t - x0) / (x1 - x0)
                return y0 + a * (y1 - y0)
        return pts[-1][1]


@dataclass
class PhaseChange:
    latent_heat: float
    t_solidus: float
    t_liquidus: float

    def apparent_cp(self, t: float) -> float:
        if self.t_solidus <= t <= self.t_liquidus and self.t_liquidus > self.t_solidus:
            return self.latent_heat / (self.t_liquidus - self.t_solidus)
        return 0.0


@dataclass
class Material:
    id: str
    name: str
    conductivity: PropertyCurve
    heat_capacity: PropertyCurve
    density: float
    phase_change: Optional[PhaseChange] = None

    def k(self, t: float) -> float:
        return self.conductivity.eval(t)

    def cp(self, t: float) -> float:
        base = self.heat_capacity.eval(t)
        if self.phase_change:
            base += self.phase_change.apparent_cp(t)
        return base

    def volumetric_capacity(self, t: float) -> float:
        return self.cp(t) * self.density


@dataclass
class RectangleRegion:
    id: str
    x: float
    y: float
    width: float
    height: float
    material_id: str
    priority: int = 0
    heat_source: float = 0.0

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height


ScheduleType = Literal["constant", "sinusoidal", "step_constant", "step_linear"]


@dataclass
class Schedule:
    type: ScheduleType
    value: float = 0.0
    amplitude: float = 0.0
    period: float = 86400.0
    offset: float = 0.0
    steps: List[Tuple[float, float]] = field(default_factory=list)

    def eval(self, t: float) -> float:
        import math

        if self.type == "constant":
            return self.value
        if self.type == "sinusoidal":
            return self.offset + self.amplitude * math.sin((2 * math.pi * t) / self.period)
        if not self.steps:
            return self.value
        pts = sorted(self.steps)
        if self.type == "step_constant":
            v = pts[0][1]
            for ts, tv in pts:
                if t >= ts:
                    v = tv
                else:
                    break
            return v
        if self.type == "step_linear":
            if t <= pts[0][0]:
                return pts[0][1]
            if t >= pts[-1][0]:
                return pts[-1][1]
            for (t0, v0), (t1, v1) in zip(pts[:-1], pts[1:]):
                if t0 <= t <= t1:
                    a = (t - t0) / (t1 - t0)
                    return v0 + a * (v1 - v0)
        return self.value


BoundaryType = Literal["fixed_temp", "flux", "convective"]
BoundarySide = Literal["left", "right", "top", "bottom"]


@dataclass
class BoundaryCondition:
    side: BoundarySide
    type: BoundaryType
    schedule: Schedule
    h: float = 0.0
    resistance: float = 0.0


@dataclass
class Probe:
    id: str
    x: float
    y: float


@dataclass
class MeshSettings:
    nx: int
    ny: int
    nonuniform_x: Optional[List[float]] = None
    nonuniform_y: Optional[List[float]] = None


@dataclass
class SolverSettings:
    mode: Literal["steady", "transient"]
    t_end: float = 86400
    dt: Optional[float] = None
    output_interval: float = 3600
    sor_omega: float = 1.7
    sor_tol: float = 1e-6
    sor_max_iter: int = 20000


@dataclass
class Project:
    name: str
    width: float
    height: float
    materials: Dict[str, Material]
    rectangles: List[RectangleRegion]
    boundaries: List[BoundaryCondition]
    probes: List[Probe]
    mesh: MeshSettings
    solver: SolverSettings
    initial_temperature: float = 20.0
