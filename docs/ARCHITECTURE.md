# DLL Insight Studio Architecture

## Layers
- `gui/`: PySide6 presentation layer (navigation, workflows, forms, tables, wizard text).
- `services/`: orchestration for project lifecycle, guidance, and pipeline flow.
- `analyzers/`: modular analysis engines for file identity, metadata, string intelligence, structure, function roles, variables, and model patterns.
- `persistence/`: SQLite schema/versioning and repository persistence APIs.
- `runtime/`: runtime validation workflow support with graceful fallback.
- `reports/`: HTML/PDF/JSON report generation.
- `utilities/`: logging and hash helpers.

## Pipeline
Project setup -> file identification -> metadata extraction -> string classification -> structural mapping -> function role scoring -> variable inference -> pattern ranking -> guidance/runtime updates -> report generation.

## Confidence & Evidence
Each major classifier emits confidence plus evidence text. User decisions and runtime notes are persisted and can be applied during rerun.
