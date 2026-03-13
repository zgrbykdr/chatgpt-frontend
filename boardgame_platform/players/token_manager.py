import pygame


def draw_token(surface: pygame.Surface, center: tuple[int, int], color: tuple[int, int, int], icon: str, radius: int = 14) -> None:
    shadow = (center[0] + 2, center[1] + 3)
    pygame.draw.circle(surface, (0, 0, 0, 80), shadow, radius)
    pygame.draw.circle(surface, color, center, radius)
    pygame.draw.circle(surface, (250, 250, 250), (center[0] - 4, center[1] - 4), radius // 3)
    font = pygame.font.SysFont("arial", 14, bold=True)
    text = font.render(icon[:1].upper(), True, (20, 20, 20))
    surface.blit(text, text.get_rect(center=center))
