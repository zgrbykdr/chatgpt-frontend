# D&D 3e Master Suite (PySide6)

A modular desktop Game Master command center for Dungeons & Dragons 3rd Edition inspired workflows.

## Included systems
- Dashboard
- GM Assistant generators (NPC/Quest/Encounter/etc.)
- Tactical Battle Map + combat tracker
- Lore Manager database editor
- Story Engine event pressure generator
- Atmosphere (music/ambience) controller with graceful missing-file handling
- Dice Lab with d20 helpers and simulation
- Settings panel

## Install
1. Install Python 3.10+.
2. Open terminal in this folder.
3. Run: `python -m venv .venv`
4. Activate venv:
   - Windows: `.venv\\Scripts\\activate`
   - macOS/Linux: `source .venv/bin/activate`
5. Install deps: `pip install -r requirements.txt`

## Run
`python main.py`

## Build EXE (Windows)
1. Install builder: `pip install pyinstaller`
2. Build: `pyinstaller --noconfirm --windowed --name dnd3e_master_suite main.py`
3. Copy `data`, `assets`, and `saves` folders beside generated executable.

## Notes
- Campaign autosaves on close.
- JSON writes are atomic via temp-file replacement.
- Sample campaign is auto-created in `saves/campaigns/sample_campaign.json`.
