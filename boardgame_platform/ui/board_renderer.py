from __future__ import annotations

import math
import pygame


class BoardRenderer:
    def __init__(self):
        self.board_rect = pygame.Rect(20, 20, 760, 760)

    def square_position(self, index: int, size: int) -> tuple[int, int]:
        perimeter = size
        side = perimeter // 4
        step = self.board_rect.width // side
        if index < side:
            return self.board_rect.right - (index + 1) * step + step // 2, self.board_rect.bottom - step // 2
        if index < side * 2:
            k = index - side
            return self.board_rect.left + step // 2, self.board_rect.bottom - (k + 1) * step + step // 2
        if index < side * 3:
            k = index - side * 2
            return self.board_rect.left + (k + 1) * step - step // 2, self.board_rect.top + step // 2
        k = index - side * 3
        return self.board_rect.right - step // 2, self.board_rect.top + (k + 1) * step - step // 2

    def draw(self, screen, board, players, property_state):
        pygame.draw.rect(screen, (196, 235, 204), self.board_rect)
        pygame.draw.rect(screen, (35, 35, 35), self.board_rect, width=3)
        side = board.size // 4
        step = self.board_rect.width // side

        for i, square in enumerate(board.squares):
            x, y = self.square_position(i, board.size)
            cell = pygame.Rect(x - step // 2, y - step // 2, step, step)
            pygame.draw.rect(screen, (255, 255, 255), cell, width=1)
            if square.type == "property" and square.group:
                group_colors = {
                    "brown": (139, 69, 19), "light_blue": (135, 206, 235), "pink": (255, 105, 180),
                    "orange": (255, 165, 0), "red": (220, 20, 60), "yellow": (255, 215, 0),
                    "green": (50, 205, 50), "dark_blue": (65, 105, 225),
                }
                pygame.draw.rect(screen, group_colors.get(square.group, (120, 120, 120)), (cell.x, cell.y, cell.w, 8))
            font = pygame.font.SysFont("arial", 11)
            label = font.render(square.name[:13], True, (20, 20, 20))
            screen.blit(label, (cell.x + 2, cell.y + 10))

            state = property_state.get(square.id)
            if state and state.owner is not None:
                pygame.draw.circle(screen, players[state.owner].color, (cell.right - 8, cell.top + 8), 5)

        for p in players:
            tx, ty = self.square_position(p.position, board.size)
            pygame.draw.circle(screen, p.color, (tx, ty), 10)
