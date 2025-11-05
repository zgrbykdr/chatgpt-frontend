# Architecture

HeatPumpSim is a monorepo that couples an Electron desktop shell, a React + TypeScript UI, and a Python FastAPI engine for thermofluid simulations. The system is designed for deterministic, offline execution across Windows, macOS, and Linux.

## High-Level Overview

```
┌─────────────────────────────┐       ┌─────────────────────────┐
│ Electron Main Process       │       │ Python Runtime          │
│ - Launches Vite dev server  │ Web   │ FastAPI Application     │
│ - Spawns FastAPI subprocess │──────►│ - REST & WebSocket API  │
│ - Handles lifecycle events  │Socket │ - Simulation engine     │
└──────────────┬──────────────┘       └─────────┬───────────────┘
               │                                  │
               │                                  │
        ┌──────▼────────┐                  ┌──────▼────────────┐
        │ React UI      │                  │ Engine Core       │
        │ - Node canvas │                  │ - Graph parser    │
        │ - Property UI │◄─HTTP/WS────────►│ - Components      │
        │ - Validation  │                  │ - Integrators     │
        └───────────────┘                  └───────────────────┘
```

## UI Layer (`app/`)

- **Vite + React + TypeScript** with TailwindCSS for styling.
- **Canvas Graph**: Custom canvas (`GraphCanvas`) with smooth pan/zoom, snapping, and port-aware edges.
- **State Management**: Zustand store (`simulationStore.ts`) centralizes nodes, edges, validation, and scenario state.
- **React Query**: Manages HTTP queries (e.g., fluid lists).
- **IPC**: Uses `apiClient.ts` (fetch-based) and WebSocket hook (`useSimulationSocket`) to communicate with FastAPI.
- **Tests**: Jest + React Testing Library covering component interactions, validation overlays, and store logic.

## Electron Layer (`electron/`)

- **`main.ts`**: Creates the browser window, launches the Python subprocess through `PythonRunner`, and handles app lifecycle events.
- **`preload.ts`**: Exposes a safe `electronAPI` bridge for renderer processes.
- **`python-runner.ts`**: Resolves the Python executable (embedded runtime or local venv), spawns the FastAPI server, and streams stdout/stderr.
- **Packaging**: `builder-config.yml` configures Electron Builder for DMG, AppImage, and NSIS targets.

## Engine Layer (`server/`)

- **FastAPI** (`main.py`): Exposes simulation endpoints, property queries, model metadata, and WebSocket streams.
- **Routers** (`server/api/`): `routes_sim`, `routes_models`, `routes_props`, and `ws` provide REST/WS surfaces.
- **Graphs** (`engine/graphs/`): JSON Schema validation (`schemas.py`) ensures project files (.hpsim.json) adhere to a strict DSL.
- **Components** (`engine/components/`):
  - `MovingBoundaryHX` and `FiniteVolumeHX` implement MB and FVM HX models with region tracking and energy balances.
  - `Compressor`, `Pump`, `ExpansionValve`, `Sensor` capture key equipment behaviours.
- **Controls** (`engine/controls/`): PID controllers with anti-windup clamping.
- **Fluids** (`engine/fluids/`): `FluidState` wraps CoolProp with deterministic fallbacks for offline testing, providing properties via `PropsSI` or approximations.
- **Core Manager** (`engine/core/manager.py`):
  - Parses projects with `parse_project`.
  - Instantiates components and manages simulation time.
  - Maintains validation summaries and broadcasts snapshots to subscribers (WS).
  - Supports continuous and step execution with deterministic stepping.
- **Data** (`server/data/`): Library templates and EN 14511 scenario presets.
- **Tests** (`engine/tests/`): >35 pytest cases covering fluids, components, controls, manager behaviour, and EN 14511 scenarios.

## IPC & Data Flow

1. **User builds a model** in the React UI; the Zustand store manages the graph.
2. **Run command** serializes the graph (`exportProject`) and POSTs to `/sim/load`.
3. **Engine parses & instantiates** components, returning component IDs.
4. **Simulation run**: `/sim/run` (HTTP) triggers the manager; results stream via `/ws/sim` WebSocket.
5. **UI updates** validation, probes, and overlays with streamed snapshots.
6. **Scenario & reporting**: Scenario wizard loads EN14511 presets; reporting endpoints provide CSV exports (engine placeholder for extension).

## Determinism & Performance

- Fixed ordering of component evaluation ensures reproducible results.
- Simplified integrator with consistent timestep (`dt=1`) for deterministic tests.
- Float operations use double precision; energy residuals tracked per component and aggregated.

## Packaging Considerations

- Include Python runtime (python-embed on Windows) or PyInstaller bundles.
- Electron Builder config references `server/` for inclusion.
- Scripts in `tools/` support linting and schema generation; packaging hooks may be extended.

## Extensibility

- Additional components can extend `ComponentModel` or `EnergyBalancedComponent`.
- JSON schemas may be expanded via `tools/scripts/generate_schemas.ts` to propagate to UI.
- Validation and reporting can be enriched by subscribing to WebSocket snapshots.
