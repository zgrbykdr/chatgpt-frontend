from __future__ import annotations

from pathlib import Path
import sys

import pygame

from board.board_loader import BoardLoader
from core.game_engine import GameEngine
from editor.board_editor import BoardEditor
from editor.deck_editor import DeckEditor
from editor.rule_editor import RuleEditor
from players.player_model import Player
from save.save_manager import SaveManager
from ui.editor_screen import EditorScreen
from ui.game_screen import GameScreen
from ui.menu_system import MenuSystem


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def build_default_engine() -> GameEngine:
    board_loader = BoardLoader(DATA / "boards")
    board = board_loader.load_board("monopoly.json")
    engine = GameEngine.from_files(board, str(DATA / "rules" / "monopoly_rules.json"), DATA / "decks")
    engine.setup_default_decks()
    colors = [(220, 40, 40), (50, 90, 230), (35, 150, 60), (160, 80, 170)]
    for i, name in enumerate(["Player 1", "Player 2"]):
        engine.add_player(Player(name=name, token=f"token_{i+1}", color=colors[i]))
    for p in engine.state.players:
        p.money = engine.state.rules.get("starting_money", 1500)
    return engine


def run() -> int:
    pygame.init()
    screen = pygame.display.set_mode((1200, 860))
    pygame.display.set_caption("Board Game Platform")
    clock = pygame.time.Clock()

    engine = build_default_engine()
    game_screen = GameScreen(engine)
    menu = MenuSystem()
    editor_ui = EditorScreen()
    save_manager = SaveManager(ROOT / "saves")

    mode = "menu"
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if mode == "menu":
                    if event.key == pygame.K_UP:
                        menu.selected = (menu.selected - 1) % len(menu.options)
                    elif event.key == pygame.K_DOWN:
                        menu.selected = (menu.selected + 1) % len(menu.options)
                    elif event.key == pygame.K_RETURN:
                        if menu.selected == 0:
                            engine = build_default_engine()
                            game_screen = GameScreen(engine)
                            mode = "game"
                        elif menu.selected == 1:
                            try:
                                save_manager.load_into_engine("autosave.json", engine)
                                mode = "game"
                            except FileNotFoundError:
                                engine.state.messages.append("No autosave found")
                        elif menu.selected == 2:
                            mode = "editor"
                        else:
                            running = False
                elif mode == "game":
                    if event.key == pygame.K_SPACE and not engine.state.game_over:
                        engine.play_turn()
                    elif event.key == pygame.K_s:
                        save_manager.save_game("autosave.json", engine)
                        engine.state.messages.append("Game saved")
                    elif event.key == pygame.K_l:
                        save_manager.load_into_engine("autosave.json", engine)
                        engine.state.messages.append("Game loaded")
                    elif event.key == pygame.K_e:
                        mode = "editor"
                    elif event.key == pygame.K_ESCAPE:
                        mode = "menu"
                elif mode == "editor":
                    if event.key == pygame.K_ESCAPE:
                        mode = "menu"
                    elif event.key == pygame.K_b:
                        BoardEditor(DATA / "boards" / "monopoly.json")
                    elif event.key == pygame.K_d:
                        DeckEditor(DATA / "decks" / "chance.json")
                    elif event.key == pygame.K_r:
                        RuleEditor(DATA / "rules" / "monopoly_rules.json")

        if mode == "menu":
            menu.draw(screen)
        elif mode == "game":
            game_screen.draw(screen)
        else:
            editor_ui.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
