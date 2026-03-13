import pygame

from core.game_engine import GameEngine
from players.player_model import Player
from ui.asset_generator import draw_button
from ui.editor_screen import run_editor_shell
from ui.game_screen import GameScreen


def create_default_engine():
    engine = GameEngine(
        board_path="boardgame_platform/data/boards/monopoly.json",
        deck_paths={
            "chance": "boardgame_platform/data/decks/chance.json",
            "community_chest": "boardgame_platform/data/decks/community_chest.json",
        },
        rules_path="boardgame_platform/data/rules/monopoly_rules.json",
    )
    players = [
        Player(0, "Player 1", "Top Hat", [200, 80, 80], 1500),
        Player(1, "Player 2", "Car", [80, 130, 210], 1500),
        Player(2, "Player 3", "Dog", [90, 170, 110], 1500),
        Player(3, "Player 4", "Ship", [190, 150, 70], 1500),
    ]
    engine.add_players(players)
    return engine


def run_app():
    pygame.init()
    screen = pygame.display.set_mode((1440, 900), pygame.RESIZABLE)
    pygame.display.set_caption("Board Game Platform")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 28, bold=True)
    small = pygame.font.SysFont("arial", 24)

    running = True
    while running:
        w, h = screen.get_size()
        buttons = {
            "play": pygame.Rect(w // 2 - 180, 240, 360, 56),
            "custom": pygame.Rect(w // 2 - 180, 310, 360, 56),
            "load": pygame.Rect(w // 2 - 180, 380, 360, 56),
            "board_editor": pygame.Rect(w // 2 - 180, 450, 360, 56),
            "deck_editor": pygame.Rect(w // 2 - 180, 520, 360, 56),
            "exit": pygame.Rect(w // 2 - 180, 590, 360, 56),
        }
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if buttons["play"].collidepoint(e.pos):
                    GameScreen(screen, create_default_engine()).run()
                elif buttons["custom"].collidepoint(e.pos):
                    GameScreen(screen, create_default_engine()).run()
                elif buttons["load"].collidepoint(e.pos):
                    eng = create_default_engine()
                    from save.save_manager import SaveManager
                    try:
                        SaveManager.load("boardgame_platform/saves/autosave.json", eng)
                    except FileNotFoundError:
                        pass
                    GameScreen(screen, eng).run()
                elif buttons["board_editor"].collidepoint(e.pos) or buttons["deck_editor"].collidepoint(e.pos):
                    if run_editor_shell(screen, clock) == "quit":
                        running = False
                elif buttons["exit"].collidepoint(e.pos):
                    running = False

        screen.fill((26, 38, 52))
        title = font.render("Monopoly Board Game Platform", True, (245, 245, 245))
        screen.blit(title, title.get_rect(center=(w // 2, 140)))
        draw_button(screen, buttons["play"], "Play Monopoly", False, small)
        draw_button(screen, buttons["custom"], "New Custom Game", False, small)
        draw_button(screen, buttons["load"], "Load Game", False, small)
        draw_button(screen, buttons["board_editor"], "Board Editor", False, small)
        draw_button(screen, buttons["deck_editor"], "Deck / Rule Editors", False, small)
        draw_button(screen, buttons["exit"], "Exit", False, small)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
