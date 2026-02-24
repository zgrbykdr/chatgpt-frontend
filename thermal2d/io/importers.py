from __future__ import annotations

from pathlib import Path
from typing import List

from thermal2d.models import RectangleRegion


def import_svg_rectangles(path: str | Path, default_material: str) -> List[RectangleRegion]:
    from xml.etree import ElementTree as ET

    tree = ET.parse(path)
    root = tree.getroot()
    rects = []
    idx = 0
    for el in root.iter():
        tag = el.tag.lower()
        if tag.endswith("rect"):
            rects.append(
                RectangleRegion(
                    id=f"svg_{idx}",
                    x=float(el.attrib.get("x", 0.0)),
                    y=float(el.attrib.get("y", 0.0)),
                    width=float(el.attrib.get("width", 0.0)),
                    height=float(el.attrib.get("height", 0.0)),
                    material_id=default_material,
                    priority=idx,
                )
            )
            idx += 1
    return rects


def import_dxf_rectangles(path: str | Path, default_material: str) -> List[RectangleRegion]:
    import ezdxf

    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    rects = []
    idx = 0
    for e in msp:
        if e.dxftype() == "LWPOLYLINE" and e.closed:
            points = [(p[0], p[1]) for p in e.get_points()]
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            rects.append(
                RectangleRegion(
                    id=f"dxf_{idx}",
                    x=min(xs),
                    y=min(ys),
                    width=max(xs) - min(xs),
                    height=max(ys) - min(ys),
                    material_id=default_material,
                    priority=idx,
                )
            )
            idx += 1
    return rects
