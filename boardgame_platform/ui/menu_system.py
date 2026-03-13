import pygame


class MenuSystem:
    def __init__(self):
        self.options = ["New Monopoly Game", "Load Game", "Editor", "Quit"]
        self.selected = 0

    def draw(self, screen):
        screen.fill((35, 55, 80))
        title = pygame.font.SysFont("arial", 52, bold=True).render("Board Game Platform", True, (255, 255, 255))
        screen.blit(title, (120, 90))
        font = pygame.font.SysFont("arial", 32)
        for i, option in enumerate(self.options):
            color = (255, 230, 120) if i == self.selected else (255, 255, 255)
            screen.blit(font.render(option, True, color), (160, 220 + i * 55))
