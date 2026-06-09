from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

INTERFACE_TYPES = {"perfect_contact", "contact_resistance", "thermal_pad", "air_gap", "adiabatic"}


@dataclass
class Interface:
    id: str = field(default_factory=lambda: str(uuid4()))
    part_a_id: str = ""
    face_a: str = "right"
    part_b_id: str = ""
    face_b: str = "left"
    type: str = "perfect_contact"
    contact_area: float = 0.001
    contact_resistance: float = 0.1
    thickness: float = 0.001
    material_name: str = "Thermal Pad 3 W/mK"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Interface":
        obj = cls()
        for key in asdict(obj):
            if key in data:
                setattr(obj, key, data[key])
        obj.type = obj.type if obj.type in INTERFACE_TYPES else "perfect_contact"
        obj.contact_area = float(obj.contact_area or 0.001)
        obj.contact_resistance = float(obj.contact_resistance or 0.1)
        obj.thickness = float(obj.thickness or 0.001)
        return obj
