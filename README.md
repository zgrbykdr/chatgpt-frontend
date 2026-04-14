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
2. Open terminal in repository root (`chatgpt-frontend`).
3. Create and activate a virtual environment:
   - PowerShell:
     ```powershell
     py -3 -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
4. Install dependencies and package:
   ```bash
   pip install -e .
   ```

## Run options
From the repository root, you can run any of these:
```bash
python -m dll_insight_studio.app
python -m dll_insight_studio
```
If installed via pip editable mode, you can also run:
```bash
dll-insight-studio
```
Or on Windows, double-click or run:
```bat
launch_dll_insight_studio.bat
```

## Troubleshooting: `ModuleNotFoundError: No module named 'dll_insight_studio'`
This means Python cannot see the package path yet. Fix it by:
1. `cd` into the repository root.
2. Running `pip install -e .`
3. Re-running `python -m dll_insight_studio.app`

If you do not want installation, you must still launch from repository root so Python can import the local package folder.

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
