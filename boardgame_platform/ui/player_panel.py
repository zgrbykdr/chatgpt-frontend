import pygame
from ui.asset_generator import draw_panel


def draw_player_panel(surface, rect, players, current_idx):
    draw_panel(surface, rect, (230, 236, 244), 14)
    title = pygame.font.SysFont("arial", 24, bold=True).render("Players", True, (24, 24, 24))
    surface.blit(title, (rect.x + 16, rect.y + 12))
    font = pygame.font.SysFont("arial", 18)
    y = rect.y + 52
    for i, p in enumerate(players):
        row = pygame.Rect(rect.x + 10, y, rect.w - 20, 74)
        c = (251, 248, 232) if i == current_idx else (243, 245, 250)
        draw_panel(surface, row, c, 10)
        pygame.draw.circle(surface, tuple(p.color), (row.x + 24, row.y + 24), 12)
        surface.blit(font.render(p.name, True, (25, 25, 25)), (row.x + 42, row.y + 10))
        surface.blit(font.render(f"${p.money}", True, (25, 25, 25)), (row.x + 42, row.y + 35))
        surface.blit(font.render(f"Pos {p.position}", True, (65, 65, 65)), (row.right - 80, row.y + 10))
        if p.in_jail:
            surface.blit(font.render("JAIL", True, (160, 70, 60)), (row.right - 78, row.y + 38))
        y += 82
