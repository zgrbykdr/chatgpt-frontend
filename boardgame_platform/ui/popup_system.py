import pygame
from ui.asset_generator import draw_panel


class PopupSystem:
    def __init__(self):
        self.card = None
        self.timer = 0

    def show_card(self, card):
        self.card = card
        self.timer = 240

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.card = None

    def draw(self, surface, w, h):
        if not self.card:
            return
        rect = pygame.Rect(w // 2 - 190, h // 2 - 130, 380, 260)
        draw_panel(surface, rect, (247, 247, 251), 14)
        f1 = pygame.font.SysFont("arial", 26, bold=True)
        f2 = pygame.font.SysFont("arial", 20)
        surface.blit(f1.render(self.card.get("title", "Card"), True, (20, 20, 20)), (rect.x + 20, rect.y + 20))
        lines = self.wrap(self.card.get("description", ""), f2, rect.w - 40)
        y = rect.y + 70
        for line in lines:
            surface.blit(f2.render(line, True, (40, 40, 40)), (rect.x + 20, y))
            y += 26

    @staticmethod
    def wrap(text, font, maxw):
        words, lines, line = text.split(), [], ""
        for w in words:
            test = (line + " " + w).strip()
            if font.size(test)[0] <= maxw:
                line = test
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines
