# FMU Reverse Engineering Platform

Production-grade, modular platform for reverse engineering FMUs and deriving high-fidelity surrogate models (equations, piecewise models, LUTs, and dynamic surrogates).

## Deliverables in this starter

This repository includes:

1. **System architecture blueprint** (A)
2. **Module-by-module responsibilities** (B)
3. **Recommended folder structure** (C)
4. **Base interfaces and registries** (D)
5. **Core typed data schemas** (E)
6. **Pipeline orchestration design and implementation** (F)
7. **Prioritized roadmap** (G)
8. **Starter implementation skeleton** (H)
9. **Example configuration files** (I)
10. **Example CLI commands** (J)
11. **End-to-end run flow example** (K)

---

## A) System architecture description

The platform is organized as a **configuration-driven workflow engine** orchestrating replaceable subsystems:

- FMU inspection and metadata extraction
- variable catalog + dependency graph generation
- range inference + feasible region learning
- experiment design (OFAT, DOE, adaptive, dynamic tests)
- scalable simulation execution and artifact tracking
- data cleaning + feature engineering
- influence/sensitivity discovery
- progressive model zoo search
- piecewise/regime discovery
- LUT and dynamic surrogate fallback
- multi-objective evaluation and model selection
- report and export generation

The orchestration strategy follows staged complexity:

1. Interpretable global equations
2. Sparse/symbolic models
3. Strong black-box baselines
4. Regime-based piecewise models
5. LUT fallback
6. Dynamic identification path (if memory effects detected)

---

## B) Module-by-module responsibilities

See [`docs/architecture.md`](docs/architecture.md) and [`docs/workflow.md`](docs/workflow.md).

---

## C) Final recommended folder structure

The skeleton follows the requested structure under `src/fmu_reverse_engineering/` and supporting top-level directories.

---

## D) Base class/interface design

Key interfaces live in:

- `models/base.py`
- `experiments/base.py`
- `evaluation/base.py`
- `workflows/pipeline.py`
- plugin registries in `core/registry.py`, `models/registry.py`

---

## E) Data schema definitions

Typed Pydantic schemas in:

- `domain/schemas/fmu_schema.py`
- `domain/schemas/variable_schema.py`
- `domain/schemas/experiment_schema.py`
- `domain/schemas/dataset_schema.py`
- `domain/schemas/model_schema.py`
- `domain/schemas/lut_schema.py`
- `domain/schemas/report_schema.py`

---

## F) Pipeline orchestration design

Three modes are implemented in `workflows/`:

- automatic
- semi-automatic
- manual

A shared `PipelineOrchestrator` executes the full stage graph with mode-specific plan construction.

---

## G) Prioritized development roadmap

### Phase 1 (MVP)
- FMU inspector + metadata export
- basic experiment design (OFAT + LHS)
- simulation runner with fault capture
- baseline model zoo (constant/linear/polynomial/GP/RF)
- evaluator and ranking
- HTML/JSON report

### Phase 2
- symbolic regression and sparse discovery
- regime detector + piecewise fitting
- LUT builder with adaptive grid
- richer sensitivity methods

### Phase 3
- dynamic model identification (ARX/NARX/state-space)
- robust active learning loops
- full C/C++ export hardening
- industrial-scale parallel execution

---

## H) Starter code skeleton

Implemented in `src/fmu_reverse_engineering/` with extensible interfaces, orchestrator, registry patterns, and placeholders for subsystem implementation.

---

## I) Example configs

See `configs/default.yaml`, `configs/automatic_mode.yaml`, `configs/semi_automatic_mode.yaml`, `configs/manual_mode.yaml`, and `configs/model_zoo.yaml`.

---

## J) Example CLI commands

```bash
python scripts/run_pipeline.py --fmu path/to/model.fmu --mode automatic --config configs/default.yaml
python scripts/inspect_fmu.py --fmu path/to/model.fmu --out artifacts/reports/inspection
python scripts/fit_models.py --dataset artifacts/processed/dataset.parquet --config configs/model_zoo.yaml
```

---

## K) Example run flow

1. User passes FMU path and mode.
2. Inspector extracts metadata and writes:
   - `fmu_manifest.json`
   - `variable_catalog.csv`
   - `dependency_graph.json`
3. Range inference proposes input envelopes.
4. Experiment designer creates screening + DOE plan.
5. Runner executes FMU simulations and records failures.
6. Data pipeline builds clean/train/validation datasets.
7. Influence engine proposes reduced variable sets and constants.
8. Model search executes staged zoo.
9. If needed: regime detector + LUT builder + dynamic model path.
10. Evaluator ranks candidates (accuracy + simplicity + robustness + runtime).
11. Selector exports best surrogate per output and final report.

## Development

```bash
pip install -e .[dev]
pytest -q
```
