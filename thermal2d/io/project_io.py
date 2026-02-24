from __future__ import annotations

import json
from pathlib import Path

from thermal2d.models import (
    BoundaryCondition,
    Material,
    MeshSettings,
    PhaseChange,
    Probe,
    Project,
    PropertyCurve,
    RectangleRegion,
    Schedule,
    SolverSettings,
)


def load_project(path: str | Path) -> Project:
    data = json.loads(Path(path).read_text())
    mats = {}
    for m in data["materials"]:
        phase = m.get("phase_change")
        mats[m["id"]] = Material(
            id=m["id"],
            name=m["name"],
            conductivity=PropertyCurve(m["conductivity"]),
            heat_capacity=PropertyCurve(m["heat_capacity"]),
            density=m["density"],
            phase_change=PhaseChange(**phase) if phase else None,
        )
    project = Project(
        name=data["name"],
        width=data["width"],
        height=data["height"],
        materials=mats,
        rectangles=[RectangleRegion(**r) for r in data["rectangles"]],
        boundaries=[
            BoundaryCondition(
                side=b["side"],
                type=b["type"],
                schedule=Schedule(**b["schedule"]),
                h=b.get("h", 0.0),
                resistance=b.get("resistance", 0.0),
            )
            for b in data["boundaries"]
        ],
        probes=[Probe(**p) for p in data.get("probes", [])],
        mesh=MeshSettings(**data["mesh"]),
        solver=SolverSettings(**data["solver"]),
        initial_temperature=data.get("initial_temperature", 20.0),
    )
    return project


def save_project(project: Project, path: str | Path) -> None:
    payload = {
        "name": project.name,
        "width": project.width,
        "height": project.height,
        "initial_temperature": project.initial_temperature,
        "materials": [
            {
                "id": m.id,
                "name": m.name,
                "conductivity": m.conductivity.points,
                "heat_capacity": m.heat_capacity.points,
                "density": m.density,
                "phase_change": (
                    {
                        "latent_heat": m.phase_change.latent_heat,
                        "t_solidus": m.phase_change.t_solidus,
                        "t_liquidus": m.phase_change.t_liquidus,
                    }
                    if m.phase_change
                    else None
                ),
            }
            for m in project.materials.values()
        ],
        "rectangles": [r.__dict__ for r in project.rectangles],
        "boundaries": [
            {
                "side": b.side,
                "type": b.type,
                "schedule": b.schedule.__dict__,
                "h": b.h,
                "resistance": b.resistance,
            }
            for b in project.boundaries
        ],
        "probes": [p.__dict__ for p in project.probes],
        "mesh": project.mesh.__dict__,
        "solver": project.solver.__dict__,
    }
    Path(path).write_text(json.dumps(payload, indent=2))
