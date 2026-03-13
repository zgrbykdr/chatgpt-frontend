import pygame


class DiceView:
    def draw(self, screen, dice, pos=(850, 100)):
        font = pygame.font.SysFont("arial", 28, bold=True)
        txt = font.render(f"Dice: {dice[0]} + {dice[1]}", True, (25, 25, 25))
        pygame.draw.rect(screen, (245, 245, 245), (*pos, 230, 50), border_radius=8)
        pygame.draw.rect(screen, (80, 80, 80), (*pos, 230, 50), width=2, border_radius=8)
        screen.blit(txt, (pos[0] + 15, pos[1] + 10))
