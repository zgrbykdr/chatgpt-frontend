# DLL Insight Studio

DLL Insight Studio is a Windows desktop application (Python + PySide6 + SQLite) for guided analysis of complex DLL-based models.

## Features
- Automatic, Guided Semi-Automatic, and Expert workflows.
- PE file identification (x86/x64, native/.NET, protection suspicion).
- Metadata extraction (exports, imports, strings, resources, version info, numeric clues).
- String intelligence with manual relabeling support.
- Structural mapping for native and .NET branches.
- Function role classification with confidence/evidence.
- Variable ecosystem inference with offset/region grouping.
- Model-pattern ranking with evidence and uncertainty.
- Guided decision flows and runtime validation assistant.
- Report generation to HTML, PDF, JSON.
- SQLite project persistence, logs, report history.

## Project structure
- `dll_insight_studio/app.py` entry point
- `dll_insight_studio/gui/` GUI screens and navigation
- `dll_insight_studio/services/` workflow orchestration
- `dll_insight_studio/analyzers/` core analysis engines
- `dll_insight_studio/persistence/` database and repository
- `dll_insight_studio/reports/` report export modules
- `dll_insight_studio/runtime/` runtime validation module
- `dll_insight_studio/utilities/` helpers and logging
- `tests/` automated tests for core non-UI logic

## Setup (development)
1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -e .
   ```
4. Start app:
   ```bash
   python -m dll_insight_studio.app
   ```

## PDF report generation
PDF export uses `reportlab` (installed via dependencies). Use the **Report Preview / Export** screen and click **Export PDF**.

## Running tests
```bash
pytest
```

## Notes
- Core operation is local-only (no cloud dependencies).
- Runtime assistant gracefully degrades when host EXE is unavailable.
- Projects are stored under `workspace_projects/` with SQLite databases and exported reports.
