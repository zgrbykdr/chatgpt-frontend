from __future__ import annotations

import pygame

from ui.animation_manager import AnimationManager
from ui.board_renderer import BoardRenderer
from ui.dice_view import DiceView
from ui.player_panel import PlayerPanel
from ui.popup_system import PopupSystem


class GameScreen:
    def __init__(self, engine):
        self.engine = engine
        self.board_renderer = BoardRenderer()
        self.player_panel = PlayerPanel()
        self.dice_view = DiceView()
        self.popups = PopupSystem()
        self.animations = AnimationManager()

    def draw(self, screen):
        screen.fill((210, 220, 235))
        self.board_renderer.draw(screen, self.engine.state.board, self.engine.state.players, self.engine.state.property_state)
        self.player_panel.draw(screen, self.engine.state.players, self.engine.state.current_player_index)
        self.dice_view.draw(screen, self.engine.turn_manager.last_roll)
        if self.engine.state.messages:
            self.popups.show(self.engine.state.messages[-1], frames=120)
        self.popups.draw(screen, pygame.font.SysFont("arial", 22))

        hint_font = pygame.font.SysFont("arial", 22)
        screen.blit(hint_font.render("SPACE: Roll / S: Save / L: Load / E: Editor / ESC: Menu", True, (15, 15, 15)), (20, 790))
        self.animations.tick()
