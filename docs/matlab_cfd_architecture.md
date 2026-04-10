# MATLAB R2022b CFD Platform Architecture (Fluent-Equivalent Scope)

## 1) System Architecture

### 1.1 Architectural Style
A layered, workflow-driven architecture is used to keep numerical kernels, preprocessing, orchestration, and reliability services decoupled:

1. **Presentation Layer**
   - CLI entrypoint and optional App Designer GUI.
   - Accepts project configuration, geometry path, operating conditions, solver setup, and run mode.

2. **Application/Orchestration Layer**
   - Workflow engine that executes ordered stages with checkpoints:
     1) Input validation
     2) Geometry preparation
     3) Meshing
     4) Mesh quality + repair
     5) Physics setup
     6) Solver execution
     7) Post-processing and validation
   - Centralized run state management and failure recovery.

3. **Domain Layer (CFD Core)**
   - Geometry domain services.
   - Meshing/quality services.
   - Finite-volume pressure-based incompressible RANS solver.
   - Turbulence model implementations (e.g., Spalart-Allmaras, k-epsilon variants, k-omega SST where feasible in 2D).
   - Boundary condition and material model handlers.

4. **Infrastructure Layer**
   - MATLAB PDE Toolbox adapters (geometry import, triangulation support, PDEModel interoperability).
   - File IO, project persistence, checkpoint/restart, logging, report generation.
   - Diagnostics and telemetry.

5. **Reliability & Governance Cross-Cutting Layer**
   - Defensive validation guards on all interfaces.
   - Structured logging, exception enrichment, and controlled abort semantics.
   - Deterministic run fingerprints (config hash, mesh hash, solver hash).
   - Numerical safety controls (CFL guards, residual stagnation detection, fallback under-relaxation).

### 1.2 Execution Model
- **Primary mode**: deterministic batch run for reproducibility.
- **Secondary mode**: interactive steering (e.g., stop/resume, plot update frequency).
- **Checkpoint cadence**: user-defined iteration interval + mandatory checkpoint before risky operations (mesh repair and turbulence model switch).

### 1.3 Core Design Principles
- **Strict MATLAB R2022b compatibility**.
- **No hidden state**: all major modules pass typed structs/classes explicitly.
- **Fail fast on invalid inputs**, fail safe during runtime instabilities.
- **Numerical robustness first**, performance second (with vectorization and sparse operations applied where safe).
- **Auditability**: every run is reproducible from archived inputs + versioned settings.

---

## 2) Full Folder Structure

