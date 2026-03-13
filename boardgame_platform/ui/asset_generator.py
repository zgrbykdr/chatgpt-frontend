import pygame


def draw_panel(surface, rect, color, radius=12):
    pygame.draw.rect(surface, (0, 0, 0, 70), rect.move(3, 4), border_radius=radius)
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, (255, 255, 255), rect.inflate(-8, -8), width=1, border_radius=radius)


def draw_button(surface, rect, text, hover, font):
    color = (95, 126, 165) if hover else (72, 98, 132)
    draw_panel(surface, rect, color, radius=10)
    label = font.render(text, True, (245, 245, 245))
    surface.blit(label, label.get_rect(center=rect.center))
