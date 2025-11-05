# Schemas

HeatPumpSim uses a JSON graph DSL for project files (`.hpsim.json`). Validation is enforced on both frontend (Ajv) and backend (jsonschema Draft 2020-12). The canonical schema is exposed in TypeScript (`app/src/lib/schemas.ts`) and Python (`server/engine/graphs/schemas.py`).

## Project Graph Schema (`project.schema.json`)

### Root Object

| Field | Type | Description |
| ----- | ---- | ----------- |
| `version` | string | DSL version identifier (e.g., `"1.0.0"`). |
| `fluids` | array | List of fluid identifiers or objects with `name`, `role`, and optional `options`. |
| `components` | array | Array of component definitions (see below). |
| `connections` | array | Array of directed port connections. |
| `simulation` | object | Simulation configuration (start, stop, integrator, tolerances, scenario). |
| `units` | object | Display and reporting units. |
| `metadata` | object? | Optional metadata (validation summary, timestamps). |

### Component Object

| Field | Type | Description |
| ----- | ---- | ----------- |
| `id` | string | Unique identifier. |
| `type` | string | Component type (Evaporator, Compressor, etc.). |
| `modeling` | enum | `"MB"`, `"FVM"`, or `"LUMPED"`. |
| `params` | object | Arbitrary parameter map (geometry, HTC choice, etc.). |
| `ports` | array | Array of `{ name, direction, medium }`. Medium is one of `refrigerant`, `liquid`, `heat`, `signal`, `power`. |
| `ui.position` | object? | Optional `{ x, y }` coordinates for layout persistence. |

### Connection Object

| Field | Type | Description |
| ----- | ---- | ----------- |
| `id` | string | Unique connection ID. |
| `from` | object | `{ id, port }` referencing the source component/port. |
| `to` | object | `{ id, port }` referencing the destination component/port. |
| `type` | enum | `"fluid"`, `"heat"`, `"signal"`, or `"power"`. |

### Simulation Config

| Field | Type | Description |
| ----- | ---- | ----------- |
| `start` | number | Start time (s). |
| `stop` | number | Stop time (s). |
| `integrator` | enum | `"BDF2"` or `"TRAP"`. |
| `scenario` | string? | Optional scenario identifier (e.g., `"W10/W35"`). |
| `tolerances` | object | `{ absolute, relative }` error tolerances. |

### Units

| Field | Type | Description |
| ----- | ---- | ----------- |
| `temperature` | enum | `"C"` or `"K"`. |
| `pressure` | enum | `"Pa"` or `"bar"`. |
| `massFlow` | enum | `"kg/s"` or `"g/s"`. |

## Validation Strategy

1. **Frontend**: `validateProject` wraps Ajv with formats and throws `ValidationError` capturing schema paths.
2. **Backend**: `validate_project` uses `jsonschema.Draft202012Validator` to reject invalid payloads before instantiation.
3. **Testing**: Jest and pytest include schema validation coverage to prevent regressions.

## Schema Generation

`npm run schema` executes `tools/scripts/generate_schemas.ts`, exporting the schema JSON to `dist/schemas/project.schema.json`. This artifact can feed external tooling (e.g., editors, CI validation).

## Extending the Schema

- Add new component types by extending the `enum` in `schemas.ts`/`schemas.py` and updating component factories.
- Optional parameters belong in the `params` object; to enforce shape, consider adding component-specific schema fragments.
- Non-breaking changes should increment the `version` field for clarity and compatibility checks.
