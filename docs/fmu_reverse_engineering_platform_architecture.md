# MATLAB/Simulink FMU Reverse-Engineering & Surrogate Modeling Platform

## 1) Executive Summary

### What the platform does
This platform is a **production-grade, modular FMU analysis and surrogate-modeling system** that ingests complex FMUs (co-simulation or model-exchange), probes them safely, learns input-output behavior, and exports deployable artifacts to MATLAB/Simulink.

It explicitly supports the hierarchy:
1. Single analytic equation
2. Piecewise analytic equation
3. Dynamic identified model
4. Statistical/ML surrogate model
5. Lookup table fallback

### Why this architecture is appropriate
- **Black-box robust**: treats FMU as partially observable and failure-prone.
- **Method-agnostic orchestration**: multiple model families compete under unified scoring.
- **Traceable and reproducible**: configuration snapshots, run manifests, experiment logs, model lineage.
- **High-dimensional ready**: DOE + adaptive sampling + feature screening + regime segmentation.
- **Engineering deployment oriented**: direct export to Simulink blocks, MATLAB classes/functions, validation scripts, reports.

### Technical limits (explicit)
- Exact recovery of internal physical equations from black-box FMU is generally impossible.
- Best possible outcome is often **behavioral equivalence over validated operating regions**.
- Event-driven/hybrid logic and hidden states may only be approximated (piecewise or LUT/ML).
- Extrapolation outside tested domains is high risk and must be flagged.

---

## 2) Full Software Architecture

### Architectural style
Recommended: **Layered + Pipeline + Plugin** architecture.

- **UI Layer**: App Designer + CLI scripting.
- **Application Layer**: Project orchestration, workflow control, mode handling.
- **Domain Layer**: FMU introspection, DOE, behavior analysis, modeling engines, scoring.
- **Infrastructure Layer**: file I/O, logs, parallel runner, report/export generators.

### Core data contracts
- `ProjectConfig` (user settings + defaults)
- `FMUMetadata` (variables, units, causality, variability, limits)
- `VariableCatalog` (classified roles + confidence)
- `ExperimentPlan` (stimulus schedule + safety policy)
- `RunRecord` (execution results, diagnostics)
- `DatasetBundle` (train/val/test + regime tags)
- `ModelArtifact` (trained model + metadata)
- `ScoreCard` (metrics vector + weighted score)
- `SelectionReport` (best-by-objective set)

### Module interconnection (high-level)
1. FMU import/introspection -> metadata repository.
2. Variable classification + range inference + user constraints.
3. Experiment planner builds safe DOE/excitation plans.
4. Simulation orchestrator executes runs in parallel.
5. Dataset builder + behavior analyzer characterize plant behavior.
6. Model factory instantiates candidate pipelines.
7. Model engines train/evaluate candidates.
8. Scorer + selector determine champion models.
9. Export/report subsystems generate deliverables.

---

## 3) Detailed Module List

