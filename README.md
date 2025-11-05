# HeatPumpSim

HeatPumpSim is a cross-platform desktop application for modeling and simulating liquid-to-liquid heat pumps using a vapor compression cycle. It offers an Amesim-style drag-and-drop environment with Moving-Boundary (MB) and Finite Volume Method (FVM) component models, a FastAPI-based numerical engine, and an Electron/Vite desktop shell.

## Quick Start

```bash
# Install Node dependencies
npm install

# Create a Python virtual environment and install packages
python -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt

# Launch the development environment (Electron + Vite + FastAPI)
npm run dev
```

The UI runs on `http://localhost:5173` and the Python engine listens on `http://127.0.0.1:8000`.

## Development Workflow

- **UI**: Located in `app/` (React + TypeScript + Tailwind). Use `npm run dev` for hot reloading.
- **Electron shell**: Located in `electron/`. Manages the desktop window and Python subprocess.
- **Engine**: Located in `server/`. Provides FastAPI endpoints and simulation engine modules.
- **Schemas & Data**: JSON schemas, libraries, and scenarios live under `server/engine/graphs/` and `server/data/`.

Useful commands:

```bash
# Lint TypeScript and Python
npm run lint

# Run unit tests (Jest + pytest)
npm run test

# Build the React bundle
npm run build

# Generate JSON schemas
npm run schema
```

## Packaging

HeatPumpSim uses Electron Builder for cross-platform distribution.

```bash
# Package for the current platform (requires Python build artifacts)
npm run package
```

Packaging bundles the React app, Electron shell, and the FastAPI engine. For Windows, embed the Python runtime using python-embed. For macOS/Linux, use PyInstaller (see `tools/scripts` for helpers).

## Repository Layout

```
heatpump-sim/
  app/                # React UI
  electron/           # Electron main & preload scripts
  server/             # FastAPI service and simulation engine
  tools/              # Developer tools and scripts
  server/data/        # Component libraries & EN14511 scenarios
```

## Testing

- **Frontend**: Jest + React Testing Library (`npm run test:ui`).
- **Engine**: pytest (`npm run test:engine`).
- **Scenario**: EN 14511 working points under `server/data/scenarios/` with tests in `server/engine/tests/test_scenarios_en14511.py`.

## Documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`MODELS.md`](MODELS.md)
- [`API.md`](API.md)
- [`SCHEMAS.md`](SCHEMAS.md)
- [`VALIDATION.md`](VALIDATION.md)

## License

[MIT](LICENSE)
