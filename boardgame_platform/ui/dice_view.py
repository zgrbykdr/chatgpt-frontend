import pygame


def draw_die(surface, rect, value):
    pygame.draw.rect(surface, (250, 250, 250), rect, border_radius=8)
    pygame.draw.rect(surface, (50, 50, 50), rect, width=2, border_radius=8)
    font = pygame.font.SysFont("arial", 24, bold=True)
    txt = font.render(str(value), True, (30, 30, 30))
    surface.blit(txt, txt.get_rect(center=rect.center))
