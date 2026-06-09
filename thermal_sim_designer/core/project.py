from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from core.boundary import BoundaryCondition
from core.fluid import Fluid, ensure_fluids_file, load_fluids
from core.interface import Interface
from core.material import Material, ensure_materials_file, load_materials, material_by_name
from core.part import Part

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MATERIALS_PATH = DATA_DIR / "materials_100.json"
FLUIDS_PATH = DATA_DIR / "fluids_20.json"
DEFAULT_PROJECT_PATH = DATA_DIR / "default_project.json"
COLORS = ["#77aadd", "#ee8866", "#44bb99", "#ffaabb", "#99ddff", "#bbcc33", "#aaaa00"]


@dataclass
class Project:
    project_name: str = "ThermalSim Project"
    units: str = "SI"
    parts: list[Part] = field(default_factory=list)
    materials: list[Material] = field(default_factory=list)
    fluids: list[Fluid] = field(default_factory=list)
    boundaries: list[BoundaryCondition] = field(default_factory=list)
    interfaces: list[Interface] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @classmethod
    def new_project(cls) -> "Project":
        ensure_default_data()
        project = cls(materials=load_materials(MATERIALS_PATH), fluids=load_fluids(FLUIDS_PATH))
        project.add_part()
        return project

    def add_part(self, geometry_type: str = "rectangle") -> Part:
        idx = len(self.parts) + 1
        part = Part(name=f"Part_{idx}", geometry_type=geometry_type, x=0.02 * (idx - 1), color=COLORS[(idx - 1) % len(COLORS)])
        self.parts.append(part)
        self.touch()
        return part

    def delete_part(self, part_id: str) -> bool:
        before = len(self.parts)
        self.parts = [part for part in self.parts if part.id != part_id]
        self.boundaries = [bc for bc in self.boundaries if bc.part_id != part_id]
        self.interfaces = [it for it in self.interfaces if it.part_a_id != part_id and it.part_b_id != part_id]
        self.touch()
        return len(self.parts) != before

    def add_boundary(self, boundary: BoundaryCondition) -> BoundaryCondition:
        self.boundaries.append(boundary)
        part = self.get_part_by_id(boundary.part_id)
        if part and boundary.id not in part.boundaries:
            part.boundaries.append(boundary.id)
        self.touch()
        return boundary

    def add_interface(self, interface: Interface) -> Interface:
        self.interfaces.append(interface)
        for part_id in (interface.part_a_id, interface.part_b_id):
            part = self.get_part_by_id(part_id)
            if part and interface.id not in part.interfaces:
                part.interfaces.append(interface.id)
        self.touch()
        return interface

    def get_part_by_id(self, part_id: str) -> Part | None:
        return next((part for part in self.parts if part.id == part_id), None)

    def touch(self) -> None:
        self.modified_at = datetime.now().isoformat(timespec="seconds")

    def validate_project(self) -> list[str]:
        warnings: list[str] = []
        if not self.parts:
            warnings.append("No parts in project")
        if not self.boundaries:
            warnings.append("No boundary condition")
        if not any(part.heat_power > 0 for part in self.parts) and not any(b.type in {"heat_power", "heat_flux"} for b in self.boundaries):
            warnings.append("No heat source")
        if not any(b.type in {"fixed_temperature", "convection"} for b in self.boundaries):
            warnings.append("No fixed temperature or convection sink")
        for part in self.parts:
            material = material_by_name(self.materials, part.material_name)
            if material.name != part.material_name:
                warnings.append(f"Material missing: {part.name}")
            if part.area() <= 0 or part.thickness <= 0:
                warnings.append(f"Invalid geometry: {part.name}")
            if material.thermal_conductivity <= 0:
                warnings.append(f"Invalid thermal conductivity: {material.name}")
        for boundary in self.boundaries:
            if boundary.type == "convection" and boundary.h_value <= 0:
                warnings.append(f"Invalid h value: {boundary.id}")
        for interface in self.interfaces:
            if interface.type != "adiabatic" and interface.contact_area <= 0:
                warnings.append(f"Invalid contact area: {interface.id}")
        return warnings

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "units": self.units,
            "parts": [p.to_dict() for p in self.parts],
            "materials": [m.to_dict() for m in self.materials],
            "fluids": [f.to_dict() for f in self.fluids],
            "boundaries": [b.to_dict() for b in self.boundaries],
            "interfaces": [i.to_dict() for i in self.interfaces],
            "results": self.results,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        ensure_default_data()
        return cls(
            project_name=str(data.get("project_name", "ThermalSim Project")),
            units=str(data.get("units", "SI")),
            parts=[Part.from_dict(item) for item in data.get("parts", [])],
            materials=[Material.from_dict(item) for item in data.get("materials", [])] or load_materials(MATERIALS_PATH),
            fluids=[Fluid.from_dict(item) for item in data.get("fluids", [])] or load_fluids(FLUIDS_PATH),
            boundaries=[BoundaryCondition.from_dict(item) for item in data.get("boundaries", [])],
            interfaces=[Interface.from_dict(item) for item in data.get("interfaces", [])],
            results=dict(data.get("results", {})),
            created_at=str(data.get("created_at", datetime.now().isoformat(timespec="seconds"))),
            modified_at=str(data.get("modified_at", datetime.now().isoformat(timespec="seconds"))),
        )

    def save_to_file(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.touch()
        with target.open("w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, path: str | Path) -> "Project":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))


def ensure_default_data() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ensure_materials_file(MATERIALS_PATH)
    ensure_fluids_file(FLUIDS_PATH)
    if not DEFAULT_PROJECT_PATH.exists():
        project = Project(materials=load_materials(MATERIALS_PATH), fluids=load_fluids(FLUIDS_PATH))
        project.add_part()
        bc = BoundaryCondition(part_id=project.parts[0].id, type="convection", h_value=10.0, ambient_temperature=25.0)
        project.add_boundary(bc)
        project.save_to_file(DEFAULT_PROJECT_PATH)
