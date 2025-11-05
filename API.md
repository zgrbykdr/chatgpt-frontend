# API Reference

The FastAPI server exposes HTTP and WebSocket interfaces for managing simulations, querying model metadata, and retrieving thermophysical properties. All responses are JSON unless otherwise noted.

Base URL: `http://127.0.0.1:8000`

## Simulation

### `POST /sim/load`

Load and validate a project graph.

- **Body**: JSON object conforming to `project.schema.json`.
- **Response**: `{ "status": "ok", "components": ["comp", ...] }`.

### `POST /sim/run`

Start simulation execution.

- **Body**:
  ```json
  {
    "mode": "continuous" | "step",
    "step": 1.0            // optional for step mode
  }
  ```
- **Response**:
  - Continuous: `{ "status": "started" }`
  - Step: `{ "status": "step", "time": <float> }`

### `POST /sim/pause`

Cancel the background simulation task.

- **Response**: `{ "status": "paused" }`

### `POST /sim/reset`

Reinitialize component states to project initial conditions.

- **Response**: `{ "status": "reset" }`

### `WS /ws/sim`

Bidirectional WebSocket streaming simulation snapshots.

- **Messages** (server → client):
  ```json
  {
    "type": "state",
    "time": 120.0,
    "components": {
      "comp": { "power": 4500.0, ... },
      "evap": { "heatDuty": 12000.0, ... }
    },
    "validation": {
      "energyResidual": 320.0,
      "jacobianCondition": 1.5,
      "warnings": []
    }
  }
  ```

## Model Metadata

### `GET /models/correlations`

Returns available correlations for boiling, condensation, and two-phase pressure drop.

```
{
  "boiling": ["Chen", "Shah", "Kandlikar"],
  "condensation": ["Shah"],
  "twoPhasePressureDrop": ["LockhartMartinelli"]
}
```

### `GET /models/defaults`

Default parameter sets for key components (e.g., evaporator, condenser, compressor).

## Thermophysical Properties

### `GET /props/list_fluids`

Enumerates fluids available through CoolProp wrappers.

### `POST /props/query`

Evaluate basic fluid properties.

- **Body**:
  ```json
  {
    "fluid": "Water",
    "pressure": 101325,
    "temperature": 298.15
  }
  ```
- **Response**:
  ```json
  {
    "density": 997.0,
    "cp": 4180.0,
    "enthalpy": 10483.2
  }
  ```

## Reporting (Placeholder)

### `POST /report/export`

Reserved for CSV export of time-series results. Implementers can extend `SimulationManager` to generate aggregated CSV lines per snapshot and return a download URL or inline data.

## Error Handling

Validation errors return HTTP 422 with a message aggregated from JSON Schema diagnostics. Runtime errors (e.g., calling `/sim/run` before `/sim/load`) return 500 with a descriptive message.