```text
matlab-cfd/
├─ main.m
├─ run_project.m
├─ +cfd/
│  ├─ +app/
│  │  ├─ WorkflowController.m
│  │  ├─ StageRunner.m
│  │  ├─ RunContext.m
│  │  └─ FailurePolicy.m
│  ├─ +config/
│  │  ├─ loadConfig.m
│  │  ├─ validateConfig.m
│  │  ├─ defaultConfig.m
│  │  └─ schema/
│  │     ├─ geometrySchema.m
│  │     ├─ meshSchema.m
│  │     ├─ solverSchema.m
│  │     └─ turbulenceSchema.m
│  ├─ +geom/
│  │  ├─ GeometryManager.m
│  │  ├─ importGeometry.m
│  │  ├─ repairGeometry.m
│  │  ├─ simplifyGeometry.m
│  │  ├─ detectFeatureEdges.m
│  │  └─ buildGeometryModel.m
│  ├─ +mesh/
│  │  ├─ MeshManager.m
│  │  ├─ generateInitialMesh.m
│  │  ├─ refineMeshAdaptive.m
│  │  ├─ computeMeshMetrics.m
│  │  ├─ repairMesh.m
│  │  ├─ enforceBoundaryLayerMesh.m
│  │  └─ convertToFvTopology.m
│  ├─ +physics/
│  │  ├─ MaterialDatabase.m
│  │  ├─ BoundaryConditionManager.m
│  │  ├─ initializeFlowField.m
│  │  └─ referenceScales.m
│  ├─ +solver/
│  │  ├─ PressureBasedSolver.m
│  │  ├─ MomentumEquation.m
│  │  ├─ PressureCorrectionEquation.m
│  │  ├─ CouplingSchemeSIMPLE.m
│  │  ├─ CouplingSchemeSIMPLEC.m
│  │  ├─ UnderRelaxationController.m
│  │  ├─ LinearSystemBuilder.m
│  │  ├─ LinearSolverFactory.m
│  │  ├─ ResidualMonitor.m
│  │  └─ ConvergenceController.m
│  ├─ +turbulence/
│  │  ├─ TurbulenceModelFactory.m
│  │  ├─ SpalartAllmarasModel.m
│  │  ├─ KEpsilonStandardModel.m
│  │  ├─ KEpsilonRNGModel.m
│  │  ├─ KOmegaSSTModel.m
│  │  ├─ WallFunctionManager.m
│  │  └─ TurbulenceFieldLimiter.m
│  ├─ +numerics/
│  │  ├─ GradientReconstruction.m
│  │  ├─ FluxCalculator.m
│  │  ├─ DiffusionOperator.m
│  │  ├─ ConvectionSchemes.m
│  │  ├─ RhieChowInterpolator.m
│  │  ├─ TimeIntegration.m
│  │  ├─ CflController.m
│  │  └─ MatrixDiagnostics.m
│  ├─ +quality/
│  │  ├─ QualityGate.m
│  │  ├─ MeshQualityRules.m
│  │  ├─ SolverHealthRules.m
│  │  ├─ PhysicsPlausibilityChecks.m
│  │  └─ ValidationSuite.m
│  ├─ +post/
│  │  ├─ PostProcessor.m
│  │  ├─ computeDerivedFields.m
│  │  ├─ integrateSurfaceQuantities.m
│  │  ├─ exportVTK.m
│  │  ├─ exportCSV.m
│  │  └─ generateRunReport.m
│  ├─ +io/
│  │  ├─ ProjectStore.m
│  │  ├─ saveCheckpoint.m
│  │  ├─ loadCheckpoint.m
│  │  ├─ FileLockManager.m
│  │  └─ PathManager.m
│  ├─ +logging/
│  │  ├─ Logger.m
│  │  ├─ LogEvent.m
│  │  ├─ LogLevel.m
│  │  └─ RunAuditTrail.m
│  ├─ +utils/
│  │  ├─ Assert.m
│  │  ├─ SafeMath.m
│  │  ├─ Hashing.m
│  │  ├─ Timer.m
│  │  └─ ParallelSupport.m
│  └─ +tests/
│     ├─ unit/
│     ├─ integration/
│     ├─ regression/
│     └─ benchmark/
├─ examples/
│  ├─ cavity2d/
│  ├─ backward_facing_step/
│  └─ cylinder_crossflow/
├─ resources/
│  ├─ templates/
│  ├─ material_db/
│  └─ validation_cases/
└─ docs/
   ├─ architecture.md
   ├─ numerical_methods.md
   ├─ failure_modes.md
   └─ user_workflow.md
```

---

## 3) Module Responsibilities

### 3.1 Orchestration (`+cfd/+app`)
- Build run plan from configuration.
- Execute stages transactionally with pre/post checks.
- Propagate stage outputs through `RunContext` only.
- Apply `FailurePolicy` (retry, fallback, abort) per error category.

### 3.2 Configuration (`+cfd/+config`)
- Parse and validate user configuration against strict schema.
- Fill defaults only when physically safe.
- Reject ambiguous or conflicting solver/turbulence settings.

### 3.3 Geometry (`+cfd/+geom`)
- Import 2D CAD (DXF/STL-derived boundary extraction where viable).
- Repair geometry defects (gaps, non-manifold edges, duplicate edges).
- Simplify tiny features below user threshold with topology preservation checks.
- Build MATLAB PDE geometry objects for downstream meshing.

### 3.4 Meshing (`+cfd/+mesh`)
- Generate initial triangulation via PDE Toolbox-driven meshing.
- Add boundary layer refinement and targeted local refinement.
- Convert mesh into finite-volume control-volume connectivity.
- Repair low-quality elements through smoothing/swapping/local remesh.

