import pygame


class PopupSystem:
    def __init__(self):
        self.message = ""
        self.timer = 0

    def show(self, message: str, frames: int = 180):
        self.message = message
        self.timer = frames

    def draw(self, screen, font):
        if self.timer <= 0:
            return
        self.timer -= 1
        w, h = screen.get_size()
        rect = pygame.Rect(w // 4, h // 3, w // 2, h // 4)
        pygame.draw.rect(screen, (40, 40, 40), rect, border_radius=10)
        pygame.draw.rect(screen, (220, 220, 220), rect, width=2, border_radius=10)
        rendered = font.render(self.message[:100], True, (255, 255, 255))
        screen.blit(rendered, (rect.x + 20, rect.y + rect.height // 2 - 10))
