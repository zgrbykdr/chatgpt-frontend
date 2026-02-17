"""VTK output helpers (legacy rectilinear grid)."""

from __future__ import annotations

from pathlib import Path
import numpy as np

from .mesh import StructuredMesh


def _flatten_cell(a: np.ndarray) -> np.ndarray:
    return np.asarray(a, dtype=float).transpose(2, 1, 0).ravel()


def write_vtk_rectilinear(path: str | Path, mesh: StructuredMesh, fields: dict[str, np.ndarray]) -> None:
    path = Path(path)
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    with path.open("w", encoding="utf-8") as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write("cfdles output\n")
        f.write("ASCII\n")
        f.write("DATASET RECTILINEAR_GRID\n")
        f.write(f"DIMENSIONS {nx+1} {ny+1} {nz+1}\n")
        f.write(f"X_COORDINATES {nx+1} float\n")
        f.write(" ".join(f"{x:.8e}" for x in mesh.x_edges) + "\n")
        f.write(f"Y_COORDINATES {ny+1} float\n")
        f.write(" ".join(f"{y:.8e}" for y in mesh.y_edges) + "\n")
        f.write(f"Z_COORDINATES {nz+1} float\n")
        f.write(" ".join(f"{z:.8e}" for z in mesh.z_edges) + "\n")
        f.write(f"CELL_DATA {nx*ny*nz}\n")

        for name, arr in fields.items():
            data = _flatten_cell(arr)
            f.write(f"SCALARS {name} float 1\n")
            f.write("LOOKUP_TABLE default\n")
            for i in range(0, data.size, 8):
                f.write(" ".join(f"{v:.8e}" for v in data[i : i + 8]) + "\n")
