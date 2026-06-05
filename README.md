# Box Board Game Studio

A complete Python 3 + Pygame desktop application for creating, editing, saving and playing custom 2D property/box board games.

## Turkish quick start

1. Python 3 kurun: https://www.python.org/downloads/
2. Terminal / Komut İstemi açın ve proje klasörüne girin.
3. Pygame kurun:
   ```bash
   python -m pip install -r requirements.txt
   ```
   Alternatif:
   ```bash
   python -m pip install pygame
   ```
4. Programı başlatın:
   ```bash
   python main.py
   ```

Program ilk açılışta şu klasörleri otomatik oluşturur:

- `games/`
- `saves/`
- `assets/`
- `default_templates/`
- `settings.json`

İlk açılışta `games/Classic_Property_Trading_Game_Template.json` otomatik oluşturulur. Ekranda daha genel isim olarak **Classic Property Trading Game Template** görünür.

## Features in this first working version

- Modern resizable Pygame UI with dark/light theme support.
- Main menu: Add New Game, Edit Existing Game, Play Game, Settings, Exit.
- JSON game creation with player counts, starting money, board square count, board layout, pass-start money and jail/waiting setting.
- Built-in 40-square classic property-trading template with start, properties, railroads, utilities, taxes, jail/waiting, free parking, go-to-jail, Chance and Community Chest style decks.
- Editor panels for board squares, square actions, timers, cards, rules, trade/debt notes and assets.
- Gameplay with dice animation, token movement animation, property purchase, rent, auction, simple trade, loans/debt due turns, building, mortgage, card draw, jail/waiting, bankruptcy and winner detection.
- Mid-game JSON save files in `saves/`.
- Safe JSON loading and missing asset fallback by using generated shapes/icons.


## Project file structure

See `FILE_STRUCTURE.md` for the full copy/paste-friendly project tree. The application code is in `main.py`, data is stored as JSON in `games/` and `saves/`, optional images can be placed in `assets/`, and the default classic property-trading template is bundled in both `games/` and `default_templates/`.

## Notes for non-programmers

- You do not need Pillow; this version only requires Pygame.
- If an image path is empty or invalid, the game keeps running and uses built-in colored shapes.
- If a JSON file is broken, it is skipped in the game list instead of crashing the program.
- Use `Save JSON` inside the editor after changing board squares, square actions, timers, decks or rules.
- Use `Save` during gameplay to write a JSON save file into `saves/`.
