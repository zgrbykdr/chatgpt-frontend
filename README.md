# MATLAB R2022b CFD Project

This repository contains a full staged CFD workflow in MATLAB R2022b:

1. Configuration loading/validation
2. Geometry processing
3. Meshing
4. Mesh quality analysis and repair
5. Pressure-based incompressible solver
6. Turbulence model integration
7. Postprocessing
8. Workflow orchestration with checkpoints/resume

## Requirements

- MATLAB R2022b
- PDE Toolbox
- (Optional) Parallel Computing Toolbox for optional meshing refinements

## Project Initialization

```matlab
startup
```

## Main Entry

```matlab
result = run_case('examples/channel_flow/case_config.json');
```

## GUI Workbench

Launch the Fluent-like MATLAB GUI control hub:

```matlab
main_gui
```

The GUI provides direct access to configuration, geometry, meshing, quality,
solver, turbulence, orchestration, postprocessing, and self-validation.

### Resume an interrupted run

```matlab
result = run_case('examples/channel_flow/case_config.json', struct('resume', true));
```

## Self Validation

Run built-in self validation (geometry/mesh/solver/turbulence):

```matlab
report = self_validate();
disp(report)
```

## Example Cases

- `examples/channel_flow/case_config.json`
- `examples/backward_facing_step/case_config.json`
- `examples/cylinder_flow/case_config.json`

Run any case:

```matlab
result = run_case('examples/backward_facing_step/case_config.json');
```

## Execution Order (Orchestrator)

`run_case()` executes the following stages via `cfd.app.WorkflowController`:

1. `load_config`
2. `geometry`
3. `meshing`
4. `mesh_quality`
5. `repair_loop`
6. `solver_setup`
7. `solve`
8. `postprocess`

Each stage writes logs and checkpoints. Failures generate debug bundles.

## Output Artifacts

- Checkpoint: `checkpoints/latest_checkpoint.mat`
- Log file: `logs/run.log`
- Postprocess CSV/JSON in `outputs/`
- Debug bundles in `debug/`

## Notes

- Default parametric geometry is used automatically when geometry mode is `parametric` or geometry file path is empty.
- Turbulence model is switched by `cfg.turbulence.model` and integrated during solver iterations.
- Mesh quality gates and repair loops run before solve stage.
