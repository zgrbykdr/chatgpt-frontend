from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Material:
    name: str
    category: str
    thermal_conductivity: float
    density: float
    specific_heat: float
    emissivity: float
    melting_point: float | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Material":
        return cls(
            name=str(data.get("name", "Aluminum 6061")),
            category=str(data.get("category", "Metals")),
            thermal_conductivity=float(data.get("thermal_conductivity", 167.0) or 167.0),
            density=float(data.get("density", 2700.0) or 2700.0),
            specific_heat=float(data.get("specific_heat", 896.0) or 896.0),
            emissivity=float(data.get("emissivity", 0.1) or 0.1),
            melting_point=data.get("melting_point"),
            notes=str(data.get("notes", "")),
        )


def default_materials() -> list[Material]:
    raw = [
        ("Aluminum 1050","Aluminum Alloys",229,2705,900,0.09),("Aluminum 2024","Aluminum Alloys",121,2780,875,0.09),("Aluminum 3003","Aluminum Alloys",193,2730,893,0.09),("Aluminum 5052","Aluminum Alloys",138,2680,880,0.09),("Aluminum 6061","Aluminum Alloys",167,2700,896,0.09),("Aluminum 6063","Aluminum Alloys",201,2700,900,0.09),("Aluminum 7075","Aluminum Alloys",130,2810,960,0.09),
        ("Pure Copper","Copper Alloys",401,8960,385,0.03),("Copper C110","Copper Alloys",391,8940,385,0.03),("Brass","Copper Alloys",109,8500,380,0.2),("Bronze","Copper Alloys",60,8800,380,0.2),("Beryllium Copper","Copper Alloys",105,8250,420,0.15),
        ("Carbon Steel","Steels",54,7850,486,0.8),("Mild Steel","Steels",51,7850,486,0.8),("AISI 1010 Steel","Steels",63,7870,448,0.8),("AISI 1020 Steel","Steels",52,7870,486,0.8),("AISI 1045 Steel","Steels",49,7850,486,0.8),("Cast Iron","Steels",52,7200,460,0.64),("Ductile Iron","Steels",36,7100,460,0.64),
        ("Stainless Steel 304","Stainless Steels",16.2,8000,500,0.85),("Stainless Steel 316","Stainless Steels",16.3,8000,500,0.85),("Stainless Steel 321","Stainless Steels",16.1,8020,500,0.85),("Stainless Steel 430","Stainless Steels",26,7750,460,0.85),("Tool Steel","Steels",27,7700,460,0.8),
        ("Titanium Grade 2","Titanium Alloys",16.4,4510,520,0.35),("Titanium Grade 5","Titanium Alloys",6.7,4430,560,0.35),("Inconel 600","Nickel Alloys",14.9,8470,444,0.88),("Inconel 625","Nickel Alloys",9.8,8440,410,0.88),("Inconel 718","Nickel Alloys",11.4,8190,435,0.88),("Nickel 200","Nickel Alloys",70,8890,440,0.31),("Monel 400","Nickel Alloys",22,8830,427,0.35),
        ("Zinc","Metals",116,7140,388,0.05),("Tin","Metals",67,7310,227,0.05),("Lead","Metals",35,11340,129,0.28),("Magnesium AZ31","Metals",96,1770,1040,0.07),("Silver","Metals",429,10490,235,0.02),("Gold","Metals",317,19300,129,0.02),("Platinum","Metals",72,21450,133,0.1),("Tungsten","Metals",174,19300,134,0.35),("Molybdenum","Metals",138,10220,251,0.25),
        ("Graphite","Electronics Materials",120,1800,710,0.8),("Silicon","Electronics Materials",148,2330,700,0.65),("Silicon Carbide","Ceramics",120,3210,750,0.85),("Alumina","Ceramics",30,3900,880,0.85),("Aluminum Nitride","Ceramics",170,3260,740,0.8),("Boron Nitride","Ceramics",60,2100,800,0.8),("Zirconia","Ceramics",2.2,5680,480,0.85),("Glass","Ceramics",1.05,2500,840,0.9),("Quartz","Ceramics",1.4,2650,730,0.9),("Soda Lime Glass","Ceramics",0.96,2500,840,0.9),
        ("FR4 PCB","Electronics Materials",0.3,1850,1100,0.9),("Polyimide","Polymers",0.12,1420,1090,0.85),("Kapton","Polymers",0.12,1420,1090,0.85),("Epoxy","Polymers",0.2,1200,1000,0.9),("Silicone Rubber","Rubbers",0.2,1100,1460,0.9),("Natural Rubber","Rubbers",0.13,930,1880,0.9),("Nitrile Rubber","Rubbers",0.25,1000,1500,0.9),("Neoprene","Rubbers",0.19,1230,1500,0.9),
        ("PTFE","Polymers",0.25,2200,1000,0.92),("PEEK","Polymers",0.25,1320,1340,0.9),("Nylon","Polymers",0.25,1150,1700,0.9),("Polycarbonate","Polymers",0.2,1200,1200,0.9),("ABS","Polymers",0.18,1040,1300,0.9),("PVC","Polymers",0.19,1400,900,0.9),("Polyethylene","Polymers",0.42,950,1900,0.9),("Polypropylene","Polymers",0.22,900,1800,0.9),("PMMA","Polymers",0.19,1180,1470,0.9),("PET","Polymers",0.24,1380,1200,0.9),("Acetal POM","Polymers",0.31,1410,1470,0.9),("Polyurethane","Polymers",0.03,60,1400,0.9),
        ("Thermal Grease","Thermal Interface Materials",4,2500,1000,0.9),("Thermal Pad 1 W/mK","Thermal Interface Materials",1,2200,1000,0.9),("Thermal Pad 3 W/mK","Thermal Interface Materials",3,2300,1000,0.9),("Thermal Pad 5 W/mK","Thermal Interface Materials",5,2400,1000,0.9),("Thermal Adhesive","Thermal Interface Materials",1.5,1800,1000,0.9),("Solder SAC305","Electronics Materials",58,7400,220,0.3),("Lead Tin Solder","Electronics Materials",50,8400,150,0.3),("Silicon Die","Electronics Materials",130,2330,700,0.65),("Copper Trace","Electronics Materials",385,8960,385,0.03),("PCB Core Material","Electronics Materials",0.35,1850,1100,0.9),("Ceramic Substrate","Electronics Materials",24,3900,880,0.85),("DBC Substrate","Electronics Materials",180,3300,750,0.8),("Alumina Substrate","Electronics Materials",30,3900,880,0.85),("Aluminum Nitride Substrate","Electronics Materials",170,3260,740,0.8),
        ("Mica","Insulation Materials",0.7,2800,800,0.75),("Mineral Wool","Insulation Materials",0.04,100,840,0.9),("Glass Wool","Insulation Materials",0.04,24,800,0.9),("Rock Wool","Insulation Materials",0.045,80,840,0.9),("Aerogel","Insulation Materials",0.015,150,1000,0.9),("Calcium Silicate","Insulation Materials",0.06,250,1000,0.9),("Foam Insulation","Insulation Materials",0.03,35,1400,0.9),
        ("Wood","Construction Materials",0.12,600,1700,0.9),("Concrete","Construction Materials",1.4,2300,880,0.9),("Brick","Construction Materials",0.72,1800,840,0.9),("Asphalt","Construction Materials",0.75,2300,920,0.95),("Dry Soil","Construction Materials",0.25,1600,800,0.95),("Wet Soil","Construction Materials",1.5,1800,1200,0.95),("Ice","Construction Materials",2.2,917,2100,0.97),("Water Ice","Construction Materials",2.2,917,2100,0.97),("Air Gap Equivalent","Insulation Materials",0.026,1.2,1005,0.0),
        ("Carbon Fiber Composite","Composite Materials",8,1600,800,0.85),("G10 Composite","Composite Materials",0.3,1900,1000,0.9)
    ]
    return [Material(*item, notes="Varsayılan mühendislik veri tabanı değeri") for item in raw[:100]]


def load_materials(path: Path) -> list[Material]:
    ensure_materials_file(path)
    with path.open("r", encoding="utf-8") as handle:
        return [Material.from_dict(item) for item in json.load(handle)]


def ensure_materials_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump([m.to_dict() for m in default_materials()], handle, ensure_ascii=False, indent=2)


def material_by_name(materials: list[Material], name: str) -> Material:
    for material in materials:
        if material.name == name:
            return material
    for material in materials:
        if material.name == "Aluminum 6061":
            return material
    return Material("Aluminum 6061", "Aluminum Alloys", 167.0, 2700.0, 896.0, 0.09)