| Module | Purpose | Inputs | Outputs | Dependencies | Extension Points |
|---|---|---|---|---|---|
| `FMUInspector` | Parse FMU and extract FMI metadata | FMU path | `FMUMetadata` | FMI APIs, XML parser | FMI 2/3 adapters |
| `MetadataRepository` | Versioned metadata store | metadata updates | queryable metadata | MAT/JSON persistence | new schema fields |
| `VariableClassifier` | Infer input/output/parameter/constant/state roles | metadata + probe data | `VariableCatalog` | stats, rules engine | custom rules |
| `RangeInferenceEngine` | Infer missing variable limits | metadata + pilot simulations | range estimates + confidence | DOE + robust stats | alternative inference policies |
| `UserConstraintManager` | Merge user constraints with inferred limits | user inputs + inferred ranges | resolved constraints | App layer | policy presets |
| `ExperimentPlanner` | Generate test plans | constraints + budget + behavior hints | `ExperimentPlan` | Excitation library | new DOE generators |
| `ExcitationLibrary` | Signals (step/chirp/PRBS/LHS/Sobol etc.) | variable specs | trajectories | Signal Processing utilities | custom excitation templates |
| `FMURunner` | Single-run FMU execution | run definition | run outputs + status | Simulink/FMU block | solver adapters |
| `SimulationOrchestrator` | Batch scheduling, retries, parallelization | plan | run records | Parallel Computing Toolbox | new retry policies |
| `DatasetBuilder` | Build clean datasets from raw runs | run records | train/val/test bundle | timetable/table | custom splitters |
| `BehaviorAnalyzer` | Static/dynamic/switching detection | dataset | behavior profile | System ID + stats | new detectors |
| `FeatureEngineer` | Generate lag, interaction, normalized features | dataset | feature matrix | Statistics toolbox | domain features |
| `ModelFactory` | Build candidate model specs | behavior profile + config | candidate list | all model engines | plugin registry |
| `EquationDiscoveryEngine` | Sparse symbolic/equation fits | features + outputs | analytic models | Symbolic + optimization | basis dictionaries |
| `PiecewiseModelEngine` | Partition space and fit local models | data + partitions | piecewise models | clustering/tree | partitioners/blenders |
| `DynamicIdentificationEngine` | ARX/OE/SS/NARX/HW identification | time-series data | dynamic models | System ID Toolbox | new id structures |
| `StatisticalModelEngine` | GPR/SVR/ensembles/NN | supervised dataset | ML models | Stats & ML | model wrappers |
| `LookupTableEngine` | N-D LUT construction/refinement | data + importance ranking | LUT artifacts | Simulink LUT blocks | interpolation/refinement policies |
| `HyperparameterTuner` | Bayesian/grid/random tuning | candidate model + budget | tuned model variants | Global Optimization | search strategy plugins |
| `ModelScorer` | Multi-objective evaluation | predictions + metrics | `ScoreCard` | validation utilities | scoring formula modules |
| `ModelSelector` | Pick best models by objective | scorecards | selected portfolio | rules engine | safety-first selectors |
| `ValidationEngine` | CV, stress tests, regime validation | model + dataset | validation reports | parallel + stats | new test suites |
| `ExportManager` | Export model artifacts | selected models | MATLAB/Simulink artifacts | Simulink APIs | new exporters |
| `ReportGenerator` | Generate HTML/PDF technical reports | all artifacts | reports | MATLAB Report Generator (or custom) | templates |
| `ConfigManager` | Read/write config and manifests | user/project configs | validated config objects | JSON/MAT utilities | schema versions |
| `LogManager` | Structured logging and lineage | events, errors | logs and trace IDs | file/db logger | sinks (JSONL/SQLite) |
| `AppController` | Bind UI actions to backend services | UI events | workflow commands | App Designer | custom workflows |
| `ProjectManager` | Project lifecycle and state | project path/config | project snapshots | filesystem + config | remote artifact stores |

---

## 4) Suggested Folder Structure

```text
fmu-re-platform/
  app/
    +ui/
      FMUReverseEngineeringApp.mlapp
      controllers/
      viewmodels/
  src/
    +core/
      ProjectManager.m
      AppController.m
      ConfigManager.m
      LogManager.m
    +fmu/
      FMUInspector.m
      FMUMetadataParser.m
      FMURunner.m
      FMIAdapters/
    +metadata/
      MetadataRepository.m
      VariableCatalog.m
    +ranges/
      RangeInferenceEngine.m
      UserConstraintManager.m
    +experiments/
      ExperimentPlanner.m
      ExcitationLibrary.m
      SafetyGuard.m
    +simulation/
      SimulationOrchestrator.m
      RunExecutor.m
      FailureHandler.m
    +data/
      DatasetBuilder.m
      DataQualityChecker.m
      FeatureEngineer.m
    +analysis/
      BehaviorAnalyzer.m
      SensitivityAnalyzer.m
      RegimeDetector.m
    +models/
      ModelFactory.m
      ModelArtifact.m
      CandidateRegistry.m
    +models/+equation/
      EquationDiscoveryEngine.m
      BasisLibrary.m
      SparseRegressor.m
    +models/+piecewise/
      PiecewiseModelEngine.m
      PartitionEngine.m
      LocalModelFitter.m
    +models/+dynamic/
      DynamicIdentificationEngine.m
      DelayEstimator.m
      OrderSelector.m
    +models/+surrogate/
      StatisticalModelEngine.m
      GPRModel.m
      EnsembleModel.m
    +models/+lut/
      LookupTableEngine.m
      GridRefiner.m
      LUTExporter.m
    +optimization/
      HyperparameterTuner.m
      MultiObjectiveTuner.m
    +validation/
      ValidationEngine.m
      StressTestSuite.m
      ExtrapolationRiskEstimator.m
    +selection/
      ModelScorer.m
      ModelSelector.m
    +export/
      ExportManager.m
      SimulinkExporter.m
      MATLABCodeExporter.m
      ReportGenerator.m
  configs/
    schema/
    defaults/
    profiles/
  data/
    raw/
    processed/
    artifacts/
  reports/
  scripts/
    run_auto_pipeline.m
    run_batch_benchmark.m
  tests/
    unit/
    integration/
    regression/
    benchmark_fmus/
  docs/
    architecture/
    user_guide/
    developer_guide/
```

