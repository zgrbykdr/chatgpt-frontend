import pygame


class EditorScreen:
    def draw(self, screen):
        screen.fill((30, 30, 30))
        font = pygame.font.SysFont("arial", 28)
        lines = [
            "Editor Hub", "B: Board Editor", "D: Deck Editor", "R: Rule Editor", "ESC: Back",
        ]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, (230, 230, 230)), (60, 80 + i * 40))
