# Board Game Platform (Python + Pygame)

A data-driven desktop board game platform with:
- A fully playable default Monopoly-style game
- JSON-defined boards, rules, and decks
- Save/load support
- In-app editors for board/deck/rules
- Modular architecture for extending square/card actions

## Setup

```bash
cd boardgame_platform
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

## Project layout

The project follows a modular architecture:
- `core/`: engine, turn processing, action execution, rule enforcement
- `board/`: board/square models and loading
- `cards/`: deck/card systems
- `players/`: player models and token metadata
- `ui/`: pygame screens, renderer, panels, animations
- `editor/`: board/deck/rule editors
- `save/`: save/load manager
- `data/`: JSON files for built-in Monopoly board, decks, and rules

## Custom boards and decks

- Add boards in `data/boards/*.json`
- Add decks in `data/decks/*.json`
- Add rules in `data/rules/*.json`

You can use **Editor** screens in-app to create and update these JSON definitions.

## Save/load

Game states are stored in `saves/` as JSON. Save files include:
- board/rules references
- full player states
- property ownership and buildings
- turn order and current turn
- deck order/indices

## Notes

- The default game uses classic Monopoly-style flow: buy/rent/taxes/jail/chance/community chest/bankruptcy.
- The action system is generic (`move`, `money`, `jail`, `card`, custom event/message) and shared by squares and cards.