### Folder intent
- `app/`: App Designer UI and controller bindings.
- `src/`: production source code under package namespaces.
- `configs/`: schema-validated JSON profiles and defaults.
- `data/`: run-time artifacts and datasets.
- `reports/`: generated model comparison and validation reports.
- `tests/`: automated quality gates.
- `scripts/`: reproducible batch workflows/CI entry points.

---

## 5) MATLAB Package and Class Architecture

### Recommended namespaces
- `+core`, `+fmu`, `+metadata`, `+ranges`, `+experiments`, `+simulation`, `+data`, `+analysis`, `+models`, `+optimization`, `+validation`, `+selection`, `+export`, `+ui`.

### Key classes (examples)

#### `core.ProjectManager`
- **Role**: project lifecycle, state transitions.
- **Properties**: `ProjectId`, `RootPath`, `Config`, `State`, `ArtifactsIndex`.
- **Methods**: `createProject`, `loadProject`, `saveSnapshot`, `registerArtifact`.

#### `fmu.FMUInspector`
- **Role**: FMU parsing and capability detection.
- **Properties**: `FMUPath`, `FMIStandardVersion`, `ModelType`, `VariableTable`.
- **Methods**: `inspect`, `extractVariables`, `inferModelType`, `checkCapabilities`.

#### `ranges.RangeInferenceEngine`
- **Role**: infer unknown min/max.
- **Properties**: `ProbePolicy`, `RiskThreshold`, `ConfidenceModel`.
- **Methods**: `inferRanges`, `safeProbe`, `scoreConfidence`.

#### `experiments.ExperimentPlanner`
- **Role**: create multi-stage DOE/excitation plans.
- **Methods**: `buildInitialPlan`, `buildRefinementPlan`, `allocateBudget`.

#### `simulation.SimulationOrchestrator`
- **Role**: execute plans at scale with retries.
- **Methods**: `runPlan`, `runParallel`, `recoverFailedRuns`, `summarizeRunHealth`.

#### `analysis.BehaviorAnalyzer`
- **Role**: classify system behavior.
- **Methods**: `detectStaticVsDynamic`, `estimateDelay`, `detectRegimes`, `nonlinearityScore`.

#### `models.ModelFactory`
- **Role**: candidate generation by behavior-driven rules.
- **Methods**: `createCandidates`, `filterByBudget`, `attachTuners`.

#### `models.equation.EquationDiscoveryEngine`
- **Role**: sparse equation discovery + symbolic simplification.
- **Methods**: `buildDictionary`, `fitSparse`, `pruneTerms`, `simplifySymbolic`.

#### `models.dynamic.DynamicIdentificationEngine`
- **Role**: dynamic ID models.
- **Methods**: `fitARX`, `fitOE`, `fitStateSpace`, `fitNARX`, `selectOrder`.

#### `selection.ModelScorer`
- **Role**: compute composite ranking metrics.
- **Methods**: `computeMetrics`, `computeCompositeScore`, `explainScore`.

#### `export.ExportManager`
- **Role**: artifact generation.
- **Methods**: `exportSimulinkSubsystem`, `exportMATLABFunction`, `exportLUTBlock`, `exportReport`.

Relationships: `ProjectManager` owns repositories and orchestrates services; engines are stateless where possible and consume config plus data contracts.

---

## 6) End-to-End Workflow

1. **Import FMU**
   - Load FMU and parse `modelDescription.xml`.
   - Detect FMI version/type (Co-Simulation vs Model Exchange).
2. **Metadata inspection**
   - Extract variable table: causality, variability, units, initial/start/nominal/min/max.
3. **Role inference**
   - Classify ambiguous variables (parameter vs input candidate etc.).
4. **Range inference**
   - Use metadata first; safe pilot probing second; robust envelope estimation third.
5. **Constraint merge**
   - Apply user hard/soft bounds, fixed constants, forbidden zones.
6. **Experiment plan generation**
   - Stage 1 exploration + Stage 2 refinement + Stage 3 active learning.
7. **Simulation execution**
   - Parallel run batches, capture failures with trace IDs and retry policy.
