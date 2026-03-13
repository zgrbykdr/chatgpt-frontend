import pygame


class PlayerPanel:
    def draw(self, screen, players, current_idx: int, start=(820, 180)):
        font = pygame.font.SysFont("arial", 22)
        x, y = start
        for i, p in enumerate(players):
            rect = pygame.Rect(x, y + i * 85, 350, 75)
            color = (245, 245, 220) if i == current_idx else (230, 230, 230)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, (90, 90, 90), rect, width=2, border_radius=8)
            pygame.draw.circle(screen, p.color, (rect.x + 20, rect.y + 20), 8)
            screen.blit(font.render(p.name, True, (0, 0, 0)), (rect.x + 35, rect.y + 8))
            screen.blit(font.render(f"$ {p.money}", True, (0, 90, 0)), (rect.x + 35, rect.y + 35))
