"""Compact NumPy snapshot output for fast post-processing/GUI."""

from __future__ import annotations

from pathlib import Path
import numpy as np

from .mesh import StructuredMesh


def write_snapshot_npz(
    path: str | Path,
    mesh: StructuredMesh,
    u: np.ndarray,
    v: np.ndarray,
    w: np.ndarray,
    p: np.ndarray,
    nu_t: np.ndarray,
    s_mag: np.ndarray,
    divergence: np.ndarray,
    time: float,
    step: int,
) -> None:
    """Write a compressed snapshot with mesh and fields for GUI/postprocessing."""
    np.savez_compressed(
        Path(path),
        x_edges=mesh.x_edges,
        y_edges=mesh.y_edges,
        z_edges=mesh.z_edges,
        xc=mesh.xc,
        yc=mesh.yc,
        zc=mesh.zc,
        u=u,
        v=v,
        w=w,
        p=p,
        nu_t=nu_t,
        s_mag=s_mag,
        divergence=divergence,
        time=float(time),
        step=int(step),
    )
