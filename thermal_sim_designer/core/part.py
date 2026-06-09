from __future__ import annotations

from dataclasses import dataclass, field
from math import pi
from typing import Any
from uuid import uuid4


@dataclass
class Part:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Part_1"
    geometry_type: str = "rectangle"
    x: float = 0.0
    y: float = 0.0
    width: float = 0.1
    height: float = 0.05
    radius: float = 0.025
    thickness: float = 0.005
    material_name: str = "Aluminum 6061"
    heat_power: float = 0.0
    initial_temperature: float = 25.0
    temperature_result: float | None = None
    boundaries: list[str] = field(default_factory=list)
    interfaces: list[str] = field(default_factory=list)
    color: str = "#77aadd"
    visible: bool = True

    def area(self) -> float:
        if self.geometry_type == "circle":
            return max(pi * self.radius * self.radius, 0.0)
        return max(self.width * self.height, 0.0)

    def volume(self) -> float:
        return self.area() * max(self.thickness, 0.0)

    def characteristic_length(self) -> float:
        if self.geometry_type == "circle":
            return max(2.0 * self.radius, 1e-12)
        positive = [v for v in (self.width, self.height, self.thickness) if v > 0]
        return min(positive) if positive else 1e-12

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "geometry_type": self.geometry_type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "radius": self.radius,
            "thickness": self.thickness,
            "material_name": self.material_name,
            "heat_power": self.heat_power,
            "initial_temperature": self.initial_temperature,
            "temperature_result": self.temperature_result,
            "boundaries": list(self.boundaries),
            "interfaces": list(self.interfaces),
            "color": self.color,
            "visible": self.visible,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Part":
        safe = cls()
        for key in safe.to_dict():
            if key in data:
                setattr(safe, key, data[key])
        safe.geometry_type = safe.geometry_type if safe.geometry_type in {"rectangle", "circle"} else "rectangle"
        safe.width = float(safe.width or 0.1)
        safe.height = float(safe.height or 0.05)
        safe.radius = float(safe.radius or 0.025)
        safe.thickness = float(safe.thickness or 0.005)
        safe.heat_power = float(safe.heat_power or 0.0)
        safe.initial_temperature = float(safe.initial_temperature or 25.0)
        return safe
