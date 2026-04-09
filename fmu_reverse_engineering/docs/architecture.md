# Architecture

## Layered design

1. **Interface layer**: CLI/API/config parsing.
2. **Workflow layer**: mode orchestrators and stage sequencing.
3. **Domain services**: FMU, experiments, runner, analysis, models, evaluation.
4. **Infrastructure layer**: artifact store, logging, cache, registry.

## Core design principles

- Plugin-first registration for models/samplers/exporters.
- Strict schema-based contracts between stages.
- Full artifact persistence for reproducibility.
- Deterministic seeds and explicit run manifests.
- Graceful degradation on simulation failure.