8. **Dataset assembly**
   - Build synchronized input/output datasets and quality labels.
9. **Behavior analysis**
   - Determine static/dynamic/switching, delays, monotonicity, saturation, hysteresis signals.
10. **Model candidate generation**
    - Behavior-driven shortlist from Equation/Piecewise/Dynamic/ML/LUT families.
11. **Training + tuning**
    - Fit all candidates under compute budget and constraints.
12. **Validation + scoring**
    - Cross-region and stress validation, uncertainty/risk estimation, complexity/runtime scoring.
13. **Selection**
    - Return portfolio: best-accuracy, best-explainability, best-runtime, safest.
14. **Export + reporting**
    - Export MATLAB/Simulink artifacts, plots, and full traceability report.

---

## 7) Model Orchestration Logic

### Rule-based decision engine (initial)

```pseudo
if dynamic_score < T_dyn and hysteresis_score < T_hys:
    try simple analytic models first
    if fit_quality >= Q_target: select analytic
    else try rich nonlinear equation + sparse symbolic
    if still poor: try piecewise
else:
    estimate delay and memory depth
    try ARX/OE/SS baseline
    if nonlinearity high: add NARX/Hammerstein-Wiener

if switching/regime_score high:
    force piecewise/tree-partition branch

if all equation/dynamic surrogates fail target or extrapolation risk high:
    build adaptive LUT fallback
```

### Suggested thresholds (configurable)
- `Q_target`: NRMSE >= 0.90 (or domain-specific).
- `T_dyn`: autocorrelation/lag-importance threshold.
- `T_hys`: loop-area-based hysteresis indicator.
- `Risk_max`: extrapolation-risk ceiling for deployment approval.

---

## 8) Mathematical Modeling Catalog

| Family | Strengths | Weaknesses | Use when | Avoid when | MATLAB tools |
|---|---|---|---|---|---|
| Linear/Affine | Fast, interpretable | Misses nonlinearities | near-linear regime | strong nonlinearity | `fitlm`, `idpoly` |
| Polynomial/Sparse poly | Interpretable nonlinear | unstable extrapolation | smooth moderate nonlinear | high-dimensional raw | Curve Fitting + LASSO |
| Rational/Exp/Log/Power | Compact physics-like forms | fitting sensitivity | known functional shape | noisy multimodal | `fit`, custom lsq |
| Smoothing splines | Excellent interpolation | poor extrapolation | smooth static map | discontinuities | `fit` (spline) |
| Symbolic sparse discovery | Equation recovery attempt | dictionary bias | moderate complexity | heavy noise/switching | Symbolic + optimization |
| Piecewise local fits | Handles regimes | boundary artifacts | switching/saturation | extremely sparse data | tree/clustering + local regression |
| ARX/ARMAX/OE/BJ | Strong dynamic baseline | linear structure limits | dynamic linear-ish | severe nonlinearity | System Identification Toolbox |
| State-space | compact dynamic models | less interpretable | MIMO dynamics | strong switching | `ssest`, `n4sid` |
| NARX/HW | nonlinear dynamics | tuning complexity | dynamic nonlinear | tiny datasets | `nlarx`, `nlhw` |
| GPR | uncertainty estimates | scaling limits | medium data, smooth maps | very large N/high D | `fitrgp` |
| SVR | robust nonlinear regression | hyperparameter sensitive | moderate high-D | huge datasets | `fitrsvm` |
| Ensemble trees | robust, nonparametric | less smooth | complex static/switching | need symbolic equation | `fitrensemble` |
| KNN/local regression | simple local behavior | memory/runtime heavy | dense local data | sparse/noisy high-D | `fitrknn`, `fit` |
| LUT (1D- nD) | deterministic deployment | memory explosion in high-D | strict runtime/safety | extreme dimensionality without reduction | Simulink LUT blocks |

---

## 9) Range Inference Strategy

### Multi-source range inference pipeline
1. **Metadata extraction**: use FMU min/max/start/nominal and units first.
2. **Semantic inference**: detect likely physical bounds by units and variable naming (e.g., `%`, temperature).
3. **Safe probing**:
   - Start near start/nominal.
   - Expand with geometric steps until instability/error/invalid output.
4. **Statistical envelope estimation**:
   - Use robust quantiles from successful runs.
   - Separate hard-failure boundary from soft-performance degradation boundary.
5. **Confidence scoring**:
   - `confidence = w_meta*meta_quality + w_probe*success_density + w_stability*margin`.
