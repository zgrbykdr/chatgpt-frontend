# Monopoly (2-Player, Local, Fully Customizable)

A fully playable 2-player Monopoly implementation with a GUI built in Python (PySimpleGUI). It ships with the original Monopoly board, Chance and Community Chest decks, and rules as defaults. You can edit any square (name, description, pricing, rent tables, taxes, movement rules) and both card decks at runtime using the in-app Editor. Save and load your own custom game configurations as JSON.

## Features
- 2 local players on the same computer
- Original Monopoly defaults (US/Atlantic City edition) preloaded
- Fully editable board squares and card decks in-app
- Dice rolling with doubles and 3-doubles-to-jail
- Property purchase, rent, color sets, houses/hotels with even-building enforcement
- Railroads and utilities with correct rent rules
- Jail rules (pay, doubles, card) and Get Out of Jail cards
- Taxes (income tax with choice, luxury tax)
- Chance and Community Chest cards (move, pay/collect, nearest railroad/utility, repairs, jail, GO, etc.)
- Mortgage and unmortgage (with interest)
- Auctions when property not purchased
- Trading between players (cash, properties, and Get Out of Jail cards)
- Free Parking is empty by default, but you can customize rules
- Save/Load custom configuration JSON

## Requirements
- Python 3.9+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

This opens the game window. The left shows the board and tokens; the right shows the control panel. The Editor tab lets you edit any square or card. Use the File menu to Save/Load configurations.

## Configuration Files
Defaults are stored in `monopoly/data`:
- `board.json`: Board squares with rules
- `chance.json`: Chance deck
- `community_chest.json`: Community Chest deck

You can save your edits to a new folder or overwrite these defaults. Use File → Save Config / Load Config to apply.

## Notes
- This build focuses on 2 players locally; networking is out of scope.
- If you encounter any issues with window scaling, try maximizing the window or adjusting your OS scaling.
- For clarity, the UI uses a simplified board image composed of labeled tiles (no artwork). All numbers and rules are functional.