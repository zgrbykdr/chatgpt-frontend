from __future__ import annotations

import numpy as np

from cfdles.config import SolverConfig
from cfdles.mesh import generate_mesh
from cfdles.operators import d_dx, divergence


def test_grad_sin_matches_cos() -> None:
    cfg = SolverConfig()
    cfg.mesh.nx = 32
    cfg.mesh.ny = 8
    cfg.mesh.nz = 8
    cfg.mesh.lengths = (2.0 * np.pi, 1.0, 1.0)
    cfg.bcs = {"periodic": ["x"]}
    mesh = generate_mesh(cfg)

    phi = np.zeros((mesh.nx + 2, mesh.ny + 2, mesh.nz + 2))
    X = mesh.xc[:, None, None]
    phi[1:-1, 1:-1, 1:-1] = np.sin(X)
    phi[0, 1:-1, 1:-1] = phi[-2, 1:-1, 1:-1]
    phi[-1, 1:-1, 1:-1] = phi[1, 1:-1, 1:-1]
    phi[:, 0, :] = phi[:, 1, :]
    phi[:, -1, :] = phi[:, -2, :]
    phi[:, :, 0] = phi[:, :, 1]
    phi[:, :, -1] = phi[:, :, -2]

    num = d_dx(phi, mesh.dx)[1:-1, 1:-1, 1:-1]
    exact = np.cos(X)
    err = np.sqrt(np.mean((num[:, 0, 0] - exact[:, 0, 0]) ** 2))
    assert err < 0.12


def test_divergence_free_field_is_small() -> None:
    cfg = SolverConfig()
    cfg.mesh.nx = 16
    cfg.mesh.ny = 16
    cfg.mesh.nz = 16
    cfg.mesh.lengths = (1.0, 1.0, 1.0)
    cfg.bcs = {"periodic": ["x", "y", "z"]}
    mesh = generate_mesh(cfg)

    u = np.zeros((mesh.nx + 2, mesh.ny + 2, mesh.nz + 2))
    v = np.zeros_like(u)
    w = np.zeros_like(u)

    X, Y, Z = np.meshgrid(mesh.xc, mesh.yc, mesh.zc, indexing="ij")
    u[1:-1, 1:-1, 1:-1] = np.sin(2 * np.pi * Y)
    v[1:-1, 1:-1, 1:-1] = np.sin(2 * np.pi * Z)
    w[1:-1, 1:-1, 1:-1] = np.sin(2 * np.pi * X)

    for arr in (u, v, w):
        arr[0, :, :] = arr[-2, :, :]
        arr[-1, :, :] = arr[1, :, :]
        arr[:, 0, :] = arr[:, -2, :]
        arr[:, -1, :] = arr[:, 1, :]
        arr[:, :, 0] = arr[:, :, -2]
        arr[:, :, -1] = arr[:, :, 1]

    div = divergence(u, v, w, mesh)[1:-1, 1:-1, 1:-1]
    assert np.sqrt(np.mean(div**2)) < 0.35
