from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

BOUNDARY_TYPES = {"adiabatic", "fixed_temperature", "heat_flux", "heat_power", "convection"}
FACES = {"left", "right", "top", "bottom", "front", "back", "all"}


@dataclass
class BoundaryCondition:
    id: str = field(default_factory=lambda: str(uuid4()))
    part_id: str = ""
    face: str = "all"
    type: str = "convection"
    value: float = 0.0
    ambient_temperature: float = 25.0
    fluid_name: str = "Air"
    h_value: float = 10.0
    h_mode: str = "manual"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BoundaryCondition":
        obj = cls()
        for key in asdict(obj):
            if key in data:
                setattr(obj, key, data[key])
        obj.face = obj.face if obj.face in FACES else "all"
        obj.type = obj.type if obj.type in BOUNDARY_TYPES else "adiabatic"
        obj.value = float(obj.value or 0.0)
        obj.ambient_temperature = float(obj.ambient_temperature or 25.0)
        obj.h_value = float(obj.h_value or 0.0)
        return obj
