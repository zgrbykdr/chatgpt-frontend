from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Fluid:
    name: str
    density: float
    dynamic_viscosity: float
    kinematic_viscosity: float
    thermal_conductivity: float
    specific_heat: float
    prandtl_number: float
    thermal_expansion_coefficient: float
    valid_temperature_min: float
    valid_temperature_max: float
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Fluid":
        return cls(
            name=str(data.get("name", "Air")),
            density=float(data.get("density", 1.2) or 1.2),
            dynamic_viscosity=float(data.get("dynamic_viscosity", 1.8e-5) or 1.8e-5),
            kinematic_viscosity=float(data.get("kinematic_viscosity", 1.5e-5) or 1.5e-5),
            thermal_conductivity=float(data.get("thermal_conductivity", 0.026) or 0.026),
            specific_heat=float(data.get("specific_heat", 1005) or 1005),
            prandtl_number=float(data.get("prandtl_number", 0.71) or 0.71),
            thermal_expansion_coefficient=float(data.get("thermal_expansion_coefficient", 0.0034) or 0.0034),
            valid_temperature_min=float(data.get("valid_temperature_min", -50) or -50),
            valid_temperature_max=float(data.get("valid_temperature_max", 200) or 200),
            notes=str(data.get("notes", "")),
        )


def default_fluids() -> list[Fluid]:
    rows = [
        ("Air",1.184,1.85e-5,1.56e-5,0.0262,1005,0.71,0.00335,-50,200),
        ("Water",997,8.9e-4,8.93e-7,0.607,4182,6.14,0.00021,0,100),
        ("Seawater",1025,1.08e-3,1.05e-6,0.6,3990,7.2,0.00022,-2,100),
        ("Engine Oil",870,0.25,2.87e-4,0.145,2000,3400,0.0007,-20,150),
        ("Hydraulic Oil",860,0.046,5.35e-5,0.13,1900,670,0.0007,-20,120),
        ("Transformer Oil",880,0.012,1.36e-5,0.13,1860,170,0.00075,-20,120),
        ("Ethylene Glycol",1110,0.0161,1.45e-5,0.258,2415,150,0.00065,-20,150),
        ("Propylene Glycol",1036,0.042,4.05e-5,0.21,2500,500,0.0007,-20,150),
        ("Water Ethylene Glycol 50-50",1065,0.0034,3.19e-6,0.38,3350,30,0.00045,-35,120),
        ("Water Propylene Glycol 50-50",1030,0.006,5.83e-6,0.36,3500,55,0.0005,-30,120),
        ("Nitrogen",1.145,1.76e-5,1.54e-5,0.0258,1040,0.71,0.00335,-100,200),
        ("Oxygen",1.331,2.05e-5,1.54e-5,0.0266,918,0.71,0.00335,-100,200),
        ("Carbon Dioxide",1.842,1.48e-5,8.0e-6,0.0166,844,0.75,0.00335,-50,150),
        ("Hydrogen",0.082,8.9e-6,1.09e-4,0.180,14300,0.69,0.00335,-200,200),
        ("Steam",0.598,1.25e-5,2.09e-5,0.025,2010,1.0,0.003,100,300),
        ("Refrigerant R134a",4.25,1.23e-5,2.89e-6,0.014,850,0.75,0.003, -30,80),
        ("Refrigerant R410A",3.9,1.35e-5,3.46e-6,0.013,900,0.8,-0.003,-40,80),
        ("Ammonia",0.73,9.8e-6,1.34e-5,0.025,2060,0.82,0.0034,-40,120),
        ("Silicone Oil",960,0.096,1.0e-4,0.15,1500,960,0.00095,-40,200),
        ("Diesel Fuel",830,0.003,3.61e-6,0.13,2100,48,0.0008,-20,100),
    ]
    return [Fluid(*row, notes="25 C civarı varsayılan özellik") for row in rows]


def ensure_fluids_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump([f.to_dict() for f in default_fluids()], handle, ensure_ascii=False, indent=2)


def load_fluids(path: Path) -> list[Fluid]:
    ensure_fluids_file(path)
    with path.open("r", encoding="utf-8") as handle:
        return [Fluid.from_dict(item) for item in json.load(handle)]


def fluid_by_name(fluids: list[Fluid], name: str) -> Fluid:
    for fluid in fluids:
        if fluid.name == name:
            return fluid
    for fluid in fluids:
        if fluid.name == "Air":
            return fluid
    return Fluid("Air",1.184,1.85e-5,1.56e-5,0.0262,1005,0.71,0.00335,-50,200)
