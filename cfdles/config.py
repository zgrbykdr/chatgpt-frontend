"""Configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass
class LESConfig:
    cs: float = 0.17
    wall_damping: bool = False
    van_driest_a_plus: float = 26.0


@dataclass
class TimeConfig:
    cfl_target: float = 0.5
    dt: float | None = None
    t_end: float = 2.0
    max_steps: int = 2000


@dataclass
class OutputConfig:
    interval: int = 20
    directory: str = "outputs"
    prefix: str = "sol"


@dataclass
class MeshConfig:
    nx: int = 32
    ny: int = 32
    nz: int = 32
    lengths: tuple[float, float, float] = (1.0, 1.0, 1.0)
    near_wall_stretching: dict[str, Any] = field(default_factory=dict)
    refinement_zones: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SolverConfig:
    domain: str = "cavity"
    rho: float = 1.0
    nu: float = 0.01
    body_force: tuple[float, float, float] = (0.0, 0.0, 0.0)
    mesh: MeshConfig = field(default_factory=MeshConfig)
    time: TimeConfig = field(default_factory=TimeConfig)
    les: LESConfig = field(default_factory=LESConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    convection_scheme: str = "central"
    central_blend: float = 0.1
    pressure_tol: float = 1e-6
    pressure_max_iter: int = 400
    pressure_solver: str = "cg"
    pressure_reference: tuple[int, int, int] = (1, 1, 1)
    bcs: dict[str, Any] = field(default_factory=dict)
    sphere: dict[str, Any] = field(default_factory=dict)


def _tuple3(values: Any, key: str) -> tuple[float, float, float]:
    if not isinstance(values, (list, tuple)) or len(values) != 3:
        raise ValueError(f"{key} must be a list/tuple of length 3")
    return (float(values[0]), float(values[1]), float(values[2]))


def load_config(path: str | Path) -> SolverConfig:
    """Load JSON config into SolverConfig with friendly errors."""
    raw = json.loads(Path(path).read_text())
    cfg = SolverConfig()
    cfg.domain = str(raw.get("domain", cfg.domain)).lower()
    cfg.rho = float(raw.get("rho", cfg.rho))
    cfg.nu = float(raw.get("nu", cfg.nu))
    cfg.body_force = _tuple3(raw.get("body_force", cfg.body_force), "body_force")

    mesh_raw = raw.get("mesh", {})
    cfg.mesh = MeshConfig(
        nx=int(mesh_raw.get("nx", cfg.mesh.nx)),
        ny=int(mesh_raw.get("ny", cfg.mesh.ny)),
        nz=int(mesh_raw.get("nz", cfg.mesh.nz)),
        lengths=_tuple3(mesh_raw.get("lengths", cfg.mesh.lengths), "mesh.lengths"),
        near_wall_stretching=mesh_raw.get("near_wall_stretching", {}),
        refinement_zones=mesh_raw.get("refinement_zones", []),
    )

    time_raw = raw.get("time", {})
    cfg.time = TimeConfig(
        cfl_target=float(time_raw.get("cfl_target", cfg.time.cfl_target)),
        dt=time_raw.get("dt", cfg.time.dt),
        t_end=float(time_raw.get("t_end", cfg.time.t_end)),
        max_steps=int(time_raw.get("max_steps", cfg.time.max_steps)),
    )
    if cfg.time.dt is not None:
        cfg.time.dt = float(cfg.time.dt)

    les_raw = raw.get("les", {})
    cfg.les = LESConfig(
        cs=float(les_raw.get("cs", cfg.les.cs)),
        wall_damping=bool(les_raw.get("wall_damping", cfg.les.wall_damping)),
        van_driest_a_plus=float(les_raw.get("van_driest_a_plus", cfg.les.van_driest_a_plus)),
    )

    out_raw = raw.get("output", {})
    cfg.output = OutputConfig(
        interval=int(out_raw.get("interval", cfg.output.interval)),
        directory=str(out_raw.get("directory", cfg.output.directory)),
        prefix=str(out_raw.get("prefix", cfg.output.prefix)),
    )

    cfg.convection_scheme = str(raw.get("convection_scheme", cfg.convection_scheme)).lower()
    cfg.central_blend = float(raw.get("central_blend", cfg.central_blend))
    cfg.pressure_tol = float(raw.get("pressure_tol", cfg.pressure_tol))
    cfg.pressure_max_iter = int(raw.get("pressure_max_iter", cfg.pressure_max_iter))
    cfg.pressure_solver = str(raw.get("pressure_solver", cfg.pressure_solver)).lower()
    cfg.pressure_reference = tuple(raw.get("pressure_reference", cfg.pressure_reference))
    cfg.bcs = raw.get("bcs", {})
    cfg.sphere = raw.get("sphere", {})

    if cfg.mesh.nx < 4 or cfg.mesh.ny < 4 or cfg.mesh.nz < 4:
        raise ValueError("nx, ny, nz must each be >= 4")
    if cfg.nu <= 0.0:
        raise ValueError("nu must be > 0")
    if cfg.time.cfl_target <= 0.0:
        raise ValueError("time.cfl_target must be > 0")
    return cfg
