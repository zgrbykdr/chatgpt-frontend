# CFDLES: 3D Incompressible LES Solver (Python)

Educational, runnable 3D incompressible Navier–Stokes LES solver with:
- Fractional-step / projection method
- Smagorinsky–Lilly SGS (+ Van Driest wall damping option)
- Structured finite-volume-like mesh with nonuniform spacing and auto-mesh refinement weights
- Periodic/wall/inflow/outflow boundary conditions
- Pressure Poisson CG / BiCGSTAB with Jacobi preconditioning
- VTK output for ParaView
- Built-in demos and operator tests

## Install

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e .
```

## One-command default demo run

```bash
python run_demo.py demos/cavity.json
```

This writes VTK + CSV logs to `outputs/cavity/`.

## Other demos

```bash
python run_demo.py demos/channel.json
python run_demo.py demos/sphere.json
```

## Plot diagnostics

```bash
python plot_results.py demos/cavity.json
```

## What gets saved
- `*.vtk` fields: `u, v, w, p, nu_t, S_mag, divergence`
- `*_log.csv`: step, time, dt, CFL, pressure residual, kinetic energy, divergence norm, mean `nu_t`

## Expected qualitative demo behavior
- **Cavity:** top moving lid drives a primary recirculation + 3D corner vortices.
- **Channel:** periodic streamwise/spanwise flow with near-wall shear and turbulent-like fluctuations.
- **Sphere:** wake-like low-speed region behind immersed sphere (Brinkman penalization).

## Tests

```bash
pytest -q
```

## Notes / limitations
- Spatial operators are cell-centered and prioritize clarity over high-order accuracy.
- Diffusion is explicit; dt includes both CFL and diffusion limits.
- Pressure operator is matrix-free and robust for small-medium grids; for large cases, a multigrid preconditioner is recommended.
- SGS extension point: add new model in `cfdles/sgs.py` and switch in `timestepper.py`.
- Implicit diffusion could be added by solving Helmholtz systems for each velocity component.
