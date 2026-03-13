import pygame

from save.save_manager import SaveManager
from ui.animation_manager import AnimationManager
from ui.asset_generator import draw_button
from ui.board_renderer import BoardRenderer
from ui.dice_view import draw_die
from ui.player_panel import draw_player_panel
from ui.popup_system import PopupSystem


class GameScreen:
    def __init__(self, screen, engine):
        self.screen = screen
        self.engine = engine
        self.clock = pygame.time.Clock()
        self.board_renderer = BoardRenderer(engine.board)
        self.anim = AnimationManager()
        self.popup = PopupSystem()
        self.engine.bus.subscribe("card_drawn", lambda card: self.popup.show_card(card))

    def run(self):
        running = True
        while running:
            w, h = self.screen.get_size()
            roll_btn = pygame.Rect(w - 250, h - 90, 105, 52)
            save_btn = pygame.Rect(w - 132, h - 90, 105, 52)
            load_btn = pygame.Rect(w - 250, h - 150, 223, 46)
            buy_btn = pygame.Rect(w - 250, h - 210, 223, 46)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "quit"
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return "menu"
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if roll_btn.collidepoint(e.pos):
                        self.engine.take_turn()
                    elif save_btn.collidepoint(e.pos):
                        SaveManager.save("boardgame_platform/saves/autosave.json", self.engine)
                    elif load_btn.collidepoint(e.pos):
                        SaveManager.load("boardgame_platform/saves/autosave.json", self.engine)
                    elif buy_btn.collidepoint(e.pos):
                        self.engine.buy_current_property()
            self.anim.update()
            self.popup.update()
            self.draw(roll_btn, save_btn, load_btn, buy_btn)
            pygame.display.flip()
            self.clock.tick(60)
        return "menu"

    def draw(self, roll_btn, save_btn, load_btn, buy_btn):
        w, h = self.screen.get_size()
        self.screen.fill((197, 205, 214))
        self.board_renderer.draw(self.screen, (30, 30, min(w - 340, h - 60), min(w - 340, h - 60)), self.engine)
        draw_player_panel(self.screen, pygame.Rect(w - 290, 30, 260, h - 270), self.engine.state.players, self.engine.state.current_turn)
        font = pygame.font.SysFont("arial", 20)
        d1, d2 = self.engine.state.last_roll
        draw_die(self.screen, pygame.Rect(w - 165, h - 265, 52, 52), d1)
        draw_die(self.screen, pygame.Rect(w - 101, h - 265, 52, 52), d2)
        draw_button(self.screen, buy_btn, "Buy Property", False, font)
        draw_button(self.screen, load_btn, "Load Save", False, font)
        draw_button(self.screen, roll_btn, "Roll", False, font)
        draw_button(self.screen, save_btn, "Save", False, font)
        y = h - 205
        for msg in self.engine.state.messages[-5:]:
            self.screen.blit(font.render(msg, True, (20, 20, 20)), (40, y))
            y += 30
        self.popup.draw(self.screen, w, h)