6. **User override**:
   - Hard bounds supersede inferred bounds.
   - Track source tags per bound: FMU/inferred/user.

### Bound schema per variable
- `hardMin`, `hardMax`, `softMin`, `softMax`, `defaultValue`, `forbiddenZones[]`, `source`, `confidence`.

---

## 10) Experiment Design Strategy

### Stage A: Initial exploration (coverage-first)
- OFAT scans for sensitivity screening.
- LHS/Sobol across active variables for global coverage.
- Basic step/ramp for dynamic clues.

### Stage B: Behavior-targeted refinement
- If dynamic: PRBS, chirp, sine sweep, multi-step.
- If switching suspected: boundary-focused random staircase.
- If saturation suspected: edge-biased sampling near soft limits.

### Stage C: Adaptive/active learning
- Use model uncertainty or high residual regions to request new samples.
- Acquisition examples: max variance (GPR), max disagreement (ensemble), max residual region coverage.

### Safety-aware probing
- Guardrails:
  - max slew rate per input
  - envelope monitor on outputs
  - simulation timeout/watchdog
  - rollback to safe operating point
- Failed simulation handling:
  - classify failure type (divergence, event error, numeric issue)
  - record and avoid region by exclusion mask.

---

## 11) Validation Framework

### Data splits
- Run-level split (avoid leakage across temporally related segments).
- Region-aware split (ensure each regime has train/val/test representation).
- Extrapolation holdout (outer-shell region reserved for risk estimate).

### Metric suite
- Accuracy: RMSE, MAE, max error, R², NRMSE.
- Dynamic: transient error, settling error, delay mismatch, frequency-response mismatch.
- Robustness: noise perturbation sensitivity, missing-point resilience.
- Cost: inference runtime, memory footprint.
- Explainability: closed-form simplicity, number of parameters, monotonic constraints satisfied.
- Risk: extrapolation risk and regime boundary risk.

### Stress tests
- Corner points and edge trajectories.
- Rapid switching sequences.
- Long horizon drift tests.

---

## 12) Export Strategy

### Export targets
1. **Analytic equation**
   - MATLAB function + symbolic expression + validity domain.
2. **Piecewise equation**
   - region predicates + local equations + optional blend functions.
3. **Dynamic models**
   - `idmodel` objects + Simulink identified model block wrappers.
4. **Surrogate ML models**
   - compact prediction function/class + serialized model object.
5. **LUT models**
   - Simulink 1D/2D/nD Lookup Table blocks with interpolation config.
6. **Validation assets**
   - scripts to replay benchmark test sets and regenerate plots.

### Simulink integration strategy
- Generate a reusable subsystem per selected model type.
- Auto-construct input/output bus interfaces.
- Embed validity checks (assertions/saturation) around model block.
- For piecewise/LUT, include domain monitor and fallback behavior.

---

## 13) App Designer UI Architecture

### Proposed tabs/panels
1. **Project Setup**: create/load project, mode select (auto/semi/manual).
2. **FMU Import**: load FMU, inspect capabilities, model type.
3. **Variable Inspector**: variable table, role/confidence editing.
4. **Range Manager**: bounds, forbidden zones, confidence/source tags.
5. **Experiment Planner**: DOE/excitation configuration and budget.
6. **Simulation Monitor**: run queue, progress, failures, retries.
7. **Data Explorer**: trajectory plots, scatter matrices, distribution checks.
8. **Model Discovery Dashboard**: candidate families, tuning status.
9. **Candidate Comparison**: sortable metrics, Pareto front.
10. **Equation Viewer**: symbolic form, simplification, validity range.
11. **Lookup Table Viewer**: grid density, interpolation, memory estimates.
12. **Validation Dashboard**: regime errors, stress test results, uncertainty.
13. **Export Center**: choose targets/profiles and generate artifacts.
14. **Logs & Diagnostics**: trace IDs, warnings, failure summaries.

### UI-backend data flow
- UI manipulates `ProjectConfig` via `AppController`.
- All heavy tasks executed asynchronously through service layer.
- Progress events published to monitor/log tabs.

---

## 14) Configuration System

### Configuration files
- `project.json`: project-level settings and selected FMU.
- `variables.json`: role classifications and range constraints.
- `experiments.json`: DOE/excitation policies and budgets.
- `modeling.json`: allowed families, tuning budgets, objective weights.
- `export.json`: export targets and profiles.
- `manifest.json`: immutable run manifest with hashes and timestamps.

