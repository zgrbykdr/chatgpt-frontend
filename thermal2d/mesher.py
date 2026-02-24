from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np

from .models import Material, Project


@dataclass
class MeshResult:
    x: np.ndarray
    y: np.ndarray
    dx: np.ndarray
    dy: np.ndarray
    material_index: np.ndarray
    source: np.ndarray
    material_map: Dict[int, Material]


class StructuredMesher:
    def generate(self, project: Project) -> MeshResult:
        nx, ny = project.mesh.nx, project.mesh.ny
        if project.mesh.nonuniform_x:
            x = np.array(project.mesh.nonuniform_x)
        else:
            x = np.linspace(0.0, project.width, nx + 1)
        if project.mesh.nonuniform_y:
            y = np.array(project.mesh.nonuniform_y)
        else:
            y = np.linspace(0.0, project.height, ny + 1)
        dx = np.diff(x)
        dy = np.diff(y)

        xc = 0.5 * (x[:-1] + x[1:])
        yc = 0.5 * (y[:-1] + y[1:])

        material_ids = list(project.materials.keys())
        mat_id_to_idx = {mid: i for i, mid in enumerate(material_ids)}
        mat_map = {i: project.materials[mid] for mid, i in mat_id_to_idx.items()}

        material_index = np.zeros((ny, nx), dtype=np.int32)
        source = np.zeros((ny, nx), dtype=float)

        rects = sorted(project.rectangles, key=lambda r: r.priority)
        for j, py in enumerate(yc):
            for i, px in enumerate(xc):
                chosen = rects[0]
                for r in rects:
                    if r.contains(px, py):
                        chosen = r
                material_index[j, i] = mat_id_to_idx[chosen.material_id]
                source[j, i] = chosen.heat_source

        return MeshResult(x=x, y=y, dx=dx, dy=dy, material_index=material_index, source=source, material_map=mat_map)
