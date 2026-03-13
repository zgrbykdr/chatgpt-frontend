import pygame
from ui.theme_manager import PALETTE, GROUP_COLORS
from players.token_manager import draw_token


class BoardRenderer:
    def __init__(self, board):
        self.board = board

    def square_rects(self, area):
        x, y, w, h = area
        tile = int(min(w, h) * 0.12)
        rects = []
        for i in range(11):
            rects.append(pygame.Rect(x + w - tile * (i + 1), y + h - tile, tile, tile))
        for i in range(1, 10):
            rects.append(pygame.Rect(x, y + h - tile * (i + 1), tile, tile))
        for i in range(11):
            rects.append(pygame.Rect(x + tile * i, y, tile, tile))
        for i in range(1, 10):
            rects.append(pygame.Rect(x + w - tile, y + tile * i, tile, tile))
        return rects

    def draw(self, surface, area, engine):
        rects = self.square_rects(area)
        pygame.draw.rect(surface, PALETTE["bg"], area, border_radius=10)
        pygame.draw.rect(surface, PALETTE["line"], area, width=3, border_radius=10)
        font = pygame.font.SysFont("arial", 13, bold=True)
        for i, sq in enumerate(engine.board.squares):
            r = rects[i]
            pygame.draw.rect(surface, (248, 242, 226), r)
            pygame.draw.rect(surface, (40, 40, 40), r, width=1)
            if sq.group and sq.group in GROUP_COLORS:
                pygame.draw.rect(surface, GROUP_COLORS[sq.group], pygame.Rect(r.x, r.y, r.w, 12))
            elif sq.type in {"chance", "card_draw"}:
                pygame.draw.rect(surface, PALETTE["card"], pygame.Rect(r.x, r.y, r.w, 12))
            elif sq.type == "tax":
                pygame.draw.rect(surface, PALETTE["tax"], pygame.Rect(r.x, r.y, r.w, 12))
            label = font.render(sq.name[:14], True, (20, 20, 20))
            surface.blit(label, (r.x + 4, r.y + 16))
            if sq.id in engine.state.property_state:
                ps = engine.state.property_state[sq.id]
                if ps.owner_id is not None:
                    owner = next(p for p in engine.state.players if p.player_id == ps.owner_id)
                    pygame.draw.circle(surface, owner.color, (r.right - 10, r.bottom - 10), 6)
                for h in range(ps.houses):
                    pygame.draw.rect(surface, (60, 155, 70), pygame.Rect(r.x + 4 + h * 9, r.bottom - 10, 7, 6))
        for p in engine.state.players:
            rr = rects[p.position]
            draw_token(surface, (rr.centerx, rr.centery), tuple(p.color), p.token, 11)
