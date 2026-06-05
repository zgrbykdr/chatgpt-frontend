import pygame
import json
import os
import math
import random
import time
import uuid
from datetime import datetime
from copy import deepcopy

APP_TITLE = "Box Board Game Studio"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAMES_DIR = os.path.join(BASE_DIR, "games")
SAVES_DIR = os.path.join(BASE_DIR, "saves")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TEMPLATES_DIR = os.path.join(BASE_DIR, "default_templates")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
for folder in (GAMES_DIR, SAVES_DIR, ASSETS_DIR, TEMPLATES_DIR):
    os.makedirs(folder, exist_ok=True)

BOARD_TYPES = ["Classic rectangle", "Circle", "Grid path"]
SQUARE_TYPES = ["start", "property", "railroad", "utility", "tax", "card", "jail", "go_to_jail", "free", "reward", "penalty", "custom"]
ACTION_TYPES = [
    "none", "buy", "pay_rent", "draw_card", "gain_money", "lose_money", "move_forward", "move_backward",
    "go_to_square", "go_to_jail", "wait_turns", "reroll", "transfer_to_player", "collect_from_all",
    "pay_all", "develop_property", "add_house_hotel", "mortgage", "auction", "message", "timer",
    "next_turn_action"
]
ICON_NAMES = ["Token", "Car", "Hat", "Dog", "Ship", "Shoe", "Star", "Gem"]
COLORS = {
    "bg": (18, 24, 38), "panel": (30, 41, 59), "panel2": (44, 59, 84), "text": (236, 244, 255),
    "muted": (148, 163, 184), "accent": (56, 189, 248), "accent2": (168, 85, 247), "good": (34, 197, 94),
    "warn": (245, 158, 11), "bad": (239, 68, 68), "white": (255, 255, 255), "dark_text": (15, 23, 42)
}
PLAYER_COLORS = [(239, 68, 68), (59, 130, 246), (34, 197, 94), (234, 179, 8), (168, 85, 247), (236, 72, 153)]
GROUP_COLORS = {
    "Brown": (114, 73, 56), "Light Blue": (125, 211, 252), "Pink": (244, 114, 182), "Orange": (251, 146, 60),
    "Red": (239, 68, 68), "Yellow": (250, 204, 21), "Green": (34, 197, 94), "Blue": (37, 99, 235),
    "Railroad": (100, 116, 139), "Utility": (20, 184, 166), "Special": (168, 85, 247)
}


def safe_filename(name):
    clean = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    return clean or "game"


def load_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return deepcopy(fallback)


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def default_settings():
    return {"theme": "dark", "resolution": [1280, 720], "volume": 0.65, "autosave": True}


def make_action(action_type="none", amount=0, target=None, message=""):
    return {"type": action_type, "amount": amount, "target": target, "message": message, "timer": {"mode": "none", "value": 0, "after_action": "none"}}


def make_square(i, name, square_type="property", price=0, rent=0, group="Special", action=None):
    return {
        "id": i, "name": name, "type": square_type, "price": price, "rent": rent, "color_group": group,
        "image": "", "icon": "", "description": "", "actions": [action or make_action("none")],
        "timer": {"enabled": False, "mode": "turns", "value": 0, "action": make_action("none")},
        "owner": None, "houses": 0, "hotel": False, "mortgaged": False
    }


def create_classic_template():
    names = [
        ("GO", "start", 0, 0, "Special"), ("Mediterranean Avenue", "property", 60, 2, "Brown"), ("Community Chest", "card", 0, 0, "Special"),
        ("Baltic Avenue", "property", 60, 4, "Brown"), ("Income Tax", "tax", 0, 200, "Special"), ("Reading Railroad", "railroad", 200, 25, "Railroad"),
        ("Oriental Avenue", "property", 100, 6, "Light Blue"), ("Chance", "card", 0, 0, "Special"), ("Vermont Avenue", "property", 100, 6, "Light Blue"),
        ("Connecticut Avenue", "property", 120, 8, "Light Blue"), ("Jail / Visiting", "jail", 0, 0, "Special"), ("St. Charles Place", "property", 140, 10, "Pink"),
        ("Electric Company", "utility", 150, 20, "Utility"), ("States Avenue", "property", 140, 10, "Pink"), ("Virginia Avenue", "property", 160, 12, "Pink"),
        ("Pennsylvania Railroad", "railroad", 200, 25, "Railroad"), ("St. James Place", "property", 180, 14, "Orange"), ("Community Chest", "card", 0, 0, "Special"),
        ("Tennessee Avenue", "property", 180, 14, "Orange"), ("New York Avenue", "property", 200, 16, "Orange"), ("Free Parking", "free", 0, 0, "Special"),
        ("Kentucky Avenue", "property", 220, 18, "Red"), ("Chance", "card", 0, 0, "Special"), ("Indiana Avenue", "property", 220, 18, "Red"),
        ("Illinois Avenue", "property", 240, 20, "Red"), ("B. & O. Railroad", "railroad", 200, 25, "Railroad"), ("Atlantic Avenue", "property", 260, 22, "Yellow"),
        ("Ventnor Avenue", "property", 260, 22, "Yellow"), ("Water Works", "utility", 150, 20, "Utility"), ("Marvin Gardens", "property", 280, 24, "Yellow"),
        ("Go To Jail", "go_to_jail", 0, 0, "Special"), ("Pacific Avenue", "property", 300, 26, "Green"), ("North Carolina Avenue", "property", 300, 26, "Green"),
        ("Community Chest", "card", 0, 0, "Special"), ("Pennsylvania Avenue", "property", 320, 28, "Green"), ("Short Line", "railroad", 200, 25, "Railroad"),
        ("Chance", "card", 0, 0, "Special"), ("Park Place", "property", 350, 35, "Blue"), ("Luxury Tax", "tax", 0, 100, "Special"),
        ("Boardwalk", "property", 400, 50, "Blue")
    ]

    property_specs = {
        "Mediterranean Avenue": (60, 2, 4, 10, 30, 90, 160, 250, 50, 30),
        "Baltic Avenue": (60, 4, 8, 20, 60, 180, 320, 450, 50, 30),
        "Oriental Avenue": (100, 6, 12, 30, 90, 270, 400, 550, 50, 50),
        "Vermont Avenue": (100, 6, 12, 30, 90, 270, 400, 550, 50, 50),
        "Connecticut Avenue": (120, 8, 16, 40, 100, 300, 450, 600, 50, 60),
        "St. Charles Place": (140, 10, 20, 50, 150, 450, 625, 750, 100, 70),
        "States Avenue": (140, 10, 20, 50, 150, 450, 625, 750, 100, 70),
        "Virginia Avenue": (160, 12, 24, 60, 180, 500, 700, 900, 100, 80),
        "St. James Place": (180, 14, 28, 70, 200, 550, 750, 950, 100, 90),
        "Tennessee Avenue": (180, 14, 28, 70, 200, 550, 750, 950, 100, 90),
        "New York Avenue": (200, 16, 32, 80, 220, 600, 800, 1000, 100, 100),
        "Kentucky Avenue": (220, 18, 36, 90, 250, 700, 875, 1050, 150, 110),
        "Indiana Avenue": (220, 18, 36, 90, 250, 700, 875, 1050, 150, 110),
        "Illinois Avenue": (240, 20, 40, 100, 300, 750, 925, 1100, 150, 120),
        "Atlantic Avenue": (260, 22, 44, 110, 330, 800, 975, 1150, 150, 130),
        "Ventnor Avenue": (260, 22, 44, 110, 330, 800, 975, 1150, 150, 130),
        "Marvin Gardens": (280, 24, 48, 120, 360, 850, 1025, 1200, 150, 140),
        "Pacific Avenue": (300, 26, 52, 130, 390, 900, 1100, 1275, 200, 150),
        "North Carolina Avenue": (300, 26, 52, 130, 390, 900, 1100, 1275, 200, 150),
        "Pennsylvania Avenue": (320, 28, 56, 150, 450, 1000, 1200, 1400, 200, 160),
        "Park Place": (350, 35, 70, 175, 500, 1100, 1300, 1500, 200, 175),
        "Boardwalk": (400, 50, 100, 200, 600, 1400, 1700, 2000, 200, 200),
    }
    squares = []
    for i, (n, t, p, r, g) in enumerate(names):
        action = make_action("none")
        if t in ("property", "railroad", "utility"):
            action = make_action("buy")
        elif t == "tax":
            action = make_action("lose_money", r, message=f"Pay {r} tax")
        elif t == "card":
            deck = "Chance" if n == "Chance" else "Community Chest"
            action = make_action("draw_card", target=deck)
        elif t == "go_to_jail":
            action = make_action("go_to_jail")
        sq = make_square(i, n, t, p, r, g, action)
        if t == "property" and n in property_specs:
            price, rent_base, rent_full_set, r1, r2, r3, r4, hotel, house_cost, mortgage = property_specs[n]
            sq.update({"price": price, "rent": rent_base, "rent_base": rent_base, "rent_full_set": rent_full_set, "rent_1_house": r1, "rent_2_house": r2, "rent_3_house": r3, "rent_4_house": r4, "rent_hotel": hotel, "house_cost": house_cost, "mortgage_value": mortgage})
        elif t == "railroad":
            sq.update({"price": 200, "rent": 25, "rent_base": 25, "rent_full_set": 200, "mortgage_value": 100, "railroad_rents": [25, 50, 100, 200]})
        elif t == "utility":
            sq.update({"price": 150, "rent": 0, "rent_base": 0, "rent_full_set": 0, "mortgage_value": 75, "utility_multipliers": [4, 10]})
        squares.append(sq)
    chance = [
        ("Advance to Start", "advance_start", 0, None, "Move to Start and collect salary."),
        ("Advance to Illinois Avenue", "go_to_square", 0, 24, "Move to Illinois Avenue."),
        ("Advance to St. Charles Place", "go_to_square", 0, 11, "Move to St. Charles Place."),
        ("Advance to nearest Utility", "nearest_utility", 0, None, "Move to the nearest utility; rent uses dice multiplier."),
        ("Advance to nearest Railroad", "nearest_railroad", 0, None, "Move to the nearest railroad and pay railroad rent if owned."),
        ("Bank pays dividend", "gain_money", 50, None, "Gain 50."),
        ("Get Out of Jail Free", "jail_card", 0, None, "Keep this card until used."),
        ("Go Back 3 Spaces", "move_backward", 3, None, "Move back 3 spaces."),
        ("Go to Jail", "go_to_jail", 0, None, "Move directly to Jail."),
        ("General repairs", "repair_fee", 25, None, "Pay 25 per house and 100 per hotel."),
        ("Speeding fine", "lose_money", 15, None, "Pay 15."),
        ("Chairman elected", "pay_all", 50, None, "Pay every player 50."),
        ("Advance to Boardwalk", "go_to_square", 0, 39, "Move to Boardwalk."),
    ]
    chest = [
        ("Advance to Start", "advance_start", 0, None, "Move to Start and collect salary."),
        ("Bank error in your favor", "gain_money", 200, None, "Collect 200."),
        ("Doctor fee", "lose_money", 50, None, "Pay 50."),
        ("Get Out of Jail Free", "jail_card", 0, None, "Keep this card until used."),
        ("Go to Jail", "go_to_jail", 0, None, "Move directly to Jail."),
        ("Holiday fund matures", "gain_money", 100, None, "Collect 100."),
        ("Income tax refund", "gain_money", 20, None, "Collect 20."),
        ("Life insurance matures", "gain_money", 100, None, "Collect 100."),
        ("Pay hospital fees", "lose_money", 100, None, "Pay 100."),
        ("Pay school fees", "lose_money", 50, None, "Pay 50."),
        ("Receive consultancy fee", "gain_money", 25, None, "Collect 25."),
        ("Street repairs", "repair_fee", 40, None, "Pay 40 per house and 115 per hotel."),
        ("Collect from every player", "collect_from_all", 10, None, "Each player pays you 10."),
    ]
    def cards(items):
        result=[]
        for n, a, amt, target, d in items:
            action = make_action(a, amt, target=target)
            result.append({"id": str(uuid.uuid4()), "name": n, "description": d, "image": "", "return_to_deck": a != "jail_card", "single_use": a == "jail_card", "holdable": a == "jail_card", "tradable": a == "jail_card", "action": action})
        random.shuffle(result)
        return result
    game = {
        "metadata": {"id": "classic_template", "name": "Classic Property Trading Game Template", "created_at": datetime.now().isoformat(timespec="seconds"), "updated_at": datetime.now().isoformat(timespec="seconds"), "version": 1},
        "settings": {"min_players": 2, "max_players": 6, "starting_money": 1500, "board_layout": "Monopoly style square", "board_square_count": 40},
        "rules": {
            "pass_start_money_enabled": True, "pass_start_money": 200, "exact_start_bonus_enabled": True, "exact_start_bonus": 200,
            "property_purchase_enabled": True, "auction_enabled": True, "auction_unbought_property": True, "rent_enabled": True,
            "houses_hotels_enabled": True, "mortgage_enabled": True, "trade_enabled": True, "debt_enabled": True, "debt_interest_enabled": True,
            "debt_due_turns": 5, "debt_default": "transfer_collateral_or_penalty", "jail_enabled": True, "jail_fee": 50, "jail_turns": 3,
            "double_reroll_enabled": True, "three_doubles_jail": True, "free_parking_pool_enabled": False, "taxes_to": "bank",
            "end_condition": "last_player_standing", "turn_limit": 60, "wealth_target": 5000, "property_target": 12
        },
        "board": squares,
        "card_decks": {"Chance": cards(chance), "Community Chest": cards(chest), "Event Cards": [], "Penalty Cards": [], "Reward Cards": [], "Custom Deck": []},
        "player_settings": {"icons": ICON_NAMES, "colors": PLAYER_COLORS},
        "assets": {"default_icon": "", "background": ""},
        "trade_rules": {"money": True, "properties": True, "cards": True, "debt": True},
        "debt_rules": {"allow_loans": True, "default_interest": 10, "default_due_turns": 5, "default_penalty": "pay_extra_or_wait"},
        "timers": []
    }
    return game