### 3.5 Physics Setup (`+cfd/+physics`)
- Define incompressible fluid properties (constant-density baseline).
- Map and validate BCs (velocity inlet, pressure outlet, wall/no-slip, symmetry).
- Initialize flow/turbulence fields robustly for convergence.

### 3.6 Solver Core (`+cfd/+solver` + `+cfd/+numerics`)
- Finite-volume discretization on unstructured 2D mesh.
- Pressure-based segregated solution using SIMPLE/SIMPLEC.
- Rhie–Chow pressure-velocity coupling to prevent checkerboarding.
- Residual and imbalance tracking, adaptive under-relaxation, CFL control.
- Stable sparse linear solves with matrix diagnostics and fallback solvers.

### 3.7 Turbulence (`+cfd/+turbulence`)
- Provide interchangeable RANS models through factory pattern.
- Solve additional transport equations and turbulence viscosity updates.
- Enforce boundedness/positivity and wall treatment consistency.

### 3.8 Quality/Validation (`+cfd/+quality`)
- Pre-solver mesh quality gates (skewness, non-orthogonality, aspect ratio).
- Runtime health checks (divergence trends, NaN/Inf contamination).
- Post-solver plausibility checks (mass conservation, pressure bounds).
- Case-based validation harness against reference benchmarks.

### 3.9 Postprocessing (`+cfd/+post`)
- Derived quantities: vorticity, y+, turbulence intensity, coefficients.
- Surface/volume integrals and force extraction.
- Export for ParaView/CSV and generate run report.

### 3.10 IO, Logging, Utilities (`+cfd/+io`, `+cfd/+logging`, `+cfd/+utils`)
- Atomic checkpointing and reliable restart.
- Structured logs with stage, iteration, severity, and root-cause context.
- Shared safety utilities for assertions, numeric guards, hashing, timing.

---

## 4) Data Flow Between Modules

### 4.1 Primary Pipeline
1. **User Input → Config Loader**
   - Inputs: project file + CLI flags.
   - Output: validated `Config` object.

2. **Config → Geometry Manager**
   - Inputs: CAD and geometry cleanup settings.
   - Output: `GeometryState` (clean topology + boundary tags).

3. **GeometryState → Mesh Manager**
   - Inputs: sizing/refinement settings.
   - Output: `MeshState` (nodes/elements/faces + FV connectivity).

4. **MeshState → Quality Gate**
   - Inputs: mesh thresholds.
   - Output: pass/fail + repaired `MeshState` + quality report.

5. **MeshState + Config → Physics Manager**
   - Output: `PhysicsState` (materials, BC maps, initial fields).

6. **MeshState + PhysicsState + Config → Solver**
   - Iterative outputs: `IterationState` snapshots.
   - Final output: `SolutionState` (u, v, p, turbulence fields, residual history).

7. **SolutionState + MeshState → PostProcessor**
   - Output: plots, integrated quantities, exported files, run summary.

8. **All Stages → Logger/Audit/Checkpoint**
   - Continuous write of logs, metrics, and restart points.

### 4.2 Key Data Contracts
- `Config`: immutable after validation.
- `GeometryState`: topology + tags + repair provenance.
- `MeshState`: geometric arrays + adjacency + quality metrics + hash.
- `PhysicsState`: BC/material tables + initialized variables.
- `IterationState`: current fields, residuals, relaxation, CFL, diagnostics.
- `SolutionState`: converged/terminated fields + convergence metadata.
- `RunReport`: machine-readable JSON + human-readable markdown/PDF summary.

### 4.3 Failure Handling Flow
- Stage failure raises typed exception with context.
- `FailurePolicy` decides retry/fallback/abort.
- On retry: restore nearest checkpoint and apply safer numerics (lower relaxation/CFL).
- On abort: persist failure bundle (inputs, logs, checkpoint, stack trace, diagnostics).

### 4.4 Validation Flow
- Pre-run: schema + geometry integrity + mesh gate.
- In-run: per-iteration residual and physical sanity checks.
- Post-run: mass imbalance threshold, benchmark comparison, and report verdict.

---

This architecture is deliberately staged to support a stepwise implementation where each module can be delivered fully runnable and integration-tested before moving to the next stage.
