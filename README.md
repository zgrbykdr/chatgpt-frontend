# D&D 3E DM Desktop Manager (Python + PySide6)

This project is now implemented as a **Python desktop GUI application** (not JavaScript/Electron).

## What this app does
- Local-first campaign manager for D&D 3.0/3.5 style sessions.
- Character management for PCs/NPCs.
- Modifier-driven derived stats (initiative, AC, saves, ability mods).
- HP tracking with history + undo.
- Effects/conditions with round durations.
- Feat TXT import (`Name`, `Source`, `Description`) with dedupe by `Name+Source`.
- Feat rules mapping editor (`Mapped` / `Unmapped`).
- Demonstrations implemented:
  - **Improved Initiative** => `initiative +4`
  - **Fatigued** => `-2 STR`, `-2 DEX` with duration.

## Content policy
- Rules/content data are separate from code (`data/packs`, `data/schemas`, imported files).
- Only starter/SRD-style short summary samples are included.
- Private user imports are supported via TXT/JSON.

## Requirements
- Python 3.10+
- pip

## Installation
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run
From repository root (recommended):
```bash
python -m py_app.main
```

Alternative compatibility entrypoint (also from repository root):
```bash
python -m main
```

If you are already inside the `py_app/` folder, use:
```bash
python -m main
```

## Run tests
```bash
python -m unittest discover -s tests_py
```

## Build executable (optional)
Use PyInstaller:
```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name dnd3e_dm py_app/main.py
```
Output binary is generated under `dist/`.

## Key folders
- `py_app/` : Python application source
- `data/packs/` : starter data pack examples
- `data/schemas/` : JSON schema files
- `tests_py/` : Python tests