### Reproducibility metadata
- FMU checksum/hash.
- toolbox versions.
- random seeds.
- solver settings.
- Git commit hash of platform.

---

## 15) Logging and Traceability

### Logging design
- Structured JSONL logs with event schema:
  - `timestamp`, `traceId`, `projectId`, `module`, `severity`, `eventType`, `payload`.
- Event types:
  - metadata extracted
  - range inferred
  - run started/completed/failed
  - model trained/failed
  - selection decision + reason
  - export generated

### Lineage
- Every model artifact stores:
  - training dataset IDs
  - config hash
  - feature pipeline version
  - metrics + validation suite ID

---

## 16) Testing Strategy

### Unit tests
- Variable classification, range merging, metric calculations, exporters.

### Integration tests
- Full pipeline on small benchmark FMUs.
- Co-simulation and model-exchange path coverage.

### Regression tests
- Golden scorecards for benchmark FMUs.
- Detect metric drift across releases.

### Benchmark suite
- Synthetic FMUs with known ground-truth equations.
- Dynamic MIMO FMUs with delays.
- Hybrid/switching FMUs.
- “Failure-prone” FMUs for robustness testing.

---

## 17) Development Roadmap

### MVP (Phase 1)
- FMU introspection, variable/range management, basic DOE, runner/orchestrator.
- Initial model engines: linear/polynomial + ARX/OE + GPR + basic LUT.
- Scoring/selection + minimal export + CLI scripts.

### Phase 2
- Piecewise engine, symbolic sparse discovery, adaptive sampling.
- App Designer full workflow with monitoring and dashboards.
- Enhanced validation suite and report generator.

### Phase 3
- Advanced nonlinear dynamics (NARX/HW), robust multi-objective tuning.
- Regime-aware LUT refinement and memory optimization.
- Extensive CI regression and benchmark automation.

### Production hardening
- performance profiling and parallel scale testing.
- fault-tolerance improvements.
- schema/version migration tools.
- documentation and user training materials.

---

## 18) Risks and Limitations

### Feasible
- Strong behavioral surrogates in validated operating envelope.
- Reliable ranking across multiple objectives with transparent tradeoffs.

### Uncertain/hard
- Exact internal equation recovery for opaque FMUs.
- Reliable extrapolation in high-dimensional sparse regions.
- Fully capturing event-driven logic without state/event visibility.

### When LUT is better than equations
- Highly discontinuous/switching behavior.
- Strict deterministic runtime requirements.
- Equations fail error thresholds despite extensive fitting.

---

## 19) Recommended Deliverables

1. MATLAB project repository with package-structured source.
2. App Designer app (`.mlapp`) with end-to-end tabs.
3. CLI scripts for batch processing and CI.
4. Config schemas + default profiles.
5. Benchmark FMU suite + test harness.
6. Export templates (MATLAB funcs, classes, Simulink subsystems, LUT blocks).
7. Technical report templates (HTML/PDF).
8. Architecture + user + developer documentation.

---

## 20) Final Recommendation

### Architecture choice comparison
- **Option A: Monolithic script-driven pipeline**
  - Pros: fast to prototype.
  - Cons: poor maintainability/extensibility, weak traceability.
- **Option B: Service-oriented modular MATLAB packages (recommended)**
  - Pros: extensible engines, testable modules, production traceability.
  - Cons: higher initial engineering effort.

### Recommended implementation priority
1. Build robust data contracts and logging first.
2. Implement FMU inspection + safe experiment execution second.
3. Add baseline model families and selector third.
4. Add advanced piecewise/symbolic/adaptive components incrementally.
5. Build full App UI after stable backend contracts.

### Proposed model score formula (default)
Let normalized metrics (higher better) be:
- `A`: accuracy score
- `R`: robustness score
- `E`: explainability score
- `S`: safety score
- `C`: computational efficiency score
- `X`: extrapolation penalty (higher worse)

Composite:

\[
Score = 0.35A + 0.20R + 0.15E + 0.15S + 0.10C - 0.05X
\]

Adjust weights by mode:
- Automatic: balanced defaults.
- Semi-automatic: user priority sliders.
- Expert: custom objective vector + hard constraints.

### Explicit fallback policy (equation -> piecewise -> LUT)
1. Accept single equation only if accuracy/robustness/extrapolation criteria pass.
2. If not, attempt piecewise equation with bounded complexity.
3. If piecewise still fails or is too brittle, deploy LUT (possibly regime-specific).
4. Always provide a “safest model” candidate even if not most accurate.
