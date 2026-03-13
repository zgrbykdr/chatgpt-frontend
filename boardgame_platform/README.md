# Board Game Platform (Python + Pygame)

A modular, data-driven desktop board game platform with a fully playable default Monopoly mode and integrated custom content tooling.

## Features
- Default Monopoly board, rules, and decks loaded from JSON
- Data-driven square/card action system
- Turn flow, dice, jail handling, taxes, property purchase, rent, bankruptcy state
- Save/load full game state (`boardgame_platform/saves/*.json`)
- Expandable module layout for new square types, actions, themes, and decks
- In-app menu, gameplay screen, player side panels, card popup overlays
- Editor architecture (`editor/board_editor.py`, `editor/deck_editor.py`, `editor/rule_editor.py`)
- Polished fallback visuals generated in Pygame (no external assets required)

## Run
```bash
pip install -r boardgame_platform/requirements.txt
python boardgame_platform/main.py
```

## Project Structure
- `core/`: engine, turn manager, action executor, state, events
- `board/`: board/square data model, loader, property logic
- `cards/`: deck loading and card execution
- `players/`: player model and token drawing
- `ui/`: menu, game scene, renderer, popups, animations, panels
- `editor/`: board/deck/rule editing helpers
- `save/`: JSON save/load manager
- `data/boards`: custom boards (default `monopoly.json`)
- `data/decks`: custom decks (`chance.json`, `community_chest.json`)
- `data/rules`: rule profiles (`monopoly_rules.json`)
- `assets/`: drop-in optional art/themes/icons/tokens/effects

## Custom Content
- Add custom boards in `data/boards/` and load via `GameEngine(board_path=...)`
- Add deck JSON files in `data/decks/` and register via `deck_paths`
- Modify or add rules JSON in `data/rules/`
- Define square/card behavior through `actions` arrays using built-in action types in `core/action_executor.py`

## Add New Action Types
1. Add a new `type` branch in `core/action_executor.py`
2. Implement behavior in `core/game_engine.py` or dedicated subsystem
3. Reference the action in board or deck JSON

## Theme / Asset Changes
- Drop image assets into `assets/` and update renderer paths
- Keep fallback generated visuals for missing files
- Tune `ui/theme_manager.py` palette and group color mapping

## Notes
This is an expandable production-style baseline with working Monopoly gameplay and mod-friendly JSON data. It is intentionally modular to support advanced future features like auctions, mortgages, AI players, network play, and full editor UI depth.