class UI:
    def __init__(self):
        pygame.font.init()
        self.fonts = {s: pygame.font.SysFont("arial", s) for s in (14, 16, 18, 20, 24, 30, 38, 48)}

    def text(self, surf, txt, pos, size=18, color=None, center=False, max_width=None):
        color = color or COLORS["text"]
        font = self.fonts.get(size) or pygame.font.SysFont("arial", size)
        s = str(txt)
        if max_width and font.size(s)[0] > max_width:
            while s and font.size(s + "...")[0] > max_width:
                s = s[:-1]
            s += "..."
        img = font.render(s, True, color)
        rect = img.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        surf.blit(img, rect)
        return rect

    def wrap(self, surf, txt, rect, size=16, color=None, line_gap=4):
        words = str(txt).split()
        line = ""
        y = rect.y
        font = self.fonts[size]
        for w in words:
            test = (line + " " + w).strip()
            if font.size(test)[0] <= rect.w:
                line = test
            else:
                if line:
                    self.text(surf, line, (rect.x, y), size, color)
                    y += size + line_gap
                line = w
        if line and y < rect.bottom:
            self.text(surf, line, (rect.x, y), size, color)

    def rounded(self, surf, rect, color, radius=14, border=None, border_width=1, shadow=True):
        r = pygame.Rect(rect)
        if shadow:
            sh = r.copy(); sh.move_ip(5, 8)
            shadow_surf = pygame.Surface((sh.w + 12, sh.h + 12), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 95), (6, 6, sh.w, sh.h), border_radius=radius)
            surf.blit(shadow_surf, (sh.x - 6, sh.y - 6))
        pygame.draw.rect(surf, color, r, border_radius=radius)
        if border:
            pygame.draw.rect(surf, border, r, border_width, border_radius=radius)

    def glass(self, surf, rect, color=(30, 41, 59), alpha=188, radius=20, border=(56, 189, 248), border_alpha=95, shadow=True):
        r = pygame.Rect(rect)
        if shadow:
            sh = pygame.Surface((r.w + 18, r.h + 18), pygame.SRCALPHA)
            pygame.draw.rect(sh, (0, 0, 0, 105), (9, 9, r.w, r.h), border_radius=radius)
            surf.blit(sh, (r.x - 9, r.y - 9))
        panel = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*color, alpha), (0, 0, r.w, r.h), border_radius=radius)
        pygame.draw.rect(panel, (255, 255, 255, 28), (1, 1, r.w-2, max(18, r.h//4)), border_radius=radius)
        if border:
            border_rgb = border[:3]
            pygame.draw.rect(panel, (*border_rgb, border_alpha), (0, 0, r.w, r.h), 1, border_radius=radius)
        surf.blit(panel, r.topleft)

    def neon_line(self, surf, start, end, color=None, width=2):
        color = color or COLORS["accent"]
        pygame.draw.line(surf, (*color[:3],) if len(color) == 3 else color, start, end, width)
        pygame.draw.line(surf, color[:3], start, end, max(1, width-1))

    def icon(self, surf, name, center, size=20, color=None):
        color = color or COLORS["accent"]
        x, y = int(center[0]), int(center[1]); s = int(size)
        if name == "card":
            rr = pygame.Rect(0, 0, s, int(s*1.25)); rr.center = (x, y)
            pygame.draw.rect(surf, (248,250,252), rr, border_radius=4)
            pygame.draw.rect(surf, color, rr, 2, border_radius=4)
            pygame.draw.circle(surf, color, (rr.centerx, rr.centery), max(2, s//5))
        elif name == "tax":
            self.text(surf, "$", (x, y-1), max(16, s), color, True)
        elif name == "railroad":
            pygame.draw.rect(surf, color, (x-s//2, y-s//5, s, s//3), border_radius=3)
            pygame.draw.circle(surf, COLORS["dark_text"], (x-s//3, y+s//5), max(2, s//7))
            pygame.draw.circle(surf, COLORS["dark_text"], (x+s//3, y+s//5), max(2, s//7))
        elif name == "utility":
            pygame.draw.polygon(surf, color, [(x, y-s//2), (x-s//5, y), (x+s//8, y), (x-s//8, y+s//2), (x+s//3, y-s//8), (x, y-s//8)])
        elif name == "jail":
            pygame.draw.rect(surf, color, (x-s//2, y-s//2, s, s), 2, border_radius=3)
            for off in (-s//4, 0, s//4): pygame.draw.line(surf, color, (x+off, y-s//2), (x+off, y+s//2), 2)
        elif name == "go":
            pygame.draw.circle(surf, color, (x, y), s//2)
            self.text(surf, "GO", (x, y), max(10, s//2), COLORS["dark_text"], True)
        else:
            pygame.draw.circle(surf, color, (x, y), s//2)


class Button:
    def __init__(self, rect, label, action=None, kind="primary"):
        self.rect = pygame.Rect(rect); self.label = label; self.action = action; self.kind = kind; self.enabled = True; self.hover_t = 0.0
    def draw(self, surf, ui, mouse):
        hover = self.rect.collidepoint(mouse) and self.enabled
        self.hover_t += (1.0 if hover else -1.0) * 0.18
        self.hover_t = max(0.0, min(1.0, self.hover_t))
        base = COLORS["accent"] if self.kind == "primary" else COLORS["panel2"]
        if self.kind == "danger": base = COLORS["bad"]
        if self.kind == "good": base = COLORS["good"]
        if self.kind == "roll": base = (14, 165, 233)
        if not self.enabled: base = (55, 65, 81)
        lift = int(18 * self.hover_t)
        color = tuple(min(255, c + lift) for c in base)
        r = self.rect.copy(); r.y -= int(2*self.hover_t)
        if hover and self.enabled:
            glow = pygame.Surface((r.w+18, r.h+18), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*COLORS["accent"], 70), (9,9,r.w,r.h), border_radius=15)
            surf.blit(glow, (r.x-9, r.y-9))
        ui.rounded(surf, r, color, 14, border=COLORS["accent"] if hover else (255,255,255,45), shadow=True)
        txt_color = COLORS["dark_text"] if self.kind in ("primary", "good", "roll") and self.enabled else COLORS["text"]
        ui.text(surf, self.label, r.center, 17 if self.rect.w < 120 else 18, txt_color, center=True, max_width=r.w-14)
    def click(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


class InputBox:
    def __init__(self, rect, text="", numeric=False):
        self.rect = pygame.Rect(rect); self.text = str(text); self.numeric = numeric; self.active = False
    def handle(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(e.pos)
        if e.type == pygame.KEYDOWN and self.active:
            if e.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif e.key == pygame.K_RETURN:
                self.active = False
            else:
                ch = e.unicode
                if ch and (not self.numeric or ch.isdigit()):
                    self.text += ch
    def value(self, default=0):
        if self.numeric:
            try: return int(self.text)
            except ValueError: return default
        return self.text
    def draw(self, surf, ui):
        color = COLORS["panel2"] if not self.active else (51, 65, 85)
        ui.rounded(surf, self.rect, color, 10, border=COLORS["accent"] if self.active else (71, 85, 105), shadow=False)
        ui.text(surf, self.text, (self.rect.x+10, self.rect.y+9), 18, COLORS["text"], max_width=self.rect.w-20)


class Toggle:
    def __init__(self, rect, value=False): self.rect = pygame.Rect(rect); self.value = bool(value)
    def handle(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos): self.value = not self.value
    def draw(self, surf, ui):
        ui.rounded(surf, self.rect, COLORS["good"] if self.value else (71,85,105), self.rect.h//2, shadow=False)
        knob = pygame.Rect(0,0,self.rect.h-6,self.rect.h-6); knob.centery = self.rect.centery; knob.x = self.rect.right-self.rect.h+3 if self.value else self.rect.x+3
        pygame.draw.ellipse(surf, COLORS["white"], knob)


class App:
    def __init__(self):
        self.settings = load_json(SETTINGS_PATH, default_settings())
        save_json(SETTINGS_PATH, self.settings)
        pygame.init()
        self.screen = pygame.display.set_mode(tuple(self.settings.get("resolution", [1280,720])), pygame.RESIZABLE)
        pygame.display.set_caption(APP_TITLE)
        self.clock = pygame.time.Clock(); self.ui = UI(); self.running = True
        self.scene = "main_menu"; self.message = ""; self.message_until = 0
        self.buttons = []; self.inputs = []; self.toggles = []
        self.selected_game_path = None; self.games_cache = []
        self.edit_game = None; self.edit_path = None; self.editor_tab = "Board"; self.selected_square = 0; self.selected_card_deck = "Chance"; self.selected_card = 0
        self.play_state = None; self.anim = None; self.popup = None; self.dark = self.settings.get("theme", "dark") == "dark"
        self.modal = None; self.modal_buttons = []; self.modal_inputs = []; self.modal_toggles = []; self.modal_partner_index = 0
        self.editor_active = False; self.play_select_mode = "list"; self.board_hover_square = None; self.player_card_rects = []; self.detail_tab = "Properties"; self.detail_player_id = 0
        self.ensure_default_template(); self.build_main_menu()

    def ensure_default_template(self):
        path = os.path.join(GAMES_DIR, "Classic_Property_Trading_Game_Template.json")
        tpath = os.path.join(TEMPLATES_DIR, "Classic_Property_Trading_Game_Template.json")
        if not os.path.exists(path): save_json(path, create_classic_template())
        if not os.path.exists(tpath): save_json(tpath, create_classic_template())

    def notify(self, msg, seconds=3):
        self.message = msg; self.message_until = time.time() + seconds

    def list_games(self):
        games = []
        for folder in (GAMES_DIR,):
            for fn in sorted(os.listdir(folder)):
                if fn.endswith(".json"):
                    p = os.path.join(folder, fn)
                    try:
                        with open(p, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if data and "metadata" in data:
                            games.append((p, data))
                    except Exception as e:
                        self.notify(f"Broken JSON skipped: {fn} ({e})", 5)
                        continue
        self.games_cache = games
        return games

    def set_scene(self, scene):
        aliases = {"menu": "main_menu", "add": "create_game", "play": "gameplay"}
        scene = aliases.get(scene, scene)
        self.scene = scene; self.buttons = []; self.inputs = []; self.toggles = []
        getattr(self, "build_" + scene)()

    def panel_rect(self, width=760, height=560):
        w, h = self.screen.get_size()
        width = min(width, w - 80)
        height = min(height, h - 110)
        return pygame.Rect((w - width)//2, max(92, (h - height)//2 + 28), width, height)

    def build_main_menu(self):
        self.scene = "main_menu"; self.buttons = []; self.inputs = []; self.toggles = []; self.modal = None
        self.editor_active = False; self.play_select_mode = "list"; self.board_hover_square = None; self.player_card_rects = []; self.detail_tab = "Properties"; self.detail_player_id = 0
        w,h = self.screen.get_size(); panel = self.panel_rect(520, 470)
        bw,bh = min(340, panel.w-90), 54; x = panel.centerx-bw//2; y = panel.y+122
        items = [("Add New Game", lambda: self.set_scene("create_game")), ("Edit Existing Game", lambda: self.open_list("edit")), ("Play Game", lambda: self.open_list("play")), ("Settings", lambda: self.set_scene("settings")), ("Exit", self.quit)]
        for i,(lab,act) in enumerate(items): self.buttons.append(Button((x,y+i*66,bw,bh), lab, act, "primary" if i==0 else "secondary"))

    def build_menu(self):
        self.build_main_menu()

    def build_create_game(self):
        self.scene = "create_game"; self.buttons = []; self.inputs = []; self.toggles = []
        w,h = self.screen.get_size(); panel = self.panel_rect(780, 570)
        label_x = panel.x + max(34, panel.w//10)
        input_x = panel.x + panel.w//2 - 20
        input_w = min(330, panel.right - input_x - 48)
        row_y = panel.y + 98
        gap = 52
        self.add_layout_index = getattr(self, "add_layout_index", 0)
        self.inputs = [
            InputBox((input_x,row_y,input_w,38), "My Custom Board Game"),
            InputBox((input_x,row_y+gap,120,38), "2", True),
            InputBox((input_x,row_y+gap*2,120,38), "6", True),
            InputBox((input_x,row_y+gap*3,150,38), "1500", True),
            InputBox((input_x,row_y+gap*4,150,38), "28", True),
            InputBox((input_x,row_y+gap*5,150,38), "200", True),
        ]
        self.toggles = []
        button_y = panel.bottom - 72
        back_w, layout_w, create_w, gap_w = 140, 220, 180, 18
        start_x = panel.centerx - (back_w + layout_w + create_w + gap_w * 2)//2
        self.buttons = [
            Button((start_x,button_y,back_w,46), "Back", self.build_main_menu, "secondary"),
            Button((start_x+back_w+gap_w,button_y,layout_w,46), "Layout: " + BOARD_TYPES[self.add_layout_index].split()[0], self.cycle_add_layout, "secondary"),
            Button((start_x+back_w+gap_w+layout_w+gap_w,button_y,create_w,46), "Create Game", self.save_new_game, "good"),
        ]

    def build_add(self):
        self.build_create_game()
    def cycle_add_layout(self):
        self.add_layout_index = (self.add_layout_index + 1) % len(BOARD_TYPES); self.buttons[1].label = "Layout: " + BOARD_TYPES[self.add_layout_index].split()[0]
    def save_new_game(self):
        name = self.inputs[0].value("My Game").strip() or "My Game"
        count = max(8, min(80, self.inputs[4].value(28)))
        game = create_classic_template(); game["metadata"]["id"] = str(uuid.uuid4()); game["metadata"]["name"] = name; game["metadata"]["created_at"] = datetime.now().isoformat(timespec="seconds")
        game["settings"].update({"min_players": max(1,self.inputs[1].value(2)), "max_players": max(2,self.inputs[2].value(6)), "starting_money": self.inputs[3].value(1500), "board_square_count": count, "board_layout": BOARD_TYPES[self.add_layout_index]})
        game["rules"]["pass_start_money_enabled"] = True; game["rules"]["pass_start_money"] = self.inputs[5].value(200); game["rules"]["jail_enabled"] = True
        base = []
        for i in range(count):
            if i == 0: base.append(make_square(i, "Start", "start", action=make_action("none")))
            elif i == count//4: base.append(make_square(i, "Waiting Area", "jail", action=make_action("none")))
            elif i == count//2: base.append(make_square(i, "Free Bonus", "reward", action=make_action("gain_money", 50)))
            elif i == (count*3)//4: base.append(make_square(i, "Go To Waiting", "go_to_jail", action=make_action("go_to_jail")))
            elif i % 7 == 0: base.append(make_square(i, "Draw Card", "card", action=make_action("draw_card", target="Event Cards")))
            elif i % 5 == 0: base.append(make_square(i, "Tax", "tax", 0, 100, "Special", make_action("lose_money",100)))
            else:
                group = list(GROUP_COLORS.keys())[i % 8]
                base.append(make_square(i, f"Property {i}", "property", 80 + i*10, 8 + i, group, make_action("buy")))
        game["board"] = base
        path = os.path.join(GAMES_DIR, safe_filename(name)+".json"); save_json(path, game); self.notify("Game saved as JSON."); self.build_main_menu()

    def open_list(self, mode):
        self.list_mode = mode
        if mode == "edit":
            self.editor_active = False
            self.set_scene("edit_game")
        else:
            self.play_select_mode = "list"
            self.set_scene("play_select")
    def build_game_list_buttons(self, mode):
        self.list_games(); w,h = self.screen.get_size(); panel = self.panel_rect(1040, 560)
        self.buttons = [Button((panel.x+28,panel.bottom-58,140,42), "Back", self.build_main_menu, "secondary")]
        y = panel.y + 104; row_h = 64
        for idx,(p,g) in enumerate(self.games_cache[:7]):
            by = y + idx*row_h + 12
            self.buttons.append(Button((panel.right-360,by,95,36), "Play", lambda i=idx: self.start_setup(i), "good"))
            self.buttons.append(Button((panel.right-255,by,95,36), "Edit", lambda i=idx: self.start_edit(i), "secondary"))
            self.buttons.append(Button((panel.right-150,by,95,36), "Delete", lambda i=idx: self.delete_game(i), "danger"))
    def build_edit_game(self):
        if self.editor_active:
            self.build_editor()
        else:
            self.build_game_list_buttons("edit")
    def build_play_select(self):
        if self.play_select_mode == "setup":
            self.build_setup()
        else:
            self.build_game_list_buttons("play")
    def build_gamelist(self):
        if getattr(self, "list_mode", "play") == "edit": self.build_edit_game()
        else: self.build_play_select()
    def delete_game(self, idx):
        p,_=self.games_cache[idx]
        try: os.remove(p); self.notify("Game deleted.")
        except Exception as e: self.notify("Delete failed: "+str(e))
        if getattr(self, "scene", "play_select") == "edit_game": self.build_edit_game()
        else: self.build_play_select()
    def start_edit(self, idx):
        self.edit_path,self.edit_game = self.games_cache[idx]; self.editor_tab="Board"; self.selected_square=0; self.editor_active=True; self.set_scene("edit_game")
    def start_setup(self, idx):
        self.selected_game_path,self.setup_game = self.games_cache[idx]; self.play_select_mode="setup"; self.setup_count = min(max(2, self.setup_game["settings"].get("min_players",2)), self.setup_game["settings"].get("max_players",6)); self.set_scene("play_select")

    def build_setup(self):
        g=self.setup_game; w,h=self.screen.get_size(); panel = self.panel_rect(720, 560); mx=g["settings"].get("max_players",6)
        self.setup_count = min(max(g["settings"].get("min_players",2), getattr(self, "setup_count", g["settings"].get("min_players",2))), mx)
        self.inputs=[]
        x = panel.centerx - 120; y = panel.y + 135
        for i in range(self.setup_count): self.inputs.append(InputBox((x,y+i*43,240,34), f"Player {i+1}"))
        self.buttons=[Button((panel.x+32,panel.bottom-58,140,42),"Back",lambda:self.open_list("play"),"secondary"), Button((panel.centerx-180,panel.y+88,80,36),"-",self.dec_players,"secondary"), Button((panel.centerx+100,panel.y+88,80,36),"+",self.inc_players,"secondary"), Button((panel.centerx-120,panel.bottom-62,240,46),"Start Game",self.launch_game,"good")]
    def dec_players(self): self.setup_count=max(self.setup_game["settings"].get("min_players",2),self.setup_count-1); self.build_setup()
    def inc_players(self): self.setup_count=min(self.setup_game["settings"].get("max_players",6),self.setup_count+1); self.build_setup()
    def launch_game(self):
        names=[self.inputs[i].value(f"Player {i+1}").strip() or f"Player {i+1}" for i in range(min(self.setup_count, len(self.inputs)))]
        self.play_state = GameState(deepcopy(self.setup_game), names)
        self.set_scene("gameplay")

    def editor_content_rects(self):
        w,h=self.screen.get_size()
        top=128; bottom=h-82
        shell=pygame.Rect(24,118,w-48,max(430,bottom-118))
        left=pygame.Rect(shell.x+18,shell.y+58,min(440, max(300, shell.w//3)),shell.h-84)
        right=pygame.Rect(left.right+18,left.y,shell.right-left.right-36,left.h)
        return shell,left,right

    def ensure_editor_defaults(self):
        if not self.edit_game: return
        self.edit_game.setdefault("settings",{})
        self.edit_game.setdefault("rules",{})
        self.edit_game.setdefault("card_decks",{})
        self.edit_game.setdefault("trade_rules",{})
        self.edit_game.setdefault("debt_rules",{})
        self.edit_game.setdefault("visuals",{})
        self.edit_game.setdefault("economy",{})
        if not self.edit_game.get("board"):
            self.edit_game["board"]=[make_square(0,"Start","start")]
        self.selected_square=max(0,min(self.selected_square,len(self.edit_game["board"])-1))
        for i,sq in enumerate(self.edit_game["board"]):
            sq["id"]=i; sq.setdefault("actions",[make_action("none")]); sq.setdefault("timer",{"enabled":False,"mode":"turns","value":0,"action":make_action("none")})
            for key,default in (("rent_base",sq.get("rent",0)),("rent_1_house",sq.get("rent",0)*5),("rent_2_house",sq.get("rent",0)*15),("rent_3_house",sq.get("rent",0)*45),("rent_4_house",sq.get("rent",0)*80),("rent_hotel",sq.get("rent",0)*125),("house_cost",50),("mortgage_value",sq.get("price",0)//2)):
                sq.setdefault(key,default)

    def build_editor(self):
        self.scene = "edit_game"; self.ensure_editor_defaults()
        w,h=self.screen.get_size(); self.inputs=[]; self.toggles=[]
        self.editor_tabs=["Board","Squares","Rules","Cards","Economy","Trade & Debt","Visuals","Test Play"]
        self.buttons=[Button((30,h-64,120,42),"Back",lambda:self.open_list("edit"),"secondary"), Button((w-230,h-64,200,42),"Save Game Template",self.save_edit,"good")]
        tab_w=max(112,min(150,(w-60)//len(self.editor_tabs)-6)); x=30
        for t in self.editor_tabs:
            self.buttons.append(Button((x,82,tab_w,36),t,lambda tab=t:self.set_tab(tab),"primary" if t==self.editor_tab else "secondary")); x+=tab_w+6
        shell,left,right=self.editor_content_rects(); g=self.edit_game; sq=g["board"][self.selected_square]
        if self.editor_tab=="Board":
            self.buttons += [Button((left.x,left.y-44,118,34),"Add Square",self.ed_add_square,"good"), Button((left.x+126,left.y-44,98,34),"Delete",self.ed_del_square,"danger"), Button((left.x+232,left.y-44,66,34),"Up",self.ed_up,"secondary"), Button((left.x+306,left.y-44,82,34),"Down",self.ed_down,"secondary"), Button((right.x,right.y-44,220,34),"Layout: "+g["settings"].get("board_layout",BOARD_TYPES[0]),self.cycle_board_layout,"secondary")]
        elif self.editor_tab=="Squares":
            x1=right.x+150; x2=right.x+470; y=right.y+42; row=38
            self.inputs=[
                InputBox((x1,y,260,30),sq.get("name","Square")), InputBox((x1,y+row,110,30),str(sq.get("price",0)),True), InputBox((x1,y+row*2,110,30),str(sq.get("rent_base",sq.get("rent",0))),True),
                InputBox((x1,y+row*3,110,30),str(sq.get("rent_1_house",0)),True), InputBox((x1,y+row*4,110,30),str(sq.get("rent_2_house",0)),True), InputBox((x1,y+row*5,110,30),str(sq.get("rent_3_house",0)),True),
                InputBox((x1,y+row*6,110,30),str(sq.get("rent_4_house",0)),True), InputBox((x1,y+row*7,110,30),str(sq.get("rent_hotel",0)),True), InputBox((x1,y+row*8,170,30),sq.get("color_group","Special")),
                InputBox((x2,y,110,30),str(sq.get("house_cost",50)),True), InputBox((x2,y+row,110,30),str(sq.get("mortgage_value",sq.get("price",0)//2)),True), InputBox((x2,y+row*2,240,30),sq.get("image","")),
                InputBox((x2,y+row*3,170,30),sq.get("icon","")), InputBox((x2,y+row*4,240,30),sq.get("description","")), InputBox((x2,y+row*5,110,30),str(sq.get("actions",[make_action()])[0].get("amount",0)),True),
                InputBox((x2,y+row*6,180,30),str(sq.get("actions",[make_action()])[0].get("target") or "")), InputBox((x2,y+row*7,220,30),sq.get("actions",[make_action()])[0].get("message","")),
                InputBox((x2,y+row*8,95,30),str(sq.get("timer",{}).get("value",0)),True), InputBox((x2+105,y+row*8,130,30),sq.get("timer",{}).get("mode","turns")),
            ]
            self.toggles=[Toggle((right.x+150,right.y+400,56,28),sq.get("timer",{}).get("enabled",False))]
            self.buttons += [Button((right.x+20,right.y+10,178,32),"Type: "+sq.get("type","custom"),self.cycle_square_type,"secondary"), Button((right.x+210,right.y+10,210,32),"Action: "+sq.get("actions",[make_action()])[0].get("type","none"),self.cycle_action,"secondary")]
        elif self.editor_tab=="Rules":
            self.rule_keys=["pass_start_money_enabled","auction_enabled","rent_enabled","trade_enabled","debt_enabled","jail_enabled","double_reroll_enabled","three_doubles_jail","free_parking_pool_enabled","mortgage_enabled","houses_hotels_enabled","bankruptcy_enabled"]
            self.inputs=[]; self.toggles=[]
            for i,k in enumerate(self.rule_keys): self.toggles.append(Toggle((right.x+30+(i%2)*310,right.y+58+(i//2)*46,56,28),g["rules"].get(k,False)))
        elif self.editor_tab=="Cards":
            decks=list(g["card_decks"].keys()) or ["Custom Deck"]
            if self.selected_card_deck not in g["card_decks"]: self.selected_card_deck=decks[0]; g["card_decks"].setdefault(self.selected_card_deck,[])
            deck=g["card_decks"].setdefault(self.selected_card_deck,[]); card=deck[self.selected_card] if deck and self.selected_card < len(deck) else {"name":"New Card","description":"","image":"","action":make_action("gain_money",50),"holdable":False,"tradable":False,"return_to_deck":True,"single_use":False}
            self.inputs=[InputBox((right.x+180,right.y+50,240,30),self.selected_card_deck),InputBox((right.x+180,right.y+96,260,30),card.get("name","")),InputBox((right.x+180,right.y+142,360,30),card.get("description","")),InputBox((right.x+180,right.y+188,260,30),card.get("image","")),InputBox((right.x+180,right.y+234,120,30),str(card.get("action",{}).get("amount",0)),True),InputBox((right.x+180,right.y+280,220,30),str(card.get("action",{}).get("target") or ""))]
            self.toggles=[Toggle((right.x+220,right.y+328+i*38,56,28),card.get(k,False)) for i,k in enumerate(["holdable","tradable","return_to_deck","single_use"])]
            self.buttons += [Button((right.x+20,right.y+8,120,32),"New Deck",self.new_deck,"good"),Button((right.x+150,right.y+8,110,32),"Add Card",self.add_card,"good"),Button((right.x+270,right.y+8,110,32),"Del Card",self.del_card,"danger"),Button((right.x+390,right.y+8,180,32),"Card Action",self.cycle_card_action,"secondary")]
        elif self.editor_tab=="Economy":
            econ=g.setdefault("economy",{}); rules=g["rules"]; settings=g["settings"]
            self.inputs=[InputBox((right.x+260,right.y+60,130,32),str(settings.get("starting_money",1500)),True),InputBox((right.x+260,right.y+108,170,32),rules.get("tax_destination",econ.get("tax_destination","bank"))),InputBox((right.x+260,right.y+156,130,32),str(rules.get("pass_start_money",200)),True),InputBox((right.x+260,right.y+204,130,32),str(rules.get("jail_fee",50)),True),InputBox((right.x+260,right.y+252,130,32),str(econ.get("auction_minimum_bid",10)),True),InputBox((right.x+260,right.y+300,130,32),str(econ.get("mortgage_interest",10)),True)]
            self.toggles=[Toggle((right.x+260,right.y+350,56,28),econ.get("bank_unlimited",True))]
        elif self.editor_tab=="Trade & Debt":
            tr=g.setdefault("trade_rules",{}); dr=g.setdefault("debt_rules",{})
            keys=[("trade_enabled",g["rules"],"Trade enabled"),("debt_enabled",g["rules"],"Debt enabled"),("interest_enabled",dr,"Interest enabled"),("collateral_enabled",dr,"Collateral enabled"),("two_party_approval",tr,"Two side approval")]
            self.trade_debt_keys=keys; self.toggles=[]
            for i,(k,d,_) in enumerate(keys): self.toggles.append(Toggle((right.x+260,right.y+58+i*46,56,28),d.get(k,True)))
            self.inputs=[InputBox((right.x+260,right.y+292,120,32),str(g["rules"].get("debt_due_turns",dr.get("default_due_turns",5))),True),InputBox((right.x+260,right.y+340,260,32),dr.get("default_penalty","bankruptcy_if_unpaid"))]
        elif self.editor_tab=="Visuals":
            v=g.setdefault("visuals",{})
            self.inputs=[InputBox((right.x+260,right.y+60,220,32),v.get("theme","modern slate")),InputBox((right.x+260,right.y+108,300,32),v.get("board_background","")),InputBox((right.x+260,right.y+156,300,32),v.get("square_images_folder","assets/squares")),InputBox((right.x+260,right.y+204,300,32),v.get("card_back","")),InputBox((right.x+260,right.y+252,220,32),v.get("player_icon_set","classic tokens")),InputBox((right.x+260,right.y+300,90,32),str(v.get("font_size",18)),True)]
            self.toggles=[Toggle((right.x+260,right.y+350,56,28),v.get("dark_theme",True))]
        elif self.editor_tab=="Test Play":
            self.buttons += [Button((right.x+40,right.y+84,250,46),"Start 2 Player Test",self.start_editor_test_play,"roll"), Button((right.x+40,right.y+146,250,42),"Save Then Test",self.save_then_test,"good")]

    def set_tab(self,tab):
        self.save_edit_values(); self.editor_tab=tab; self.build_editor()

    def save_edit_values(self):
        if not self.edit_game: return
        self.ensure_editor_defaults(); g=self.edit_game; sq=g["board"][self.selected_square]
        if self.editor_tab=="Squares" and self.inputs:
            vals=self.inputs; sq["name"]=vals[0].value("Square"); sq["price"]=vals[1].value(0); sq["rent_base"]=vals[2].value(0); sq["rent"]=sq["rent_base"]
            for idx,key in enumerate(["rent_1_house","rent_2_house","rent_3_house","rent_4_house","rent_hotel"],3): sq[key]=vals[idx].value(0)
            sq["color_group"]=vals[8].value("Special"); sq["house_cost"]=vals[9].value(50); sq["mortgage_value"]=vals[10].value(sq.get("price",0)//2); sq["image"]=vals[11].value(""); sq["icon"]=vals[12].value(""); sq["description"]=vals[13].value("")
            act=sq.setdefault("actions",[make_action("none")])[0]; act["amount"]=vals[14].value(0); act["target"]=vals[15].value("") or None; act["message"]=vals[16].value("")
            sq["timer"]={"enabled":self.toggles[0].value if self.toggles else False,"mode":vals[18].value("turns"),"value":vals[17].value(0),"action":make_action(act.get("type","none"),act.get("amount",0),act.get("target"),act.get("message",""))}
        elif self.editor_tab=="Rules":
            for i,k in enumerate(getattr(self,"rule_keys",[])): g["rules"][k]=self.toggles[i].value
        elif self.editor_tab=="Cards" and self.inputs:
            old=self.selected_card_deck; new=self.inputs[0].value(old).strip() or old
            if new!=old: g["card_decks"][new]=g["card_decks"].pop(old,[]); self.selected_card_deck=new
            deck=g["card_decks"].setdefault(self.selected_card_deck,[])
            if deck:
                self.selected_card=min(self.selected_card,len(deck)-1); card=deck[self.selected_card]
                card["name"]=self.inputs[1].value("Card"); card["description"]=self.inputs[2].value(""); card["image"]=self.inputs[3].value(""); card.setdefault("action",make_action()); card["action"]["amount"]=self.inputs[4].value(0); card["action"]["target"]=self.inputs[5].value("") or None
                for i,k in enumerate(["holdable","tradable","return_to_deck","single_use"]): card[k]=self.toggles[i].value
        elif self.editor_tab=="Economy" and self.inputs:
            econ=g.setdefault("economy",{}); settings=g["settings"]; rules=g["rules"]
            settings["starting_money"]=self.inputs[0].value(1500); econ["bank_unlimited"]=self.toggles[0].value if self.toggles else True; rules["tax_destination"]=self.inputs[1].value("bank"); econ["tax_destination"]=rules["tax_destination"]; rules["pass_start_money"]=self.inputs[2].value(200); rules["jail_fee"]=self.inputs[3].value(50); econ["auction_minimum_bid"]=self.inputs[4].value(10); econ["mortgage_interest"]=self.inputs[5].value(10)
        elif self.editor_tab=="Trade & Debt" and self.inputs:
            for i,(k,d,_) in enumerate(getattr(self,"trade_debt_keys",[])): d[k]=self.toggles[i].value
            g["rules"]["debt_due_turns"]=self.inputs[0].value(5); g["debt_rules"]["default_due_turns"]=self.inputs[0].value(5); g["debt_rules"]["default_penalty"]=self.inputs[1].value("bankruptcy_if_unpaid")
        elif self.editor_tab=="Visuals" and self.inputs:
            v=g.setdefault("visuals",{}); keys=["theme","board_background","square_images_folder","card_back","player_icon_set","font_size"]
            for i,k in enumerate(keys): v[k]=self.inputs[i].value(18 if k=="font_size" else "")
            v["dark_theme"]=self.toggles[0].value if self.toggles else True

    def save_edit(self):
        try:
            self.save_edit_values(); self.ensure_editor_defaults(); self.edit_game["metadata"]["updated_at"]=datetime.now().isoformat(timespec="seconds"); save_json(self.edit_path,self.edit_game); self.notify("Game template saved as JSON.")
        except Exception as e:
            self.notify("JSON save failed: "+str(e),5)
    def reindex_board(self):
        for i,sq in enumerate(self.edit_game["board"]): sq["id"]=i
    def ed_add_square(self): self.save_edit_values(); i=len(self.edit_game["board"]); self.edit_game["board"].append(make_square(i,f"New Square {i}","custom",action=make_action("message",message="Custom square"))); self.selected_square=i; self.build_editor()
    def ed_del_square(self):
        if len(self.edit_game["board"])>2: self.edit_game["board"].pop(self.selected_square); self.selected_square=max(0,self.selected_square-1); self.reindex_board(); self.build_editor()
    def ed_up(self):
        self.save_edit_values(); b=self.edit_game["board"]; i=self.selected_square
        if i>0: b[i-1],b[i]=b[i],b[i-1]; self.selected_square-=1; self.reindex_board(); self.build_editor()
    def ed_down(self):
        self.save_edit_values(); b=self.edit_game["board"]; i=self.selected_square
        if i<len(b)-1: b[i+1],b[i]=b[i],b[i+1]; self.selected_square+=1; self.reindex_board(); self.build_editor()
    def cycle_board_layout(self):
        self.save_edit_values(); cur=self.edit_game["settings"].get("board_layout",BOARD_TYPES[0]); idx=(BOARD_TYPES.index(cur)+1)%len(BOARD_TYPES) if cur in BOARD_TYPES else 0; self.edit_game["settings"]["board_layout"]=BOARD_TYPES[idx]; self.build_editor()
    def cycle_square_type(self):
        self.save_edit_values(); sq=self.edit_game["board"][self.selected_square]; current=sq.get("type","custom"); idx=(SQUARE_TYPES.index(current)+1)%len(SQUARE_TYPES) if current in SQUARE_TYPES else 0; sq["type"]=SQUARE_TYPES[idx]
        if sq["type"] in ("property","railroad","utility") and sq.get("price",0)==0: sq["price"]=100; sq["rent"]=10; sq["rent_base"]=10; sq["mortgage_value"]=50
        self.build_editor()
    def cycle_action(self):
        self.save_edit_values(); sq=self.edit_game["board"][self.selected_square]; act=sq.setdefault("actions",[make_action("none")])[0]; idx=(ACTION_TYPES.index(act.get("type","none"))+1)%len(ACTION_TYPES) if act.get("type","none") in ACTION_TYPES else 0; act["type"]=ACTION_TYPES[idx]; self.build_editor()
    def new_deck(self): self.save_edit_values(); self.selected_card_deck="Custom Deck "+str(len(self.edit_game["card_decks"])+1); self.edit_game["card_decks"][self.selected_card_deck]=[]; self.selected_card=0; self.build_editor()
    def add_card(self): self.save_edit_values(); deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[]); deck.append({"id":str(uuid.uuid4()),"name":"New Card","description":"A custom card.","image":"","return_to_deck":True,"single_use":False,"holdable":False,"tradable":False,"action":make_action("gain_money",50)}); self.selected_card=len(deck)-1; self.build_editor()
    def del_card(self):
        deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[])
        if deck: deck.pop(self.selected_card); self.selected_card=max(0,self.selected_card-1); self.build_editor()
    def cycle_card_action(self):
        self.save_edit_values(); deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[])
        if deck:
            self.selected_card=min(self.selected_card,len(deck)-1); act=deck[self.selected_card].setdefault("action",make_action()); idx=(ACTION_TYPES.index(act.get("type","gain_money"))+1)%len(ACTION_TYPES) if act.get("type") in ACTION_TYPES else 0; act["type"]=ACTION_TYPES[idx]
        self.build_editor()
    def start_editor_test_play(self):
        self.save_edit_values(); self.test_play_active=True; self.play_state=GameState(deepcopy(self.edit_game),["Tester 1","Tester 2"]); self.build_gameplay()
    def save_then_test(self): self.save_edit(); self.start_editor_test_play()
    def return_to_editor(self):
        self.test_play_active=False; self.play_state=None; self.editor_active=True; self.build_editor()

    def build_settings(self):
        w,h=self.screen.get_size(); self.buttons=[Button((35,h-70,140,44),"Back",self.build_main_menu,"secondary"), Button((w//2-120,260,240,48),"Toggle Theme",self.toggle_theme,"secondary"), Button((w//2-120,325,240,48),"1280 x 720",lambda:self.set_res(1280,720),"secondary"), Button((w//2-120,390,240,48),"1920 x 1080",lambda:self.set_res(1920,1080),"secondary")]
    def toggle_theme(self): self.dark=not self.dark; self.settings["theme"]="dark" if self.dark else "light"; save_json(SETTINGS_PATH,self.settings)
    def set_res(self,w,h): self.settings["resolution"]=[w,h]; save_json(SETTINGS_PATH,self.settings); self.screen=pygame.display.set_mode((w,h),pygame.RESIZABLE); self.build_settings()
    def build_gameplay(self):
        self.scene = "gameplay"
        w,h=self.screen.get_size(); y=h-58; x=30; gap=8; end_w=132; roll_w=145; details_w=126; small_w=max(76, min(96, (w-60-end_w-roll_w-details_w-gap*12)//9))
        menu_label = "Return Editor" if getattr(self, "test_play_active", False) else "Menu"
        menu_action = self.return_to_editor if getattr(self, "test_play_active", False) else self.confirm_menu
        labels=[(menu_label,menu_action,"secondary",small_w), ("Roll Dice",self.roll_dice,"roll",roll_w), ("Buy",self.buy_property,"good",small_w), ("Auction",self.auction,"secondary",small_w), ("Trade",self.trade,"secondary",small_w), ("Debt",self.debt,"secondary",small_w), ("Build",self.build_house,"secondary",small_w), ("Mortgage",self.mortgage,"secondary",small_w), ("Card",self.use_card,"secondary",small_w), ("Player Details",self.open_current_player_details,"primary",details_w), ("Save",self.save_game,"secondary",small_w)]
        self.buttons=[]
        for lab,act,kind,bw in labels:
            self.buttons.append(Button((x,y,bw,42),lab,act,kind)); x += bw + gap
        self.buttons.append(Button((w-30-end_w,y,end_w,42),"End Turn",self.end_turn,"danger"))
    def build_play(self):
        self.build_gameplay()
    def confirm_menu(self): self.build_main_menu()

    def quit(self): self.running=False

    def roll_dice(self):
        ps=self.play_state
        if ps.rolling or ps.turn_rolled or ps.winner: return
        d1,d2=random.randint(1,6),random.randint(1,6); ps.last_roll=(d1,d2)
        p=ps.current_player(); is_double=d1==d2
        if p.get("in_jail"):
            if is_double:
                p["in_jail"]=False; p["jail_turns_served"]=0; ps.log(f"{p['name']} rolled doubles and left Jail.")
            else:
                p["jail_turns_served"]=p.get("jail_turns_served",0)+1
                if p["jail_turns_served"]>=ps.game["rules"].get("jail_turns",3) and p["money"]>=ps.game["rules"].get("jail_fee",50):
                    fee=ps.game["rules"].get("jail_fee",50); p["money"]-=fee; p["in_jail"]=False; p["jail_turns_served"]=0; ps.log(f"{p['name']} paid {fee} after 3 jail turns and left Jail.")
                else:
                    ps.turn_rolled=True; ps.log(f"{p['name']} is in Jail and did not roll doubles ({d1}+{d2})."); return
        ps.rolling=True; ps.roll_end=time.time()+0.8; ps.pending_steps=d1+d2
        p["doubles"] = p.get("doubles",0)+1 if is_double else 0
        ps.log(f"{p['name']} rolled {d1}+{d2}.")
    def buy_property(self):
        ps=self.play_state; p=ps.current_player(); sq=ps.square(p["pos"])
        if sq["type"] in ("property","railroad","utility") and sq.get("owner") is None and p["money"]>=sq.get("price",0):
            self.open_confirm_modal("buy", "Buy Property", f"Buy {sq['name']} for ${sq.get('price',0)}?", self.confirm_buy_property)
        else: ps.log("Cannot buy this square now.")
    def confirm_buy_property(self):
        ps=self.play_state; p=ps.current_player(); sq=ps.square(p["pos"])
        if sq["type"] in ("property","railroad","utility") and sq.get("owner") is None and p["money"]>=sq.get("price",0):
            p["money"]-=sq.get("price",0); sq["owner"]=p["id"]; p["properties"].append(sq["id"]); ps.log(f"{p['name']} bought {sq['name']} for {sq['price']}.")
        self.close_modal()
    def auction(self):
        ps=self.play_state; sq=ps.square(ps.current_player()["pos"])
        if sq.get("owner") is None and sq["type"] in ("property","railroad","utility"):
            self.open_confirm_modal("auction", "Auction", f"Start a quick auction for {sq['name']}?", self.confirm_auction)
        else: ps.log("Auction is unavailable.")
    def confirm_auction(self):
        ps=self.play_state; sq=ps.square(ps.current_player()["pos"]); bidders=[p for p in ps.players if not p["bankrupt"]]
        if sq.get("owner") is None and sq["type"] in ("property","railroad","utility") and bidders:
            winner=max(bidders,key=lambda p:p["money"]); bid=max(1,int(sq.get("price",100)*0.75)); bid=min(bid,winner["money"])
            winner["money"]-=bid; sq["owner"]=winner["id"]; winner["properties"].append(sq["id"]); ps.log(f"Auction sold {sq['name']} to {winner['name']} for {bid}.")
        self.close_modal()
    def open_confirm_modal(self, modal_type, title, body, confirm_action):
        w, h = self.screen.get_size()
        self.modal = {"type": modal_type, "title": title, "body": body, "opened_at": time.time()}
        self.modal_inputs=[]; self.modal_toggles=[]
        self.modal_buttons=[Button((w//2-135,h//2+105,120,42),"Confirm",confirm_action,"good"), Button((w//2+25,h//2+105,120,42),"Cancel",self.close_modal,"danger")]
    def open_info_modal(self, title, body, icon="card"):
        w, h = self.screen.get_size()
        self.modal = {"type": "info", "title": title, "body": body, "icon": icon, "opened_at": time.time()}
        self.modal_inputs=[]; self.modal_toggles=[]
        self.modal_buttons=[Button((w//2-70,h//2+115,140,42),"OK",self.close_modal,"primary")]
    def open_trade_modal(self):
        ps = self.play_state
        if not ps or not ps.game.get("rules", {}).get("trade_enabled", True):
            if ps: ps.log("Trading is disabled by rules.")
            return
        partners = [p for p in ps.players if p["id"] != ps.current_player()["id"] and not p["bankrupt"]]
        if not partners:
            ps.log("No available trade partner.")
            return
        self.modal_partner_index = 0
        w, h = self.screen.get_size()
        self.modal = {"type": "trade", "title": "Trade Offer", "partners": partners, "opened_at": time.time()}
        self.modal_inputs = [
            InputBox((w//2-95, h//2-20, 120, 34), "100", True),
            InputBox((w//2-95, h//2+35, 120, 34), "", True),
            InputBox((w//2-95, h//2+90, 120, 34), "", True),
        ]
        self.modal_buttons = [
            Button((w//2-220, h//2+145, 130, 42), "Next Player", self.next_modal_partner, "secondary"),
            Button((w//2-70, h//2+145, 120, 42), "Confirm", self.confirm_trade, "good"),
            Button((w//2+70, h//2+145, 120, 42), "Cancel", self.close_modal, "danger"),
        ]
    def next_modal_partner(self):
        if not self.modal: return
        partners = self.modal.get("partners", [])
        if partners:
            self.modal_partner_index = (self.modal_partner_index + 1) % len(partners)
    def confirm_trade(self):
        ps = self.play_state; p = ps.current_player(); partner = self.modal["partners"][self.modal_partner_index]
        amount = max(0, self.modal_inputs[0].value(0)); my_prop = self.modal_inputs[1].value(-1); partner_prop = self.modal_inputs[2].value(-1)
        if amount and p["money"] >= amount:
            p["money"] -= amount; partner["money"] += amount; ps.log(f"Trade: {p['name']} paid {partner['name']} {amount}."); ps.trade_history.append({"type":"money_transfer","from":p["id"],"to":partner["id"],"amount":amount,"turn":ps.turn_count})
        elif amount:
            ps.log("Trade money skipped: insufficient funds.")
        if my_prop in p["properties"]:
            p["properties"].remove(my_prop); partner["properties"].append(my_prop); ps.square(my_prop)["owner"] = partner["id"]; ps.log(f"Trade: {p['name']} gave {ps.square(my_prop)['name']} to {partner['name']}."); ps.trade_history.append({"type":"property_transfer","from":p["id"],"to":partner["id"],"property_id":my_prop,"turn":ps.turn_count})
        if partner_prop in partner["properties"]:
            partner["properties"].remove(partner_prop); p["properties"].append(partner_prop); ps.square(partner_prop)["owner"] = p["id"]; ps.log(f"Trade: {partner['name']} gave {ps.square(partner_prop)['name']} to {p['name']}."); ps.trade_history.append({"type":"property_transfer","from":partner["id"],"to":p["id"],"property_id":partner_prop,"turn":ps.turn_count})
        self.close_modal()
    def open_debt_modal(self):
        ps = self.play_state
        if not ps or not ps.game.get("rules", {}).get("debt_enabled", True):
            if ps: ps.log("Debt / loan system is disabled by rules.")
            return
        partners = [p for p in ps.players if p["id"] != ps.current_player()["id"] and not p["bankrupt"]]
        if not partners:
            ps.log("No lender available.")
            return
        self.modal_partner_index = 0
        w, h = self.screen.get_size()
        self.modal = {"type": "debt", "title": "Debt / Loan", "partners": partners, "opened_at": time.time()}
        self.modal_inputs = [
            InputBox((w//2-95, h//2-20, 120, 34), "100", True),
            InputBox((w//2-95, h//2+35, 120, 34), str(ps.game.get("debt_rules", {}).get("default_interest", 10)), True),
            InputBox((w//2-95, h//2+90, 120, 34), str(ps.game.get("rules", {}).get("debt_due_turns", 5)), True),
        ]
        self.modal_buttons = [
            Button((w//2-220, h//2+145, 130, 42), "Next Lender", self.next_modal_partner, "secondary"),
            Button((w//2-70, h//2+145, 120, 42), "Borrow", self.confirm_debt, "good"),
            Button((w//2+70, h//2+145, 120, 42), "Cancel", self.close_modal, "danger"),
        ]
    def confirm_debt(self):
        ps = self.play_state; borrower = ps.current_player(); lender = self.modal["partners"][self.modal_partner_index]
        amount = max(1, self.modal_inputs[0].value(100)); interest = max(0, self.modal_inputs[1].value(10)); due_turns = max(1, self.modal_inputs[2].value(5))
        if lender["money"] < amount:
            ps.log(f"Loan failed: {lender['name']} does not have {amount}."); self.close_modal(); return
        lender["money"] -= amount; borrower["money"] += amount
        due = ps.turn_count + due_turns
        borrower["debts"].append({"lender": lender["id"], "borrower": borrower["id"], "principal": amount, "interest_percent": interest, "interest": interest, "due_turn": due, "collateral_property_id": None, "penalty_if_unpaid": "bankruptcy_if_unpaid", "penalty": "bankruptcy_if_unpaid", "status": "active"})
        ps.log(f"Loan: {borrower['name']} borrowed {amount} from {lender['name']} at {interest}% interest; due turn {due}."); ps.trade_history.append({"type":"debt_contract","lender":lender["id"],"borrower":borrower["id"],"principal":amount,"interest_percent":interest,"due_turn":due,"turn":ps.turn_count})
        self.close_modal()
    def close_modal(self):
        self.modal = None; self.modal_buttons = []; self.modal_inputs = []; self.modal_toggles = []
    def trade(self):
        self.open_trade_modal()
    def debt(self):
        self.open_debt_modal()
    def build_house(self):
        ps=self.play_state; p=ps.current_player()
        candidates=ps.buildable_properties(p)
        if not candidates:
            ps.log("No property is eligible for a house/hotel. Own a full color group and build evenly."); return
        self.build_candidates=[sq["id"] for sq in candidates]
        lines=[]
        for sq in candidates[:6]: lines.append(f"#{sq['id']} {sq['name']} - cost ${sq.get('house_cost',50)} - houses {sq.get('houses',0)}")
        body = "Eligible properties:\n" + "\n".join(lines) + "\n\nConfirm builds on the first listed property."
        self.open_confirm_modal("build", "Build House / Hotel", body, self.confirm_build_house)
    def confirm_build_house(self):
        ps=self.play_state; p=ps.current_player(); candidates=[ps.square(i) for i in getattr(self,"build_candidates",[]) if i in p.get("properties",[])]
        prop=candidates[0] if candidates else None
        if not prop: ps.log("No eligible property selected."); self.close_modal(); return
        cost=prop.get("house_cost",50)
        if p["money"]<cost: ps.log(f"Need {cost} to build on {prop['name']}."); self.close_modal(); return
        p["money"]-=cost
        if prop.get("houses",0)>=4:
            prop["hotel"]=True; prop["houses"]=0; ps.log(f"Hotel built on {prop['name']} for {cost}.")
        else:
            prop["houses"]=prop.get("houses",0)+1; ps.log(f"House built on {prop['name']} for {cost}.")
        self.close_modal()
    def mortgage(self):
        ps=self.play_state; p=ps.current_player()
        prop=next((ps.square(i) for i in p["properties"] if ps.square(i).get("mortgaged")),None)
        if prop:
            due=int(prop.get("mortgage_value",prop.get("price",100)//2)*1.1)
            if p["money"]>=due:
                p["money"]-=due; prop["mortgaged"]=False; ps.log(f"{p['name']} unmortgaged {prop['name']} for {due}.")
            else: ps.log(f"Need {due} to unmortgage {prop['name']}.")
            return
        prop=next((ps.square(i) for i in p["properties"] if not ps.square(i).get("mortgaged") and not ps.square(i).get("houses",0) and not ps.square(i).get("hotel")),None)
        if prop:
            prop["mortgaged"]=True; val=prop.get("mortgage_value",prop.get("price",100)//2); p["money"]+=val; ps.log(f"{p['name']} mortgaged {prop['name']} for {val}.")
        else: ps.log("No eligible property to mortgage/unmortgage.")
    def use_card(self):
        ps=self.play_state; p=ps.current_player()
        if p["cards"]:
            c=p["cards"].pop(0); self.open_info_modal(c.get("name","Card"), c.get("description", "Card used."), "card"); ps.apply_action(p,c.get("action",make_action()),source=c.get("name","Card"))
        else: ps.log("No held cards.")
    def end_turn(self):
        ps=self.play_state
        if not ps.turn_rolled and not ps.winner: ps.log("Roll first, or use actions before ending.")
        p=ps.current_player(); sq=ps.square(p["pos"])
        if ps.turn_rolled and sq.get("owner") is None and sq.get("type") in ("property","railroad","utility") and ps.game["rules"].get("auction_unbought_property", True):
            self.confirm_auction()
        ps.next_turn()
    def save_game(self):
        ps=self.play_state; data={"saved_at":datetime.now().isoformat(timespec="seconds"),"game":ps.game,"players":ps.players,"current":ps.current,"turn_count":ps.turn_count,"last_roll":ps.last_roll,"free_pool":ps.free_pool,"trade_history":ps.trade_history,"log":ps.logs}
        path=os.path.join(SAVES_DIR,safe_filename(ps.game["metadata"]["name"])+"_save.json"); save_json(path,data); ps.log("Game saved to saves folder.")

    def player_financial_stats(self, ps, player):
        props=[ps.square(i) for i in player.get("properties",[])]
        active_debts=[d for d in player.get("debts",[]) if d.get("status","active")=="active"]
        debt_total=sum(int(d.get("principal",0)*(1+d.get("interest_percent",d.get("interest",0))/100)) for d in active_debts)
        receivable_total=0
        for other in ps.players:
            for d in other.get("debts",[]):
                if d.get("status","active")=="active" and d.get("lender")==player["id"]:
                    receivable_total += int(d.get("principal",0)*(1+d.get("interest_percent",d.get("interest",0))/100))
        return {
            "properties": props,
            "property_count": len(props),
            "railroads": sum(1 for sq in props if sq.get("type")=="railroad"),
            "utilities": sum(1 for sq in props if sq.get("type")=="utility"),
            "houses": sum(sq.get("houses",0) for sq in props),
            "hotels": sum(1 for sq in props if sq.get("hotel")),
            "mortgaged": sum(1 for sq in props if sq.get("mortgaged")),
            "debt_total": debt_total,
            "receivable_total": receivable_total,
            "special_cards": len(player.get("cards",[])),
        }
    def open_current_player_details(self):
        if self.play_state:
            self.open_player_details(self.play_state.current_player()["id"])
    def open_player_details(self, player_id):
        self.detail_player_id = player_id
        self.detail_tab = getattr(self, "detail_tab", "Properties")
        w,h=self.screen.get_size()
        self.modal={"type":"player_details","title":"Player Details","opened_at":time.time()}
        self.modal_inputs=[]; self.modal_toggles=[]
        self.modal_buttons=[Button((w//2+245,h//2+245,120,40),"Close",self.close_modal,"danger")]
    def detail_tab_rects(self):
        w,h=self.screen.get_size(); box=pygame.Rect(w//2-390,h//2-285,780,560)
        tabs=["Properties","Cards","Debt","Trade History"]
        rects=[]; x=box.x+24
        for tab in tabs:
            tw=150 if tab!="Trade History" else 170
            rects.append((tab, pygame.Rect(x, box.y+76, tw, 34))); x += tw + 10
        return rects
    def format_trade_entry(self, ps, entry):
        def pname(pid):
            return ps.players[pid]["name"] if isinstance(pid, int) and 0 <= pid < len(ps.players) else "Player"
        if entry.get("type") == "money_transfer":
            reason = f" ({entry.get('reason')})" if entry.get("reason") else ""
            return f"Turn {entry.get('turn','-')}: {pname(entry.get('from'))} paid {pname(entry.get('to'))} ${entry.get('amount',0)}{reason}."
        if entry.get("type") == "property_transfer":
            prop = ps.square(entry.get("property_id", 0)).get("name", "Property")
            return f"Turn {entry.get('turn','-')}: {prop} moved from {pname(entry.get('from'))} to {pname(entry.get('to'))}."
        if entry.get("type") == "debt_contract":
            return f"Turn {entry.get('turn','-')}: {pname(entry.get('borrower'))} borrowed ${entry.get('principal',0)} from {pname(entry.get('lender'))} at {entry.get('interest_percent',0)}%; due turn {entry.get('due_turn','-')}."
        return str(entry)

    def draw_player_details_modal(self, box):
        ps=self.play_state; player=ps.players[self.detail_player_id % len(ps.players)]; stats=self.player_financial_stats(ps, player)
        col=PLAYER_COLORS[player["id"]%len(PLAYER_COLORS)]
        pygame.draw.circle(self.screen,col,(box.x+42,box.y+42),18); self.ui.text(self.screen,str(player["id"]+1),(box.x+42,box.y+42),15,COLORS["white"],True)
        self.ui.text(self.screen,f"{player['name']}  •  ${player['money']}  •  {ps.square(player['pos'])['name']}",(box.x+72,box.y+27),22,COLORS["text"],max_width=560)
        mouse=pygame.mouse.get_pos()
        for tab,r in self.detail_tab_rects():
            active=tab==self.detail_tab; self.ui.rounded(self.screen,r,COLORS["accent"] if active else COLORS["panel2"],10,border=COLORS["accent"],shadow=False)
            self.ui.text(self.screen,tab,r.center,15,COLORS["dark_text"] if active else COLORS["text"],True,max_width=r.w-12)
        area=pygame.Rect(box.x+24,box.y+125,box.w-48,box.h-185)
        self.ui.glass(self.screen,area,COLORS["panel2"],165,14,COLORS["accent"],45,False)
        y=area.y+14
        if self.detail_tab=="Properties":
            if not stats["properties"]: self.ui.text(self.screen,"No owned properties.",(area.x+18,y),17,COLORS["muted"])
            for sq in stats["properties"][:12]:
                rent=ps.calculate_rent(sq, player) if not sq.get("mortgaged") else 0
                line=f"#{sq['id']} {sq['name']} | {sq.get('color_group')} | Price ${sq.get('price',0)} | Current rent / income ${rent} | H:{sq.get('houses',0)} Hotel:{'Yes' if sq.get('hotel') else 'No'} | Mortgage:{'Yes' if sq.get('mortgaged') else 'No'} (${sq.get('mortgage_value',0)})"
                self.ui.text(self.screen,line,(area.x+14,y),14,COLORS["text"],max_width=area.w-28); y+=27
        elif self.detail_tab=="Cards":
            if not player.get("cards"): self.ui.text(self.screen,"No held special cards.",(area.x+18,y),17,COLORS["muted"])
            for card in player.get("cards",[])[:10]:
                line=f"{card.get('name','Card')} | Usable: Yes | Tradable: {'Yes' if card.get('tradable',False) else 'No'}"
                self.ui.text(self.screen,line,(area.x+14,y),15,COLORS["text"],max_width=area.w-28); y+=22
                self.ui.text(self.screen,card.get("description",""),(area.x+28,y),13,COLORS["muted"],max_width=area.w-42); y+=28
        elif self.detail_tab=="Debt":
            self.ui.text(self.screen,"Borrowed debts",(area.x+14,y),17,COLORS["accent"]); y+=26
            for d in [d for d in player.get("debts",[]) if d.get("status","active")=="active"][:6]:
                remain=max(0,d.get("due_turn",ps.turn_count)-ps.turn_count)
                line=f"From P{d.get('lender',0)+1}: principal {d.get('principal')} | interest {d.get('interest_percent',d.get('interest',0))}% | due {d.get('due_turn')} | remaining {remain} | collateral {d.get('collateral_property_id')} | penalty {d.get('penalty_if_unpaid',d.get('penalty',''))}"
                self.ui.text(self.screen,line,(area.x+14,y),13,COLORS["text"],max_width=area.w-28); y+=24
            y+=10; self.ui.text(self.screen,"Loans given",(area.x+14,y),17,COLORS["accent"]); y+=26
            for other in ps.players:
                for d in other.get("debts",[]):
                    if d.get("status","active")=="active" and d.get("lender")==player["id"]:
                        remain=max(0,d.get("due_turn",ps.turn_count)-ps.turn_count)
                        line=f"To {other['name']}: principal {d.get('principal')} | interest {d.get('interest_percent',d.get('interest',0))}% | due {d.get('due_turn')} | remaining {remain} | status {d.get('status')}"
                        self.ui.text(self.screen,line,(area.x+14,y),13,COLORS["text"],max_width=area.w-28); y+=24
        else:
            entries=[e for e in ps.trade_history if player["id"] in (e.get("from"),e.get("to"),e.get("lender"),e.get("borrower"))]
            if not entries: self.ui.text(self.screen,"No trade history yet.",(area.x+18,y),17,COLORS["muted"])
            for e in entries[-14:]:
                self.ui.text(self.screen,self.format_trade_entry(ps,e),(area.x+14,y),13,COLORS["text"],max_width=area.w-28); y+=24

    def draw_bg(self):
        w,h=self.screen.get_size(); top=(10,18,32) if self.dark else (226,232,240); bot=(15,23,42) if self.dark else (248,250,252)
        for y in range(h):
            t=y/max(1,h); c=tuple(int(top[i]*(1-t)+bot[i]*t) for i in range(3)); pygame.draw.line(self.screen,c,(0,y),(w,y))
        # Subtle neon background blooms, drawn with alpha surfaces so no external assets are required.
        bloom=pygame.Surface((w,h),pygame.SRCALPHA)
        pygame.draw.circle(bloom,(56,189,248,28),(int(w*0.18),int(h*0.18)),max(180,w//6))
        pygame.draw.circle(bloom,(168,85,247,24),(int(w*0.82),int(h*0.28)),max(160,w//7))
        pygame.draw.circle(bloom,(34,197,94,14),(int(w*0.55),int(h*0.92)),max(180,w//6))
        self.screen.blit(bloom,(0,0))
    def handle_event(self,e):
        if e.type==pygame.QUIT: self.running=False
        if self.modal:
            for inp in self.modal_inputs: inp.handle(e)
            if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                if self.modal.get("type")=="player_details":
                    for tab,r in self.detail_tab_rects():
                        if r.collidepoint(e.pos): self.detail_tab=tab; return
                for b in list(self.modal_buttons):
                    if b.click(e.pos) and b.action:
                        b.action(); return
                # Clicks outside the popup are ignored so users do not lose typed trade/debt data.
            if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                self.close_modal(); return
            if e.type != pygame.VIDEORESIZE:
                return
        if e.type==pygame.VIDEORESIZE:
            self.screen=pygame.display.set_mode((max(1000,e.w),max(650,e.h)),pygame.RESIZABLE); getattr(self,"build_"+self.scene)()
        for inp in self.inputs: inp.handle(e)
        for tog in self.toggles: tog.handle(e)
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            for b in list(self.buttons):
                if b.click(e.pos) and b.action: b.action(); return
            if self.scene=="gameplay":
                for pid,r in getattr(self,"player_card_rects",[]):
                    if r.collidepoint(e.pos): self.open_player_details(pid); return
            if self.scene=="edit_game" and self.editor_active: self.editor_click(e.pos)
        if e.type==pygame.KEYDOWN and self.scene=="edit_game" and self.editor_active:
            if e.key==pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL: self.save_edit()
    def editor_square_rects(self, area):
        board=self.edit_game.get("board",[]) if self.edit_game else []
        n=max(1,len(board)); layout=self.edit_game.get("settings",{}).get("board_layout",BOARD_TYPES[0]) if self.edit_game else BOARD_TYPES[0]
        rects=[]
        if layout in ("Circle", "Circular path"):
            cx,cy=area.center; rad=min(area.w,area.h)*0.36
            for i in range(n):
                a=-math.pi/2+2*math.pi*i/n; r=pygame.Rect(0,0,54,38); r.center=(cx+math.cos(a)*rad,cy+math.sin(a)*rad); rects.append(r)
        elif layout in ("Grid path", "Free grid path"):
            cols=max(2,math.ceil(math.sqrt(n))); rows=math.ceil(n/cols); cell_w=area.w/(cols+0.6); cell_h=area.h/(rows+0.6)
            for i in range(n):
                r=pygame.Rect(0,0,min(70,int(cell_w*0.82)),min(44,int(cell_h*0.72))); r.center=(area.x+cell_w*(0.45+i%cols),area.y+cell_h*(0.45+i//cols)); rects.append(r)
        else:
            per=max(1,n//4); left,right,top,bottom=area.x+48,area.right-48,area.y+45,area.bottom-45
            for i in range(n):
                side=i/per
                if side<1: t=(i%per)/per; c=(right-(right-left)*t,bottom)
                elif side<2: t=(i%per)/per; c=(left,bottom-(bottom-top)*t)
                elif side<3: t=(i%per)/per; c=(left+(right-left)*t,top)
                else: t=(i%per)/max(1,n-3*per); c=(right,top+(bottom-top)*t)
                r=pygame.Rect(0,0,58 if i in (0,n//4,n//2,(n*3)//4) else 48,42 if i in (0,n//4,n//2,(n*3)//4) else 34); r.center=c; rects.append(r)
        return rects

    def editor_click(self,pos):
        if self.editor_tab in ("Board","Squares"):
            _,left,_=self.editor_content_rects()
            preview=pygame.Rect(left.x+12,left.y+18,left.w-24,min(310,left.h-160)) if self.editor_tab=="Board" else pygame.Rect(left.x+12,left.y+18,left.w-24,260)
            for i,r in enumerate(self.editor_square_rects(preview)):
                if r.collidepoint(pos): self.save_edit_values(); self.selected_square=i; self.build_editor(); return
            list_y=preview.bottom+18
            for i,sq in enumerate(self.edit_game["board"][:12]):
                if pygame.Rect(left.x+12,list_y+i*30,left.w-24,26).collidepoint(pos): self.save_edit_values(); self.selected_square=i; self.build_editor(); return
        elif self.editor_tab=="Cards":
            _,left,_=self.editor_content_rects(); y=left.y+52
            decks=list(self.edit_game["card_decks"].keys())
            for i,d in enumerate(decks[:10]):
                if pygame.Rect(left.x+14,y+i*30,left.w-28,26).collidepoint(pos): self.save_edit_values(); self.selected_card_deck=d; self.selected_card=0; self.build_editor(); return
            deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[]); cy=y+330
            for i,c in enumerate(deck[:9]):
                if pygame.Rect(left.x+14,cy+i*30,left.w-28,26).collidepoint(pos): self.save_edit_values(); self.selected_card=i; self.build_editor(); return
    def update(self,dt):
        if self.scene=="gameplay" and self.play_state:
            self.play_state.update(dt)
            if getattr(self.play_state, "last_popup", None) and not self.modal:
                pop = self.play_state.last_popup; self.play_state.last_popup = None
                self.open_info_modal(pop.get("title", "Event"), pop.get("body", ""), pop.get("icon", "card"))
    def draw(self):
        self.draw_bg(); getattr(self,"draw_"+self.scene)()
        mouse=pygame.mouse.get_pos()
        for b in self.buttons: b.draw(self.screen,self.ui,mouse)
        for inp in self.inputs: inp.draw(self.screen,self.ui)
        for tog in self.toggles: tog.draw(self.screen,self.ui)
        if time.time()<self.message_until:
            w,h=self.screen.get_size(); self.ui.rounded(self.screen,(w//2-260,20,520,44),COLORS["panel2"],12,border=COLORS["accent"]); self.ui.text(self.screen,self.message,(w//2,42),18,COLORS["text"],True,480)
        if self.modal:
            self.draw_modal()
        pygame.display.flip()
    def draw_modal(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA); overlay.fill((0, 0, 0, 155)); self.screen.blit(overlay, (0, 0))
        age = time.time() - self.modal.get("opened_at", time.time())
        scale = min(1.0, 0.88 + age * 4.0)
        if self.modal.get("type") == "player_details": full = pygame.Rect(w//2-390, h//2-285, 780, 560)
        else: full = pygame.Rect(w//2-300, h//2-185, 600, 390)
        box = pygame.Rect(0, 0, int(full.w*scale), int(full.h*scale)); box.center = full.center
        self.ui.glass(self.screen, box, COLORS["panel"], 220, 24, COLORS["accent"], 135, True)
        self.ui.text(self.screen, self.modal.get("title", "Popup"), (box.centerx, box.y+34), 30, COLORS["accent"], True, box.w-70)
        mtype = self.modal.get("type")
        if mtype == "player_details":
            self.draw_player_details_modal(box)
        elif mtype in ("info", "buy", "auction", "build"):
            icon = self.modal.get("icon", "card")
            if mtype == "buy": icon = "go"
            if mtype == "auction": icon = "tax"
            self.ui.icon(self.screen, icon, (box.centerx, box.y+105), 42, COLORS["accent"])
            self.ui.wrap(self.screen, self.modal.get("body", ""), pygame.Rect(box.x+70, box.y+145, box.w-140, 86), 20, COLORS["text"])
        else:
            partners = self.modal.get("partners", [])
            partner = partners[self.modal_partner_index] if partners else {"name": "None", "money": 0, "properties": []}
            current = self.play_state.current_player() if self.play_state else {"name": "Player", "money": 0, "properties": []}
            self.ui.text(self.screen, f"Current: {current['name']} (${current['money']})", (box.x+38, box.y+78), 17, COLORS["text"])
            self.ui.text(self.screen, f"Partner: {partner['name']} (${partner['money']})", (box.x+38, box.y+104), 17, COLORS["text"])
            labels = ["Money amount", "Your property id", "Partner property id"] if mtype == "trade" else ["Loan amount", "Interest %", "Due in turns"]
            for i, lab in enumerate(labels):
                self.ui.text(self.screen, lab, (box.x+100, h//2-14+i*55), 17, COLORS["muted"])
            helper = "Property ids are square numbers. Leave property fields empty for a money-only trade." if mtype == "trade" else "The lender gives money now. Principal plus interest is collected on the due turn."
            self.ui.wrap(self.screen, helper, pygame.Rect(box.x+330, box.y+145, 220, 95), 15, COLORS["muted"])
        mouse = pygame.mouse.get_pos()
        for inp in self.modal_inputs: inp.draw(self.screen, self.ui)
        for b in self.modal_buttons: b.draw(self.screen, self.ui, mouse)

    def draw_header(self,title,subtitle=""):

        w,h=self.screen.get_size(); self.ui.text(self.screen,title,(w//2,42),38,COLORS["text"],True)
        if subtitle: self.ui.text(self.screen,subtitle,(w//2,76),16,COLORS["muted"],True)
    def draw_main_menu(self):
        self.draw_header(APP_TITLE,"Create, edit, save and play custom property board games")
        panel = self.panel_rect(520, 470)
        self.ui.glass(self.screen,panel,COLORS["panel"],205,24,COLORS["accent"],105)
        logo_y=panel.y+58
        pygame.draw.circle(self.screen,(56,189,248),(panel.centerx-150,logo_y),24,2)
        pygame.draw.circle(self.screen,(168,85,247),(panel.centerx-150,logo_y),12)
        self.ui.text(self.screen,"BOX BOARD GAME STUDIO",(panel.centerx+12,logo_y-10),26,COLORS["text"],True,max_width=panel.w-130)
        self.ui.text(self.screen,"Commercial-quality 2D board game editor",(panel.centerx+12,logo_y+20),15,COLORS["muted"],True,max_width=panel.w-130)
    def draw_menu(self):
        self.draw_main_menu()
    def draw_create_game(self):
        self.draw_header("Create Game","Create a JSON game with a clean custom board setup")
        panel = self.panel_rect(780, 570)
        self.ui.rounded(self.screen,panel,COLORS["panel"],22,border=(255,255,255,30))
        self.ui.text(self.screen,"New Game Settings",(panel.centerx,panel.y+42),26,COLORS["accent"],True)
        label_x = panel.x + max(34, panel.w//10)
        row_y = panel.y + 106
        gap = 52
        labels=["Game Name","Minimum Players","Maximum Players","Starting Money","Board Square Count","Pass Start Money"]
        for i,l in enumerate(labels): self.ui.text(self.screen,l,(label_x,row_y+i*gap+8),18,COLORS["text"])
        self.ui.text(self.screen,"Board Layout: "+BOARD_TYPES[self.add_layout_index],(label_x,row_y+gap*6+8),18,COLORS["muted"],max_width=panel.w-80)
    def draw_gamelist(self):
        self.draw_game_list(getattr(self, "list_mode", "play"))
    def draw_setup(self):
        g=self.setup_game; self.draw_header("Start Game",g["metadata"].get("name","Game"))
        panel=self.panel_rect(720,560); self.ui.rounded(self.screen,panel,COLORS["panel"],22,border=(255,255,255,30))
        self.ui.text(self.screen,f"Player count: {self.setup_count}",(panel.centerx,panel.y+106),22,COLORS["accent"],True)
        for i in range(len(self.inputs)):
            self.ui.text(self.screen,f"P{i+1}",(self.inputs[i].rect.x-45,self.inputs[i].rect.y+7),18,PLAYER_COLORS[i%len(PLAYER_COLORS)])
    def draw_add(self):
        self.draw_create_game()
    def draw_game_list(self, mode):
        title = "Edit Existing Game" if mode == "edit" else "Play Game"
        subtitle = "Stored JSON games in the games folder"
        self.draw_header(title, subtitle)
        w,h=self.screen.get_size(); panel=self.panel_rect(1040,560)
        self.ui.rounded(self.screen,panel,COLORS["panel"],18,border=(255,255,255,30))
        y=panel.y+104; row_h=64
        if not self.games_cache:
            self.ui.text(self.screen,"No saved games found.",(panel.centerx,panel.centery),22,COLORS["muted"],True)
        for idx,(p,g) in enumerate(self.games_cache[:7]):
            r=(panel.x+34,y+idx*row_h,panel.w-430,54); self.ui.rounded(self.screen,r,COLORS["panel2"],14,border=(255,255,255,25),shadow=False)
            m=g.get("metadata",{}); st=g.get("settings",{})
            self.ui.text(self.screen,m.get("name","Untitled"),(panel.x+55,y+idx*row_h+8),20,COLORS["text"],max_width=panel.w-560)
            self.ui.text(self.screen,f"Created: {m.get('created_at','?')}  Players: {st.get('min_players',2)}-{st.get('max_players',6)}  Squares: {len(g.get('board',[]))}",(panel.x+55,y+idx*row_h+32),14,COLORS["muted"],max_width=panel.w-560)
    def draw_editor_board_preview(self, area):
        self.ui.glass(self.screen,area,COLORS["panel2"],155,18,COLORS["accent"],55,False)
        rects=self.editor_square_rects(area); board=self.edit_game.get("board",[])
        for i,sq in enumerate(board):
            if i>=len(rects): break
            r=rects[i]; col=GROUP_COLORS.get(sq.get("color_group"),(100,116,139))
            self.ui.rounded(self.screen,r,(248,250,252),8,border=COLORS["accent"] if i==self.selected_square else col,border_width=3 if i==self.selected_square else 2,shadow=i==self.selected_square)
            pygame.draw.rect(self.screen,col,(r.x+3,r.y+3,r.w-6,6),border_radius=3)
            self.ui.text(self.screen,str(i),(r.centerx,r.centery-2),12,COLORS["dark_text"],True,max_width=r.w-8)
        self.ui.text(self.screen,self.edit_game["settings"].get("board_layout",BOARD_TYPES[0]),(area.centerx,area.bottom-22),16,COLORS["muted"],True,max_width=area.w-30)

    def draw_field_labels(self, labels, start, row=38, color=None):
        x,y=start
        for i,l in enumerate(labels): self.ui.text(self.screen,l,(x,y+i*row+6),15,color or COLORS["muted"],max_width=145)

    def draw_edit_game(self):
        if not self.editor_active:
            self.draw_game_list("edit")
            return
        self.ensure_editor_defaults(); g=self.edit_game; sq=g["board"][self.selected_square]
        self.draw_header("Board Game Studio Editor",g["metadata"].get("name","Game"))
        shell,left,right=self.editor_content_rects(); self.ui.glass(self.screen,shell,COLORS["panel"],160,22,COLORS["accent"],65)
        self.ui.text(self.screen,self.editor_tab,(shell.x+24,shell.y+18),24,COLORS["accent"])
        if self.editor_tab=="Board":
            preview=pygame.Rect(left.x+12,left.y+18,left.w-24,min(310,left.h-160)); self.draw_editor_board_preview(preview)
            list_y=preview.bottom+18; self.ui.text(self.screen,"Square order",(left.x+14,list_y-24),18,COLORS["accent"])
            for i,item in enumerate(g["board"][:12]):
                r=pygame.Rect(left.x+12,list_y+i*30,left.w-24,26); self.ui.rounded(self.screen,r,COLORS["accent2"] if i==self.selected_square else COLORS["panel"],8,shadow=False)
                self.ui.text(self.screen,f"{i:02d}  {item['name']}  •  {item.get('type','custom')}",(r.x+10,r.y+5),13,COLORS["text"],max_width=r.w-20)
            self.ui.text(self.screen,"Selected square",(right.x+20,right.y+24),22,COLORS["accent"])
            self.ui.wrap(self.screen,f"#{self.selected_square} {sq['name']}\nType: {sq.get('type')}\nPrice: ${sq.get('price',0)}\nColor group: {sq.get('color_group')}\n\nUse Add/Delete/Up/Down to change the board order. Use the Layout button to switch Classic rectangle, Circle and Grid path previews.",pygame.Rect(right.x+22,right.y+70,right.w-44,210),18,COLORS["text"])
        elif self.editor_tab=="Squares":
            preview=pygame.Rect(left.x+12,left.y+18,left.w-24,260); self.draw_editor_board_preview(preview)
            list_y=preview.bottom+18
            for i,item in enumerate(g["board"][:12]):
                r=pygame.Rect(left.x+12,list_y+i*30,left.w-24,26); self.ui.rounded(self.screen,r,COLORS["accent2"] if i==self.selected_square else COLORS["panel"],8,shadow=False)
                self.ui.text(self.screen,f"{i:02d} {item['name']}",(r.x+10,r.y+5),13,COLORS["text"],max_width=r.w-20)
            self.ui.text(self.screen,f"Editing square #{self.selected_square}",(right.x+20,right.y+14),22,COLORS["accent"])
            self.draw_field_labels(["Name","Price","Rent base","Rent 1 house","Rent 2 houses","Rent 3 houses","Rent 4 houses","Rent hotel","Color group"],(right.x+20,right.y+42))
            self.draw_field_labels(["House cost","Mortgage value","Image path","Icon","Description","Action amount","Action target","Action message","Timer value / mode"],(right.x+330,right.y+42))
            self.ui.text(self.screen,"Timer enabled",(right.x+20,right.y+404),15,COLORS["muted"])
        elif self.editor_tab=="Rules":
            labels=["Pass Start Money","Auction","Rent","Trade","Debt","Jail","Double Dice","Three Doubles Jail","Free Parking Pot","Mortgage","Houses and Hotels","Bankruptcy"]
            self.ui.wrap(self.screen,"Turn major gameplay systems on/off. Economy values live in the Economy tab; trade and loan contract defaults live in Trade & Debt.",pygame.Rect(left.x+20,left.y+28,left.w-40,110),18,COLORS["text"])
            for i,l in enumerate(labels): self.ui.text(self.screen,l,(right.x+100+(i%2)*310,right.y+62+(i//2)*46),16,COLORS["text"],max_width=230)
        elif self.editor_tab=="Cards":
            self.ui.text(self.screen,"Deck list",(left.x+18,left.y+18),20,COLORS["accent"]); y=left.y+52
            for i,d in enumerate(g["card_decks"].keys()):
                if i>=10: break
                r=pygame.Rect(left.x+14,y+i*30,left.w-28,26); self.ui.rounded(self.screen,r,COLORS["accent2"] if d==self.selected_card_deck else COLORS["panel"],8,shadow=False); self.ui.text(self.screen,d,(r.x+10,r.y+5),13,COLORS["text"],max_width=r.w-20)
            self.ui.text(self.screen,"Cards in deck",(left.x+18,y+300),20,COLORS["accent"]); deck=g["card_decks"].get(self.selected_card_deck,[])
            for i,c in enumerate(deck[:9]):
                r=pygame.Rect(left.x+14,y+330+i*30,left.w-28,26); self.ui.rounded(self.screen,r,COLORS["accent2"] if i==self.selected_card else COLORS["panel"],8,shadow=False); self.ui.text(self.screen,c.get("name","Card"),(r.x+10,r.y+5),13,COLORS["text"],max_width=r.w-20)
            self.draw_field_labels(["Deck name","Card name","Description","Card image","Action amount","Action target"],(right.x+20,right.y+50),46)
            for i,l in enumerate(["Holdable","Tradable","Return to deck","Single use"]): self.ui.text(self.screen,l,(right.x+300,right.y+332+i*38),15,COLORS["text"])
        elif self.editor_tab=="Economy":
            self.ui.wrap(self.screen,"Configure money values used by the template and gameplay economy. These values are saved into JSON with the game template.",pygame.Rect(left.x+20,left.y+30,left.w-40,120),18,COLORS["text"])
            self.draw_field_labels(["Starting money","Tax destination","Salary amount","Jail fee","Auction minimum bid","Mortgage interest %","Bank money unlimited"],(right.x+40,right.y+62),48)
        elif self.editor_tab=="Trade & Debt":
            self.ui.wrap(self.screen,"Configure player-to-player trades, debt contracts, interest, collateral and approval requirements.",pygame.Rect(left.x+20,left.y+30,left.w-40,120),18,COLORS["text"])
            for i,l in enumerate(["Trade open","Debt open","Interest open","Collateral open","Two party approval"]): self.ui.text(self.screen,l,(right.x+340,right.y+62+i*46),16,COLORS["text"])
            self.draw_field_labels(["Default due turns","Default penalty"],(right.x+40,right.y+298),48)
        elif self.editor_tab=="Visuals":
            self.ui.wrap(self.screen,"Choose visual metadata for this game. Missing external assets still fall back to generated Pygame icons and tokens.",pygame.Rect(left.x+20,left.y+30,left.w-40,130),18,COLORS["text"])
            self.draw_field_labels(["Theme preset","Board background","Square images","Card back face","Player icon set","Font size","Dark theme"],(right.x+40,right.y+62),48)
        elif self.editor_tab=="Test Play":
            self.ui.wrap(self.screen,"Quickly test the current JSON template from inside the editor. A temporary 2-player game starts with Tester 1 and Tester 2. Use Return Editor in the gameplay bottom bar to come back without losing editor changes.",pygame.Rect(left.x+20,left.y+30,left.w-40,180),20,COLORS["text"])
            preview=pygame.Rect(right.x+330,right.y+70,min(360,right.w-360),260); self.draw_editor_board_preview(preview)
            self.ui.text(self.screen,"Test play uses a deepcopy of the current template.",(right.x+40,right.y+220),18,COLORS["muted"],max_width=300)
    def draw_editor(self):
        self.draw_edit_game()
    def draw_settings(self):
        self.draw_header("Settings","Theme and resolution")
        self.ui.text(self.screen,"Theme: "+("Dark" if self.dark else "Light"),(self.screen.get_size()[0]//2,210),22,COLORS["text"],True)
    def draw_play_select(self):
        if self.play_select_mode == "setup":
            self.draw_setup()
        else:
            self.draw_game_list("play")
    def draw_play(self):
        self.draw_gameplay()
    def draw_gameplay(self):
        ps=self.play_state; w,h=self.screen.get_size()
        top=pygame.Rect(30,18,w-60,60); self.ui.glass(self.screen,top,COLORS["panel"],165,18,COLORS["accent"],80,False)
        self.ui.text(self.screen,ps.game["metadata"].get("name","Game"),(w//2,34),24,COLORS["text"],True,max_width=650)
        self.ui.text(self.screen,f"Turn {ps.turn_count}  •  {ps.current_player()['name']}'s turn",(w//2,58),16,COLORS["accent"],True)
        board_rect=pygame.Rect(30,92,w-390,h-182); self.ui.glass(self.screen,board_rect,COLORS["panel"],190,22,COLORS["accent"],90)
        ps.draw_board(self.screen,self.ui,board_rect)
        self.board_hover_square = getattr(ps, "hover_square", None)
        if self.board_hover_square:
            mx,my=pygame.mouse.get_pos(); tip=pygame.Rect(mx+16,my+12,280,74)
            if tip.right>w: tip.x=mx-296
            self.ui.glass(self.screen,tip,COLORS["panel2"],235,12,COLORS["accent"],130,True)
            sq=self.board_hover_square
            self.ui.text(self.screen,sq.get("name","Square"),(tip.x+14,tip.y+10),17,COLORS["text"],max_width=250)
            self.ui.text(self.screen,f"{sq.get('type','custom')} • ${sq.get('price',0)} • rent {sq.get('rent',0)}",(tip.x+14,tip.y+39),14,COLORS["muted"],max_width=250)
        side=pygame.Rect(w-335,92,305,h-182); self.ui.glass(self.screen,side,COLORS["panel"],195,22,COLORS["accent"],85)
        self.ui.text(self.screen,"Players",(side.x+18,side.y+16),22,COLORS["accent"])
        d1,d2=ps.animated_dice(); self.draw_die(side.right-118,side.y+10,d1); self.draw_die(side.right-58,side.y+10,d2)
        self.player_card_rects=[]
        y=side.y+52
        card_h=max(52, min(108, (side.h-70)//max(1,len(ps.players))-6))
        for i,p in enumerate(ps.players):
            if y+card_h > side.bottom-10: break
            stats=self.player_financial_stats(ps,p); col=PLAYER_COLORS[i%len(PLAYER_COLORS)]; rr=pygame.Rect(side.x+14,y,277,card_h); self.player_card_rects.append((p["id"],rr.copy()))
            glow = 0.5 + 0.5*math.sin(time.time()*2.4) if i==ps.current else 0
            border = COLORS["accent"] if i==ps.current else (255,255,255,35)
            self.ui.glass(self.screen,rr,(35,48,72) if i==ps.current else (30,41,59),220,14,border,int(80+80*glow) if i==ps.current else 45,False)
            pygame.draw.circle(self.screen,col,(rr.x+22,rr.y+22),13); self.ui.text(self.screen,str(i+1),(rr.x+22,rr.y+22),13,COLORS["white"],True)
            self.ui.text(self.screen,p["name"],(rr.x+42,rr.y+6),16,COLORS["text"],max_width=120)
            self.ui.text(self.screen,f"${p['money']} • {ps.square(p['pos'])['name']}",(rr.x+42,rr.y+25),12,COLORS["muted"],max_width=220)
            if card_h >= 92:
                self.ui.text(self.screen,f"Prop {stats['property_count']} | RR {stats['railroads']} | Util {stats['utilities']}",(rr.x+14,rr.y+48),12,COLORS["text"],max_width=130)
                self.ui.text(self.screen,f"H {stats['houses']} | Hotel {stats['hotels']} | Mtg {stats['mortgaged']}",(rr.x+150,rr.y+48),12,COLORS["text"],max_width=120)
                jail = "Yes" if p.get("in_jail") else "No"
                self.ui.text(self.screen,f"Debt ${stats['debt_total']} | Receive ${stats['receivable_total']}",(rr.x+14,rr.y+66),12,COLORS["muted"],max_width=190)
                self.ui.text(self.screen,f"Jail {jail} ({p.get('jail_turns_served',0)}) | Wait {p.get('wait_turns',0)} | Cards {stats['special_cards']}",(rr.x+14,rr.y+82),12,COLORS["muted"],max_width=230)
            else:
                self.ui.text(self.screen,f"P{stats['property_count']} RR{stats['railroads']} U{stats['utilities']} H{stats['houses']} T{stats['hotels']} M{stats['mortgaged']}",(rr.x+14,rr.y+45),11,COLORS["text"],max_width=210)
                self.ui.text(self.screen,f"D${stats['debt_total']} R${stats['receivable_total']} Jail:{'Y' if p.get('in_jail') else 'N'} W{p.get('wait_turns',0)} C{stats['special_cards']}",(rr.x+14,rr.y+58),11,COLORS["muted"],max_width=230)
            chip_x=rr.right-78; chip_y=rr.y+10
            for prop_id in p["properties"][:8]:
                sq=ps.square(prop_id); chip_col=GROUP_COLORS.get(sq.get("color_group"),(100,116,139))
                pygame.draw.rect(self.screen,chip_col,(chip_x,chip_y,13,9),border_radius=3); chip_x+=16
                if chip_x>rr.right-14: chip_x=rr.right-78; chip_y+=14
            y+=card_h+6
        if y < side.bottom-82:
            self.ui.text(self.screen,"Log",(side.x+18,y+6),18,COLORS["accent"])
            yy=y+30
            for line in ps.logs[-3:]:
                if yy > side.bottom-18: break
                self.ui.text(self.screen,line,(side.x+18,yy),13,COLORS["muted"],max_width=265); yy+=20
        bottom=pygame.Rect(24,h-70,w-48,60); self.ui.glass(self.screen,bottom,COLORS["panel"],160,18,COLORS["accent"],60,False)
        # Button availability follows the current square and turn state.
        current=ps.current_player(); sq=ps.square(current["pos"])
        if len(self.buttons) >= 12:
            self.buttons[1].enabled = (not ps.rolling and not ps.turn_rolled and not ps.winner)
            can_buy = sq["type"] in ("property","railroad","utility") and sq.get("owner") is None and current["money"] >= sq.get("price",0)
            self.buttons[2].enabled = can_buy
            self.buttons[3].enabled = sq["type"] in ("property","railroad","utility") and sq.get("owner") is None
            self.buttons[6].enabled = bool(current["properties"])
            self.buttons[7].enabled = bool(current["properties"])
            self.buttons[8].enabled = bool(current["cards"])
            self.buttons[9].enabled = bool(ps.players)
        if ps.winner:
            self.ui.glass(self.screen,(w//2-260,h//2-80,520,160),COLORS["panel2"],235,24,COLORS["good"],160)
            self.ui.text(self.screen,ps.winner+" wins!",(w//2,h//2),36,COLORS["good"],True)
    def draw_die(self,x,y,val):
        rect=pygame.Rect(x,y,52,52); self.ui.rounded(self.screen,rect,(248,250,252),12,border=COLORS["accent"],shadow=True)
        pip={1:[(0,0)],2:[(-1,-1),(1,1)],3:[(-1,-1),(0,0),(1,1)],4:[(-1,-1),(1,-1),(-1,1),(1,1)],5:[(-1,-1),(1,-1),(0,0),(-1,1),(1,1)],6:[(-1,-1),(1,-1),(-1,0),(1,0),(-1,1),(1,1)]}
        for px,py in pip.get(val,[]): pygame.draw.circle(self.screen,COLORS["dark_text"],(rect.centerx+px*14,rect.centery+py*14),4)
    def run(self):
        while self.running:
            dt=self.clock.tick(60)/1000
            for e in pygame.event.get(): self.handle_event(e)
            self.update(dt); self.draw()
        pygame.quit()


class GameState:
    def __init__(self, game, names):
        self.game=game; self.players=[]; start=game["settings"].get("starting_money",1500)
        for i,n in enumerate(names): self.players.append({"id":i,"name":n,"money":start,"pos":0,"properties":[],"cards":[],"debts":[],"wait_turns":0,"in_jail":False,"jail_turns_served":0,"bankrupt":False,"doubles":0})
        self.current=0; self.turn_count=1; self.last_roll=(1,1); self.rolling=False; self.roll_end=0; self.pending_steps=0; self.moving=False; self.move_timer=0; self.turn_rolled=False; self.logs=["Game started."]; self.winner=None; self.free_pool=0; self.last_popup=None; self.hover_square=None; self.trade_history=[]
    def log(self,msg): self.logs.append(msg); self.logs=self.logs[-80:]
    def current_player(self): return self.players[self.current]
    def square(self,i): return self.game["board"][i % len(self.game["board"])]
    def update(self,dt):
        self.resolve_realtime_timers()
        if self.rolling and time.time()>=self.roll_end:
            self.rolling=False; p=self.current_player()
            if self.game["rules"].get("three_doubles_jail") and p.get("doubles",0)>=3:
                self.go_jail(p); self.turn_rolled=True; return
            self.moving=True; self.move_timer=0
        if self.moving:
            self.move_timer += dt
            if self.move_timer>=0.18:
                self.move_timer=0
                if self.pending_steps>0:
                    p=self.current_player(); old=p["pos"]; p["pos"]=(p["pos"]+1)%len(self.game["board"]); self.pending_steps-=1
                    if p["pos"]<old and p["pos"] != 0 and self.game["rules"].get("pass_start_money_enabled"):
                        p["money"]+=self.game["rules"].get("pass_start_money",200); self.log(f"{p['name']} passed Start and collected money.")
                else:
                    self.moving=False; self.turn_rolled=True; self.land(self.current_player())
    def animated_dice(self): return (random.randint(1,6),random.randint(1,6)) if self.rolling else self.last_roll
    def land(self,p):
        sq=self.square(p["pos"]); self.log(f"{p['name']} landed on {sq['name']}.")
        self.resolve_on_return_timers(p)
        if p["pos"] == 0 and self.game["rules"].get("exact_start_bonus_enabled") and self.turn_rolled:
            bonus = self.game["rules"].get("exact_start_bonus", 0)
            if bonus:
                p["money"] += bonus; self.log(f"{p['name']} landed exactly on Start and received {bonus} bonus.")
        if sq.get("timer",{}).get("enabled"):
            tm=sq["timer"]; mode=tm.get("mode","turns"); timer={"mode":mode,"action":tm.get("action",make_action()),"source":sq["name"],"square":p["pos"]}
            if mode == "seconds": timer["due_time"] = time.time() + max(1, int(tm.get("value",0)))
            elif mode == "on_return": timer["armed"] = True
            else: timer["due_turn"] = self.turn_count + max(1, int(tm.get("value",0)))
            p.setdefault("timers",[]).append(timer); self.log(f"Timer started on {sq['name']}: {tm.get('value',0)} {mode}.")
        if sq.get("type")=="free" and self.game["rules"].get("free_parking_pool_enabled") and self.free_pool:
            p["money"]+=self.free_pool; self.log(f"{p['name']} collected Free Parking pool of {self.free_pool}."); self.free_pool=0
        if sq["type"] in ("property","railroad","utility"):
            owner=sq.get("owner")
            if owner is None: self.log("Available to buy; if skipped, auction starts at end turn.")
            elif owner!=p["id"] and self.game["rules"].get("rent_enabled") and not sq.get("mortgaged"):
                rent=self.calculate_rent(sq, self.players[owner]); self.pay(p,self.players[owner],rent,f"rent for {sq['name']}")
        for act in sq.get("actions",[]): self.apply_action(p,act,source=sq["name"])
        if self.last_roll[0] == self.last_roll[1] and self.game["rules"].get("double_reroll_enabled") and not p.get("wait_turns"):
            self.turn_rolled = False; self.log(f"{p['name']} rolled doubles and may roll again.")
        self.check_bankruptcy(); self.check_winner()
    def apply_action(self,p,act,source="Action"):
        t=act.get("type","none"); amt=int(act.get("amount",0) or 0); target=act.get("target")
        if t in ("none","buy","pay_rent"): return
        if t=="advance_start": self.move_to(p,0); p["money"]+=self.game["rules"].get("pass_start_money",200); self.log(f"{p['name']} advanced to Start and collected salary.")
        elif t=="gain_money": p["money"]+=amt; self.log(f"{p['name']} gained {amt} from {source}.")
        elif t=="lose_money":
            p["money"]-=amt
            if self.game["rules"].get("free_parking_pool_enabled") and self.game["rules"].get("taxes_to")=="free_parking" and "tax" in source.lower(): self.free_pool+=amt
            self.log(f"{p['name']} paid {amt} for {source}.")
        elif t=="move_forward": self.move_direct(p, amt)
        elif t=="move_backward": self.move_direct(p, -amt); self.land(p)
        elif t=="go_to_square": self.move_to(p, int(target or 0)); self.land(p)
        elif t=="go_to_jail": self.go_jail(p)
        elif t=="wait_turns": p["wait_turns"]+=max(1,amt); self.log(f"{p['name']} waits {amt} turns.")
        elif t=="reroll": self.turn_rolled=False; self.log("Roll again granted.")
        elif t=="draw_card": self.draw_card(p, target or "Chance")
        elif t=="nearest_railroad": self.move_to_nearest(p, "railroad")
        elif t=="nearest_utility": self.move_to_nearest(p, "utility")
        elif t=="collect_from_all":
            for o in self.players:
                if o["id"]!=p["id"] and not o["bankrupt"]: self.pay(o,p,amt,"card collection")
        elif t=="pay_all":
            for o in self.players:
                if o["id"]!=p["id"] and not o["bankrupt"]: self.pay(p,o,amt,"card payment")
        elif t=="repair_fee":
            owned=[self.square(i) for i in p["properties"]]; hotel_fee = 115 if amt >= 40 else 100; fee=sum(s.get("houses",0)*amt + (hotel_fee if s.get("hotel") else 0) for s in owned)
            p["money"]-=fee; self.log(f"{p['name']} paid {fee} repair fees.")
        elif t=="transfer_to_player":
            target_id = int(target) if str(target).isdigit() else (p["id"] + 1) % len(self.players)
            other = self.players[target_id % len(self.players)]
            if other["id"] != p["id"] and not other["bankrupt"]: self.pay(p, other, amt, source)
        elif t=="jail_card":
            if p.get("in_jail"):
                p["in_jail"]=False; p["jail_turns_served"]=0; self.log(f"{p['name']} used a Get Out of Jail Free card.")
            else:
                p["cards"].append({"name":"Get Out of Jail Free","description":"Use to leave Jail without paying.","action":make_action("jail_card"),"holdable":True,"tradable":True}); self.log(f"{p['name']} received a Get Out of Jail Free card.")
        elif t=="message": self.log(act.get("message") or f"Message from {source}")
        elif t=="collect_free_parking": p["money"]+=self.free_pool; self.log(f"{p['name']} collected Free Parking pool of {self.free_pool}."); self.free_pool=0
        elif t=="timer": p.setdefault("timers",[]).append({"mode":"turns","due_turn":self.turn_count+max(1,amt),"action":make_action("gain_money",amt),"source":source}); self.log("Timer action scheduled.")
        elif t=="auction": self.log("Auction action is available through the Auction button.")
    def draw_card(self,p,deck_name):
        deck=self.game.get("card_decks",{}).get(deck_name,[])
        if not deck: self.log(deck_name+" deck is empty."); return
        card=random.choice(deck); self.log(f"Card drawn: {card.get('name','Card')} - {card.get('description','')}"); self.last_popup={"title": card.get("name","Card"), "body": card.get("description", ""), "icon": "card"}
        if card.get("holdable"): p["cards"].append(card); self.log("Card kept in hand.")
        else: self.apply_action(p,card.get("action",make_action()),source=card.get("name","Card"))
    def pay(self,src,dst,amt,reason):
        src["money"]-=amt; dst["money"]+=amt; self.log(f"{src['name']} paid {dst['name']} {amt} ({reason})."); self.trade_history.append({"type":"money_transfer","from":src["id"],"to":dst["id"],"amount":amt,"reason":reason,"turn":self.turn_count})
        if src["money"]<0 and not src.get("bankrupt"):
            self.handle_bankruptcy(src, dst.get("id"))
    def move_direct(self,p,steps): p["pos"]=(p["pos"]+steps)%len(self.game["board"]); self.log(f"{p['name']} moved to {self.square(p['pos'])['name']}.")
    def move_to(self,p,pos): p["pos"]=pos%len(self.game["board"]); self.log(f"{p['name']} moved to {self.square(p['pos'])['name']}.")
    def go_jail(self,p):
        jail=next((i for i,s in enumerate(self.game["board"]) if s["type"]=="jail"),0); p["pos"]=jail; p["in_jail"]=True; p["jail_turns_served"]=0; p["doubles"]=0; self.log(f"{p['name']} went to Jail.")
    def next_turn(self):
        p=self.current_player(); self.resolve_timers(p); self.check_bankruptcy(); self.check_winner()
        if self.winner: return
        self.turn_rolled=False; p["doubles"]=0
        for _ in range(len(self.players)):
            self.current=(self.current+1)%len(self.players)
            if self.current==0: self.turn_count+=1
            p=self.current_player()
            if p["bankrupt"]: continue
            if p.get("wait_turns",0)>0:
                p["wait_turns"]-=1; self.log(f"{p['name']} waits this turn."); continue
            break
        self.log(f"Turn: {self.current_player()['name']}.")
    def resolve_realtime_timers(self):
        for p in self.players:
            remain=[]
            for tm in p.get("timers",[]):
                if tm.get("mode") == "seconds" and time.time() >= tm.get("due_time", 10**18):
                    self.apply_action(p, tm.get("action", make_action()), source="timer from "+tm.get("source", "square"))
                else:
                    remain.append(tm)
            p["timers"] = remain
    def resolve_on_return_timers(self,p):
        remain=[]
        for tm in p.get("timers",[]):
            if tm.get("mode") == "on_return" and tm.get("square") == p.get("pos") and tm.get("armed"):
                self.apply_action(p, tm.get("action", make_action()), source="return timer from "+tm.get("source", "square"))
            else:
                remain.append(tm)
        p["timers"] = remain
    def resolve_timers(self,p):
        remain=[]
        for tm in p.get("timers",[]):
            if tm.get("mode") in ("turns", "after_n_turns") and self.turn_count>=tm.get("due_turn",10**18): self.apply_action(p,tm.get("action",make_action()),source="timer from "+tm.get("source","square"))
            else: remain.append(tm)
        p["timers"]=remain
        for debt in list(p.get("debts",[])):
            if debt.get("status","active") != "active": continue
            if self.turn_count>=debt["due_turn"]:
                due=int(debt["principal"]*(1+debt.get("interest_percent",debt.get("interest",0))/100)); self.last_popup={"title":"Debt Due","body":f"{p['name']} owes {due}. If unpaid, bankruptcy/collateral rules apply.","icon":"tax"}
                if p["money"]>=due:
                    p["money"]-=due; lender=self.players[debt.get("lender",0)]; lender["money"]+=due; debt["status"]="paid"; self.log(f"Debt due: {p['name']} paid {due} to {lender['name']}.")
                else:
                    debt["status"]="defaulted"; self.handle_bankruptcy(p, debt.get("lender")); self.log(f"{p['name']} defaulted on a debt.")
            elif debt["due_turn"]-self.turn_count<=1: self.log(f"Debt warning for {p['name']}: due soon.")
    def active_players(self): return [p for p in self.players if not p.get("bankrupt")]
    def group_squares(self, group): return [s for s in self.game["board"] if s.get("type")=="property" and s.get("color_group")==group]
    def owns_color_group(self, player, group):
        group_props=self.group_squares(group)
        return bool(group_props) and all(s.get("owner")==player["id"] for s in group_props)
    def calculate_rent(self, sq, owner):
        if sq.get("mortgaged"): return 0
        if sq.get("type")=="railroad":
            count=sum(1 for s in self.game["board"] if s.get("type")=="railroad" and s.get("owner")==owner["id"])
            rents=sq.get("railroad_rents",[25,50,100,200]); return rents[max(0,min(count,4)-1)]
        if sq.get("type")=="utility":
            count=sum(1 for s in self.game["board"] if s.get("type")=="utility" and s.get("owner")==owner["id"])
            mult=10 if count>=2 else 4; return (self.last_roll[0]+self.last_roll[1])*mult
        if sq.get("hotel"): return sq.get("rent_hotel", sq.get("rent",0))
        houses=sq.get("houses",0)
        if houses: return sq.get(f"rent_{houses}_house", sq.get("rent",0))
        if self.owns_color_group(owner, sq.get("color_group")): return sq.get("rent_full_set", sq.get("rent_base",sq.get("rent",0))*2)
        return sq.get("rent_base", sq.get("rent",0))
    def buildable_properties(self, player):
        result=[]
        for prop_id in player.get("properties",[]):
            sq=self.square(prop_id)
            if sq.get("type")!="property" or sq.get("mortgaged") or sq.get("hotel"): continue
            group=sq.get("color_group")
            if not self.owns_color_group(player, group): continue
            group_props=[s for s in self.group_squares(group) if not s.get("mortgaged") and not s.get("hotel")]
            min_h=min([s.get("houses",0) for s in group_props] or [0])
            if sq.get("houses",0)<=min_h and sq.get("houses",0)<=4: result.append(sq)
        return result
    def move_to_nearest(self,p,square_type):
        start=p["pos"]; n=len(self.game["board"])
        for step in range(1,n+1):
            idx=(start+step)%n
            if self.square(idx).get("type")==square_type:
                if idx<start and self.game["rules"].get("pass_start_money_enabled"):
                    p["money"]+=self.game["rules"].get("pass_start_money",200)
                self.move_to(p,idx); self.land(p); return
    def handle_bankruptcy(self,p, creditor_id=None):
        p["bankrupt"]=True
        creditor=self.players[creditor_id] if creditor_id is not None and 0 <= creditor_id < len(self.players) else None
        for s in self.game["board"]:
            if s.get("owner")==p["id"]:
                if creditor:
                    s["owner"]=creditor["id"]; creditor["properties"].append(s["id"])
                else:
                    s["owner"]=None; s["houses"]=0; s["hotel"]=False; s["mortgaged"]=False
        p["properties"]=[]; self.log(f"{p['name']} is bankrupt and leaves the game.")
    def check_bankruptcy(self):
        for p in self.players:
            if not p["bankrupt"] and p["money"]<0:
                self.handle_bankruptcy(p)
    def check_winner(self):
        active=[p for p in self.players if not p["bankrupt"]]
        if len(active)==1: self.winner=active[0]["name"]
        ec=self.game["rules"].get("end_condition")
        if ec=="wealth_target":
            for p in active:
                if p["money"]>=self.game["rules"].get("wealth_target",5000): self.winner=p["name"]
        if ec=="property_target":
            for p in active:
                if len(p["properties"])>=self.game["rules"].get("property_target",12): self.winner=p["name"]
        if ec=="turn_limit" and self.turn_count>=self.game["rules"].get("turn_limit",60): self.winner=max(active,key=lambda p:p["money"])["name"] if active else None
    def draw_board(self,surf,ui,rect):
        layout=self.game["settings"].get("board_layout",BOARD_TYPES[0]); n=len(self.game["board"]); centers=[]; self.hover_square=None
        mouse=pygame.mouse.get_pos()
        if layout in ("Circle", "Circular path"):
            cx,cy=rect.center; rad=min(rect.w,rect.h)*0.38
            for i in range(n):
                a=-math.pi/2+2*math.pi*i/n; centers.append((cx+math.cos(a)*rad,cy+math.sin(a)*rad))
        elif layout in ("Grid path", "Free grid path"):
            cols=math.ceil(math.sqrt(n)); rows=math.ceil(n/cols); cell=min(rect.w/(cols+1),rect.h/(rows+1))
            for i in range(n): centers.append((rect.x+cell*(1+i%cols),rect.y+cell*(1+i//cols)))
        else:
            per=max(1,n//4); left,right,top,bottom=rect.x+72,rect.right-72,rect.y+70,rect.bottom-70
            for i in range(n):
                side=i/per
                if side<1: t=(i%per)/per; centers.append((right-(right-left)*t,bottom))
                elif side<2: t=(i%per)/per; centers.append((left, bottom-(bottom-top)*t))
                elif side<3: t=(i%per)/per; centers.append((left+(right-left)*t,top))
                else: t=(i%per)/max(1,n-3*per); centers.append((right, top+(bottom-top)*t))
        # Premium center table.
        inner=pygame.Rect(rect.x+120,rect.y+95,max(180,rect.w-240),max(130,rect.h-190))
        ui.glass(surf,inner,(15,23,42),95,22,COLORS["accent2"],45,False)
        ui.text(surf,"BOARD STUDIO",inner.center,30,(71,85,105),True,max_width=inner.w-40)
        square_rects=[]
        for i,sq in enumerate(self.game["board"]):
            x,y=centers[i]; col=GROUP_COLORS.get(sq.get("color_group"),(100,116,139)); corner = i in (0, n//4, n//2, (n*3)//4)
            r=pygame.Rect(0,0,96 if corner else 78,68 if corner else 52); r.center=(x,y); square_rects.append(r)
            hover=r.collidepoint(mouse)
            if hover: self.hover_square=sq
            fill=(248,250,252) if not hover else (255,255,255)
            ui.rounded(surf,r,fill,10,border=col,border_width=3 if not hover else 4,shadow=True if hover else False)
            strip_h=14 if not corner else 18
            pygame.draw.rect(surf,col,(r.x+3,r.y+3,r.w-6,strip_h),border_radius=6)
            st=sq.get("type","custom")
            icon=None
            if st=="card": icon="card"
            elif st=="tax": icon="tax"
            elif st=="railroad": icon="railroad"
            elif st=="utility": icon="utility"
            elif st in ("jail","go_to_jail"): icon="jail"
            elif st=="start": icon="go"
            if icon:
                ui.icon(surf,icon,(r.centerx,r.y+strip_h+14),17 if not corner else 22,col)
                text_y=r.y+strip_h+27
            else:
                text_y=r.y+strip_h+8
            ui.text(surf,sq.get("name","Square"),(r.centerx,text_y),11 if not corner else 12,COLORS["dark_text"],True,max_width=r.w-10)
            if st in ("property","railroad","utility") and sq.get("price",0):
                ui.text(surf,"$"+str(sq.get("price",0)),(r.centerx,r.bottom-10),10,(71,85,105),True,max_width=r.w-10)
            if sq.get("owner") is not None:
                owner_col=PLAYER_COLORS[sq["owner"]%len(PLAYER_COLORS)]
                pygame.draw.rect(surf,owner_col,(r.x+5,r.bottom-7,r.w-10,4),border_radius=2)
                pygame.draw.circle(surf,owner_col,(r.right-10,r.bottom-13),6)
            if sq.get("mortgaged"):
                lock=pygame.Rect(r.x+6,r.bottom-20,15,13); pygame.draw.rect(surf,(107,114,128),lock,border_radius=3); pygame.draw.arc(surf,(107,114,128),(lock.x+2,lock.y-8,11,14),math.pi,0,2)
            elif sq.get("hotel"):
                pygame.draw.rect(surf,COLORS["bad"],(r.x+7,r.bottom-22,18,13),border_radius=3); ui.text(surf,"H",(r.x+16,r.bottom-16),10,COLORS["white"],True)
            elif sq.get("houses",0):
                for hi in range(min(4,sq.get("houses",0))):
                    hx=r.x+7+hi*9; pygame.draw.rect(surf,COLORS["good"],(hx,r.bottom-20,7,10),border_radius=2)
        occupants={}
        for idx,p in enumerate(self.players):
            if not p["bankrupt"]: occupants.setdefault(p["pos"],[]).append(idx)
        for pos,idxs in occupants.items():
            x,y=centers[pos]
            count=len(idxs); spacing=16
            for local,idx in enumerate(idxs):
                p=self.players[idx]; col=PLAYER_COLORS[idx%len(PLAYER_COLORS)]
                off_x=(local-(count-1)/2)*spacing; off_y=10 if count>1 else 0
                active=idx==self.current; pulse=0.5+0.5*math.sin(time.time()*4)
                if active:
                    pygame.draw.circle(surf,(*col,80),(int(x+off_x),int(y+off_y)),20+int(4*pulse))
                    glow=pygame.Surface((52,52),pygame.SRCALPHA); pygame.draw.circle(glow,(*col,95),(26,26),24); surf.blit(glow,(int(x+off_x)-26,int(y+off_y)-26))
                pygame.draw.circle(surf,(15,23,42),(int(x+off_x),int(y+off_y)),15)
                pygame.draw.circle(surf,col,(int(x+off_x),int(y+off_y)),13)
                ui.text(surf,str(idx+1),(x+off_x,y+off_y),13,COLORS["white"],True)



if __name__ == "__main__":
    try:
        App().run()
    except Exception as exc:
        pygame.init(); screen=pygame.display.set_mode((900,360)); pygame.display.set_caption("Startup error")
        font=pygame.font.SysFont("arial",22); running=True
        while running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: running=False
            screen.fill((15,23,42)); screen.blit(font.render("The application encountered an error:",True,(248,250,252)),(40,80)); screen.blit(font.render(str(exc),True,(248,113,113)),(40,125)); screen.blit(font.render("Close this window and check JSON files or terminal output.",True,(148,163,184)),(40,175)); pygame.display.flip()
        pygame.quit()
