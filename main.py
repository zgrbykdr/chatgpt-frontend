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

BOARD_TYPES = ["Monopoly style square", "Circular path", "Free grid path"]
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
        squares.append(make_square(i, n, t, p, r, g, action))
    chance = [
        ("Advance to GO", "go_to_square", 0, "Collect salary if enabled."), ("Bank pays dividend", "gain_money", 50, "Gain 50."),
        ("Go to Jail", "go_to_jail", 0, "Move directly to jail."), ("Speeding fine", "lose_money", 15, "Pay 15."),
        ("Get Out of Jail", "jail_card", 0, "Keep this card until used."), ("Advance 3 spaces", "move_forward", 3, "Move ahead."),
        ("Repairs", "repair_fee", 25, "Pay for each house/hotel."), ("Chairman elected", "pay_all", 50, "Pay every player."),
    ]
    chest = [
        ("Doctor fee", "lose_money", 50, "Pay 50."), ("Bank error in your favor", "gain_money", 200, "Collect 200."),
        ("Life insurance matures", "gain_money", 100, "Collect 100."), ("Pay school fees", "lose_money", 50, "Pay 50."),
        ("Get Out of Jail", "jail_card", 0, "Keep this card until used."), ("Collect from every player", "collect_from_all", 10, "Each player pays you."),
        ("Go to Jail", "go_to_jail", 0, "Move directly to jail."), ("Holiday fund matures", "gain_money", 100, "Collect 100."),
    ]
    def cards(items):
        return [{"id": str(uuid.uuid4()), "name": n, "description": d, "image": "", "return_to_deck": True, "single_use": a == "jail_card", "holdable": a == "jail_card", "tradable": a == "jail_card", "action": make_action(a, amt)} for n, a, amt, d in items]
    game = {
        "metadata": {"id": "classic_template", "name": "Classic Property Trading Game Template", "created_at": datetime.now().isoformat(timespec="seconds"), "updated_at": datetime.now().isoformat(timespec="seconds"), "version": 1},
        "settings": {"min_players": 2, "max_players": 6, "starting_money": 1500, "board_layout": "Monopoly style square", "board_square_count": 40},
        "rules": {
            "pass_start_money_enabled": True, "pass_start_money": 200, "exact_start_bonus_enabled": True, "exact_start_bonus": 200,
            "property_purchase_enabled": True, "auction_enabled": True, "auction_unbought_property": True, "rent_enabled": True,
            "houses_hotels_enabled": True, "mortgage_enabled": True, "trade_enabled": True, "debt_enabled": True, "debt_interest_enabled": True,
            "debt_due_turns": 5, "debt_default": "transfer_collateral_or_penalty", "jail_enabled": True, "jail_fee": 50, "jail_turns": 3,
            "double_reroll_enabled": True, "three_doubles_jail": True, "free_parking_pool_enabled": True, "taxes_to": "bank",
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
            sh = r.copy(); sh.move_ip(4, 6)
            pygame.draw.rect(surf, (0, 0, 0, 55), sh, border_radius=radius)
        pygame.draw.rect(surf, color, r, border_radius=radius)
        if border:
            pygame.draw.rect(surf, border, r, border_width, border_radius=radius)


class Button:
    def __init__(self, rect, label, action=None, kind="primary"):
        self.rect = pygame.Rect(rect); self.label = label; self.action = action; self.kind = kind; self.enabled = True
    def draw(self, surf, ui, mouse):
        hover = self.rect.collidepoint(mouse) and self.enabled
        base = COLORS["accent"] if self.kind == "primary" else COLORS["panel2"]
        if self.kind == "danger": base = COLORS["bad"]
        if self.kind == "good": base = COLORS["good"]
        if not self.enabled: base = (75, 85, 99)
        color = tuple(min(255, c + (22 if hover else 0)) for c in base)
        ui.rounded(surf, self.rect, color, 13, border=(255,255,255,40), shadow=True)
        txt_color = COLORS["dark_text"] if self.kind in ("primary", "good") else COLORS["text"]
        ui.text(surf, self.label, self.rect.center, 18, txt_color, center=True, max_width=self.rect.w-16)
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
        self.scene = "menu"; self.message = ""; self.message_until = 0
        self.buttons = []; self.inputs = []; self.toggles = []
        self.selected_game_path = None; self.games_cache = []
        self.edit_game = None; self.edit_path = None; self.editor_tab = "Board"; self.selected_square = 0; self.selected_card_deck = "Chance"; self.selected_card = 0
        self.play_state = None; self.anim = None; self.popup = None; self.dark = self.settings.get("theme", "dark") == "dark"
        self.modal = None; self.modal_buttons = []; self.modal_inputs = []; self.modal_toggles = []; self.modal_partner_index = 0
        self.ensure_default_template(); self.build_menu()

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
                        data = load_json(p, None)
                        if data and "metadata" in data:
                            games.append((p, data))
                    except Exception:
                        continue
        self.games_cache = games
        return games

    def set_scene(self, scene):
        self.scene = scene; self.buttons = []; self.inputs = []; self.toggles = []
        getattr(self, "build_" + scene)()

    def build_menu(self):
        self.scene = "menu"; self.buttons = []
        w,h = self.screen.get_size(); bw,bh = 330,54; x = w//2-bw//2; y = h//2-110
        items = [("Add New Game", lambda: self.set_scene("add")), ("Edit Existing Game", lambda: self.open_list("edit")), ("Play Game", lambda: self.open_list("play")), ("Settings", lambda: self.set_scene("settings")), ("Exit", self.quit)]
        for i,(lab,act) in enumerate(items): self.buttons.append(Button((x,y+i*68,bw,bh), lab, act, "primary" if i==0 else "secondary"))

    def build_add(self):
        w,h = self.screen.get_size(); self.add_layout_index = 0
        self.inputs = [InputBox((w//2-120,145,320,38), "My Custom Board Game"), InputBox((w//2-120,195,90,38), "2", True), InputBox((w//2+110,195,90,38), "6", True), InputBox((w//2-120,245,120,38), "1500", True), InputBox((w//2-120,295,120,38), "28", True), InputBox((w//2-120,395,120,38), "200", True)]
        self.toggles = [Toggle((w//2-120,350,56,28), True), Toggle((w//2-120,445,56,28), True)]
        self.buttons = [Button((40,h-76,160,46), "Back", self.build_menu, "secondary"), Button((w//2+40,520,220,50), "Save New Game", self.save_new_game, "good"), Button((w//2-220,520,220,50), "Layout: Square", self.cycle_add_layout, "secondary")]
    def cycle_add_layout(self):
        self.add_layout_index = (self.add_layout_index + 1) % len(BOARD_TYPES); self.buttons[-1].label = "Layout: " + BOARD_TYPES[self.add_layout_index].split()[0]
    def save_new_game(self):
        name = self.inputs[0].value("My Game").strip() or "My Game"
        count = max(8, min(80, self.inputs[4].value(28)))
        game = create_classic_template(); game["metadata"]["id"] = str(uuid.uuid4()); game["metadata"]["name"] = name; game["metadata"]["created_at"] = datetime.now().isoformat(timespec="seconds")
        game["settings"].update({"min_players": max(1,self.inputs[1].value(2)), "max_players": max(2,self.inputs[2].value(6)), "starting_money": self.inputs[3].value(1500), "board_square_count": count, "board_layout": BOARD_TYPES[self.add_layout_index]})
        game["rules"]["pass_start_money_enabled"] = self.toggles[0].value; game["rules"]["pass_start_money"] = self.inputs[5].value(200); game["rules"]["jail_enabled"] = self.toggles[1].value
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
        path = os.path.join(GAMES_DIR, safe_filename(name)+".json"); save_json(path, game); self.notify("Game saved as JSON."); self.build_menu()

    def open_list(self, mode):
        self.list_mode = mode; self.set_scene("gamelist")
    def build_gamelist(self):
        self.list_games(); w,h = self.screen.get_size(); self.buttons = [Button((35,h-70,140,44), "Back", self.build_menu, "secondary")]
        y=130
        for idx,(p,g) in enumerate(self.games_cache[:7]):
            self.buttons.append(Button((w-390,y+idx*66,100,38), "Play", lambda i=idx: self.start_setup(i), "good"))
            self.buttons.append(Button((w-280,y+idx*66,100,38), "Edit", lambda i=idx: self.start_edit(i), "secondary"))
            self.buttons.append(Button((w-170,y+idx*66,100,38), "Delete", lambda i=idx: self.delete_game(i), "danger"))
    def delete_game(self, idx):
        p,_=self.games_cache[idx]
        try: os.remove(p); self.notify("Game deleted.")
        except Exception as e: self.notify("Delete failed: "+str(e))
        self.build_gamelist()
    def start_edit(self, idx):
        self.edit_path,self.edit_game = self.games_cache[idx]; self.editor_tab="Board"; self.selected_square=0; self.set_scene("editor")
    def start_setup(self, idx):
        self.selected_game_path,self.setup_game = self.games_cache[idx]; self.set_scene("setup")

    def build_setup(self):
        g=self.setup_game; w,h=self.screen.get_size(); mx=g["settings"].get("max_players",6)
        self.setup_count = min(max(2,g["settings"].get("min_players",2)), mx)
        self.inputs=[]
        for i in range(mx): self.inputs.append(InputBox((w//2-120,155+i*45,240,34), f"Player {i+1}"))
        self.buttons=[Button((35,h-70,140,44),"Back",lambda:self.open_list("play"),"secondary"), Button((w//2-180,95,80,36),"-",self.dec_players,"secondary"), Button((w//2+100,95,80,36),"+",self.inc_players,"secondary"), Button((w//2-120,h-90,240,50),"Start Game",self.launch_game,"good")]
    def dec_players(self): self.setup_count=max(self.setup_game["settings"].get("min_players",2),self.setup_count-1)
    def inc_players(self): self.setup_count=min(self.setup_game["settings"].get("max_players",6),self.setup_count+1)
    def launch_game(self):
        names=[self.inputs[i].value(f"Player {i+1}").strip() or f"Player {i+1}" for i in range(self.setup_count)]
        self.play_state = GameState(deepcopy(self.setup_game), names)
        self.set_scene("play")

    def build_editor(self):
        w,h=self.screen.get_size(); self.buttons=[Button((30,h-64,120,42),"Back",lambda:self.open_list("edit"),"secondary"), Button((w-170,h-64,140,42),"Save JSON",self.save_edit,"good")]
        tabs=["Board","Actions","Timers","Cards","Rules","Trade","Assets"]
        x=30
        for t in tabs:
            self.buttons.append(Button((x,82,110,36),t,lambda tab=t:self.set_tab(tab),"primary" if t==self.editor_tab else "secondary")); x+=118
        if self.editor_tab=="Board":
            self.buttons += [Button((30,135,120,34),"Add Square",self.ed_add_square,"good"), Button((160,135,120,34),"Delete",self.ed_del_square,"danger"), Button((290,135,80,34),"Up",self.ed_up,"secondary"), Button((380,135,80,34),"Down",self.ed_down,"secondary"), Button((470,135,180,34),"Type",self.cycle_square_type,"secondary")]
            sq=self.edit_game["board"][self.selected_square]; self.inputs=[InputBox((620,175,260,34),sq["name"]),InputBox((620,225,120,34),str(sq.get("price",0)),True),InputBox((620,275,120,34),str(sq.get("rent",0)),True),InputBox((620,325,180,34),sq.get("color_group","Special")),InputBox((620,375,320,34),sq.get("description","")),InputBox((620,425,320,34),sq.get("image","")),InputBox((620,475,180,34),sq.get("icon",""))]
        elif self.editor_tab=="Actions":
            sq=self.edit_game["board"][self.selected_square]
            if not sq.get("actions"):
                sq["actions"] = [make_action("none")]
            act=sq["actions"][0]
            self.inputs=[InputBox((620,220,120,34),str(act.get("amount",0)),True),InputBox((620,270,230,34),str(act.get("target") or "")),InputBox((620,320,330,34),act.get("message","") )]
            self.buttons.append(Button((620,170,230,34),"Action: "+act.get("type","none"),self.cycle_action,"secondary"))
        elif self.editor_tab=="Timers":
            sq=self.edit_game["board"][self.selected_square]; tm=sq.get("timer",{})
            self.inputs=[InputBox((620,240,120,34),str(tm.get("value",0)),True),InputBox((620,290,220,34),tm.get("mode","turns")),InputBox((620,340,220,34),tm.get("action",{}).get("type","gain_money")),InputBox((620,390,120,34),str(tm.get("action",{}).get("amount",0)),True)]
            self.toggles=[Toggle((620,190,56,28),tm.get("enabled",False))]
        elif self.editor_tab=="Cards":
            self.inputs=[InputBox((620,175,230,34),self.selected_card_deck)]
            deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[])
            card=deck[self.selected_card] if deck else {"name":"New Card","description":"","action":make_action("gain_money",50)}
            self.inputs += [InputBox((620,250,260,34),card.get("name","")),InputBox((620,300,340,34),card.get("description","")),InputBox((620,350,120,34),str(card.get("action",{}).get("amount",0)),True)]
            self.buttons += [Button((620,130,120,34),"New Deck",self.new_deck,"good"),Button((750,130,120,34),"Add Card",self.add_card,"good"),Button((880,130,120,34),"Del Card",self.del_card,"danger"),Button((620,395,220,34),"Card Action",self.cycle_card_action,"secondary")]
        elif self.editor_tab=="Rules":
            self.inputs=[]; self.toggles=[]; keys=["pass_start_money_enabled","property_purchase_enabled","auction_enabled","rent_enabled","houses_hotels_enabled","mortgage_enabled","trade_enabled","debt_enabled","jail_enabled","double_reroll_enabled","three_doubles_jail","free_parking_pool_enabled"]
            self.rule_keys=keys
            for i,k in enumerate(keys): self.toggles.append(Toggle((620,145+i*36,56,26),self.edit_game["rules"].get(k,False)))
            self.inputs=[InputBox((1000,145,90,32),str(self.edit_game["rules"].get("pass_start_money",200)),True),InputBox((1000,185,90,32),str(self.edit_game["rules"].get("jail_fee",50)),True),InputBox((1000,225,90,32),str(self.edit_game["rules"].get("debt_due_turns",5)),True),InputBox((1000,265,160,32),self.edit_game["rules"].get("end_condition","last_player_standing"))]
        else:
            self.inputs=[]; self.toggles=[]
    def set_tab(self,tab): self.editor_tab=tab; self.build_editor()
    def save_edit_values(self):
        if not self.edit_game: return
        if self.editor_tab=="Board" and self.inputs:
            sq=self.edit_game["board"][self.selected_square]
            sq.update({"name":self.inputs[0].value("Square"),"price":self.inputs[1].value(0),"rent":self.inputs[2].value(0),"color_group":self.inputs[3].value("Special"),"description":self.inputs[4].value(""),"image":self.inputs[5].value(""),"icon":self.inputs[6].value("")})
        elif self.editor_tab=="Actions" and self.inputs:
            sq=self.edit_game["board"][self.selected_square]
            if not sq.get("actions"):
                sq["actions"] = [make_action("none")]
            act=sq["actions"][0]; act["amount"]=self.inputs[0].value(0); act["target"]=self.inputs[1].value("") or None; act["message"]=self.inputs[2].value("")
        elif self.editor_tab=="Timers" and self.inputs:
            sq=self.edit_game["board"][self.selected_square]; sq["timer"]={"enabled":self.toggles[0].value,"mode":self.inputs[1].value("turns"),"value":self.inputs[0].value(0),"action":make_action(self.inputs[2].value("gain_money"),self.inputs[3].value(0))}
        elif self.editor_tab=="Cards" and self.inputs:
            old=self.selected_card_deck; new=self.inputs[0].value(old).strip() or old
            if new!=old: self.edit_game["card_decks"][new]=self.edit_game["card_decks"].pop(old,[]); self.selected_card_deck=new
            deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[])
            if deck:
                card=deck[min(self.selected_card,len(deck)-1)]; card["name"]=self.inputs[1].value("Card"); card["description"]=self.inputs[2].value(""); card.setdefault("action",make_action()); card["action"]["amount"]=self.inputs[3].value(0)
        elif self.editor_tab=="Rules":
            for i,k in enumerate(self.rule_keys): self.edit_game["rules"][k]=self.toggles[i].value
            self.edit_game["rules"]["pass_start_money"]=self.inputs[0].value(200); self.edit_game["rules"]["jail_fee"]=self.inputs[1].value(50); self.edit_game["rules"]["debt_due_turns"]=self.inputs[2].value(5); self.edit_game["rules"]["end_condition"]=self.inputs[3].value("last_player_standing")
    def save_edit(self):
        self.save_edit_values(); self.edit_game["metadata"]["updated_at"]=datetime.now().isoformat(timespec="seconds"); save_json(self.edit_path,self.edit_game); self.notify("Game JSON saved.")
    def ed_add_square(self): self.save_edit_values(); i=len(self.edit_game["board"]); self.edit_game["board"].append(make_square(i,f"New Square {i}","custom",action=make_action("message",message="Custom square"))); self.selected_square=i; self.build_editor()
    def ed_del_square(self):
        if len(self.edit_game["board"])>2: self.edit_game["board"].pop(self.selected_square); self.selected_square=max(0,self.selected_square-1); self.build_editor()
    def ed_up(self):
        b=self.edit_game["board"]; i=self.selected_square
        if i>0: b[i-1],b[i]=b[i],b[i-1]; self.selected_square-=1; self.build_editor()
    def ed_down(self):
        b=self.edit_game["board"]; i=self.selected_square
        if i<len(b)-1: b[i+1],b[i]=b[i],b[i+1]; self.selected_square+=1; self.build_editor()
    def cycle_square_type(self):
        self.save_edit_values()
        sq = self.edit_game["board"][self.selected_square]
        current = sq.get("type", "custom")
        idx = (SQUARE_TYPES.index(current) + 1) % len(SQUARE_TYPES) if current in SQUARE_TYPES else 0
        sq["type"] = SQUARE_TYPES[idx]
        if sq["type"] in ("property", "railroad", "utility") and sq.get("price", 0) == 0:
            sq["price"] = 100
            sq["rent"] = 10
        self.build_editor()
    def cycle_action(self):
        sq = self.edit_game["board"][self.selected_square]
        if not sq.get("actions"):
            sq["actions"] = [make_action("none")]
        act=sq["actions"][0]; idx=(ACTION_TYPES.index(act.get("type","none")) + 1) % len(ACTION_TYPES) if act.get("type","none") in ACTION_TYPES else 0; act["type"]=ACTION_TYPES[idx]; self.build_editor()
    def new_deck(self): self.save_edit_values(); self.selected_card_deck="Custom Deck "+str(len(self.edit_game["card_decks"])+1); self.edit_game["card_decks"][self.selected_card_deck]=[]; self.selected_card=0; self.build_editor()
    def add_card(self): self.save_edit_values(); deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[]); deck.append({"id":str(uuid.uuid4()),"name":"New Card","description":"A custom card.","image":"","return_to_deck":True,"single_use":False,"holdable":False,"tradable":False,"action":make_action("gain_money",50)}); self.selected_card=len(deck)-1; self.build_editor()
    def del_card(self):
        deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[])
        if deck: deck.pop(self.selected_card); self.selected_card=max(0,self.selected_card-1); self.build_editor()
    def cycle_card_action(self):
        deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[])
        if deck:
            act=deck[self.selected_card].setdefault("action",make_action()); idx=(ACTION_TYPES.index(act.get("type","gain_money"))+1)%len(ACTION_TYPES) if act.get("type") in ACTION_TYPES else 0; act["type"]=ACTION_TYPES[idx]
        self.build_editor()

    def build_settings(self):
        w,h=self.screen.get_size(); self.buttons=[Button((35,h-70,140,44),"Back",self.build_menu,"secondary"), Button((w//2-120,260,240,48),"Toggle Theme",self.toggle_theme,"secondary"), Button((w//2-120,325,240,48),"1280 x 720",lambda:self.set_res(1280,720),"secondary"), Button((w//2-120,390,240,48),"1920 x 1080",lambda:self.set_res(1920,1080),"secondary")]
    def toggle_theme(self): self.dark=not self.dark; self.settings["theme"]="dark" if self.dark else "light"; save_json(SETTINGS_PATH,self.settings)
    def set_res(self,w,h): self.settings["resolution"]=[w,h]; save_json(SETTINGS_PATH,self.settings); self.screen=pygame.display.set_mode((w,h),pygame.RESIZABLE); self.build_settings()
    def build_play(self):
        w,h=self.screen.get_size(); self.buttons=[Button((35,h-58,122,40),"Main Menu",self.confirm_menu,"secondary"),Button((170,h-58,115,40),"Roll Dice",self.roll_dice,"primary"),Button((295,h-58,130,40),"Buy Property",self.buy_property,"good"),Button((435,h-58,100,40),"Auction",self.auction,"secondary"),Button((545,h-58,90,40),"Trade",self.trade,"secondary"),Button((645,h-58,115,40),"Debt / Loan",self.debt,"secondary"),Button((770,h-58,120,40),"Build House",self.build_house,"secondary"),Button((900,h-58,105,40),"Mortgage",self.mortgage,"secondary"),Button((1015,h-58,95,40),"Use Card",self.use_card,"secondary"),Button((1120,h-58,110,40),"End Turn",self.end_turn,"secondary"),Button((w-135,h-58,105,40),"Save",self.save_game,"secondary")]
    def confirm_menu(self): self.build_menu()

    def quit(self): self.running=False

    def roll_dice(self):
        ps=self.play_state
        if ps.rolling or ps.turn_rolled or ps.winner: return
        d1,d2=random.randint(1,6),random.randint(1,6); ps.last_roll=(d1,d2); ps.rolling=True; ps.roll_end=time.time()+0.85; ps.pending_steps=d1+d2
        p=ps.current_player(); p["doubles"] = p.get("doubles",0)+1 if d1==d2 else 0
        ps.log(f"{p['name']} rolled {d1}+{d2}.")
    def buy_property(self):
        ps=self.play_state; p=ps.current_player(); sq=ps.square(p["pos"])
        if sq["type"] in ("property","railroad","utility") and sq.get("owner") is None and p["money"]>=sq.get("price",0):
            p["money"]-=sq.get("price",0); sq["owner"]=p["id"]; p["properties"].append(sq["id"]); ps.log(f"{p['name']} bought {sq['name']} for {sq['price']}.")
        else: ps.log("Cannot buy this square now.")
    def auction(self):
        ps=self.play_state; sq=ps.square(ps.current_player()["pos"]); bidders=[p for p in ps.players if not p["bankrupt"]]
        if sq.get("owner") is None and sq["type"] in ("property","railroad","utility") and bidders:
            winner=max(bidders,key=lambda p:p["money"]); bid=max(1,int(sq.get("price",100)*0.75)); bid=min(bid,winner["money"])
            winner["money"]-=bid; sq["owner"]=winner["id"]; winner["properties"].append(sq["id"]); ps.log(f"Auction sold {sq['name']} to {winner['name']} for {bid}.")
        else: ps.log("Auction is unavailable.")
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
        self.modal = {"type": "trade", "title": "Trade Offer", "partners": partners}
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
            p["money"] -= amount; partner["money"] += amount; ps.log(f"Trade: {p['name']} paid {partner['name']} {amount}.")
        elif amount:
            ps.log("Trade money skipped: insufficient funds.")
        if my_prop in p["properties"]:
            p["properties"].remove(my_prop); partner["properties"].append(my_prop); ps.square(my_prop)["owner"] = partner["id"]; ps.log(f"Trade: {p['name']} gave {ps.square(my_prop)['name']} to {partner['name']}.")
        if partner_prop in partner["properties"]:
            partner["properties"].remove(partner_prop); p["properties"].append(partner_prop); ps.square(partner_prop)["owner"] = p["id"]; ps.log(f"Trade: {partner['name']} gave {ps.square(partner_prop)['name']} to {p['name']}.")
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
        self.modal = {"type": "debt", "title": "Debt / Loan", "partners": partners}
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
        borrower["debts"].append({"lender": lender["id"], "principal": amount, "interest": interest, "due_turn": due, "penalty": "pay_extra_or_wait"})
        ps.log(f"Loan: {borrower['name']} borrowed {amount} from {lender['name']} at {interest}% interest; due turn {due}.")
        self.close_modal()
    def close_modal(self):
        self.modal = None; self.modal_buttons = []; self.modal_inputs = []; self.modal_toggles = []
    def trade(self):
        self.open_trade_modal()
    def debt(self):
        self.open_debt_modal()
    def build_house(self):
        ps=self.play_state; p=ps.current_player(); owned=[ps.square(i) for i in p["properties"]]
        prop=next((s for s in owned if s["type"]=="property" and not s.get("hotel")),None)
        if prop and p["money"]>=50:
            p["money"]-=50
            if prop.get("houses",0)>=4: prop["hotel"]=True; prop["houses"]=0; ps.log(f"Hotel built on {prop['name']}.")
            else: prop["houses"]=prop.get("houses",0)+1; ps.log(f"House built on {prop['name']}.")
        else: ps.log("No eligible property or money.")
    def mortgage(self):
        ps=self.play_state; p=ps.current_player(); prop=next((ps.square(i) for i in p["properties"] if not ps.square(i).get("mortgaged")),None)
        if prop:
            prop["mortgaged"]=True; val=prop.get("price",100)//2; p["money"]+=val; ps.log(f"{p['name']} mortgaged {prop['name']} for {val}.")
        else: ps.log("No property to mortgage.")
    def use_card(self):
        ps=self.play_state; p=ps.current_player()
        if p["cards"]:
            c=p["cards"].pop(0); ps.apply_action(p,c.get("action",make_action()),source=c.get("name","Card"))
        else: ps.log("No held cards.")
    def end_turn(self):
        ps=self.play_state
        if not ps.turn_rolled and not ps.winner: ps.log("Roll first, or use actions before ending.")
        ps.next_turn()
    def save_game(self):
        ps=self.play_state; data={"saved_at":datetime.now().isoformat(timespec="seconds"),"game":ps.game,"players":ps.players,"current":ps.current,"turn_count":ps.turn_count,"log":ps.logs}
        path=os.path.join(SAVES_DIR,safe_filename(ps.game["metadata"]["name"])+"_save.json"); save_json(path,data); ps.log("Game saved to saves folder.")

    def draw_bg(self):
        w,h=self.screen.get_size(); top=(18,24,38) if self.dark else (226,232,240); bot=(15,23,42) if self.dark else (248,250,252)
        for y in range(h):
            t=y/max(1,h); c=tuple(int(top[i]*(1-t)+bot[i]*t) for i in range(3)); pygame.draw.line(self.screen,c,(0,y),(w,y))
    def handle_event(self,e):
        if e.type==pygame.QUIT: self.running=False
        if self.modal:
            for inp in self.modal_inputs: inp.handle(e)
            if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
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
            if self.scene=="editor": self.editor_click(e.pos)
        if e.type==pygame.KEYDOWN and self.scene=="editor":
            if e.key==pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL: self.save_edit()
    def editor_click(self,pos):
        if self.editor_tab in ("Board","Actions","Timers"):
            x,y=30,185
            for i,sq in enumerate(self.edit_game["board"]):
                r=pygame.Rect(x,y+i*32,520,28)
                if r.collidepoint(pos): self.save_edit_values(); self.selected_square=i; self.build_editor(); break
        elif self.editor_tab=="Cards":
            x,y=30,170
            decks=list(self.edit_game["card_decks"].keys())
            for i,d in enumerate(decks):
                if pygame.Rect(x,y+i*32,220,28).collidepoint(pos): self.save_edit_values(); self.selected_card_deck=d; self.selected_card=0; self.build_editor(); return
            deck=self.edit_game["card_decks"].setdefault(self.selected_card_deck,[])
            for i,c in enumerate(deck):
                if pygame.Rect(270,y+i*32,300,28).collidepoint(pos): self.save_edit_values(); self.selected_card=i; self.build_editor(); return
    def update(self,dt):
        if self.scene=="play" and self.play_state: self.play_state.update(dt)
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
        overlay = pygame.Surface((w, h), pygame.SRCALPHA); overlay.fill((0, 0, 0, 145)); self.screen.blit(overlay, (0, 0))
        box = pygame.Rect(w//2-300, h//2-175, 600, 370)
        self.ui.rounded(self.screen, box, COLORS["panel"], 22, border=COLORS["accent"], shadow=True)
        self.ui.text(self.screen, self.modal.get("title", "Popup"), (box.centerx, box.y+32), 28, COLORS["accent"], True)
        partners = self.modal.get("partners", [])
        partner = partners[self.modal_partner_index] if partners else {"name": "None", "money": 0, "properties": []}
        current = self.play_state.current_player() if self.play_state else {"name": "Player", "money": 0, "properties": []}
        self.ui.text(self.screen, f"Current: {current['name']} (${current['money']})", (box.x+35, box.y+75), 17, COLORS["text"])
        self.ui.text(self.screen, f"Partner: {partner['name']} (${partner['money']})", (box.x+35, box.y+100), 17, COLORS["text"])
        labels = ["Money amount", "Your property id", "Partner property id"] if self.modal.get("type") == "trade" else ["Loan amount", "Interest %", "Due in turns"]
        for i, lab in enumerate(labels):
            self.ui.text(self.screen, lab, (box.x+105, h//2-14+i*55), 17, COLORS["muted"])
        if self.modal.get("type") == "trade":
            self.ui.wrap(self.screen, "Property ids are the square numbers shown on the board/list. Leave property fields empty for a money-only trade.", pygame.Rect(box.x+330, box.y+135, 220, 95), 15, COLORS["muted"])
        else:
            self.ui.wrap(self.screen, "The lender gives money now. Principal plus interest is automatically collected when the due turn arrives.", pygame.Rect(box.x+330, box.y+135, 220, 95), 15, COLORS["muted"])
        mouse = pygame.mouse.get_pos()
        for inp in self.modal_inputs: inp.draw(self.screen, self.ui)
        for b in self.modal_buttons: b.draw(self.screen, self.ui, mouse)

    def draw_header(self,title,subtitle=""):

        w,h=self.screen.get_size(); self.ui.text(self.screen,title,(w//2,42),38,COLORS["text"],True)
        if subtitle: self.ui.text(self.screen,subtitle,(w//2,76),16,COLORS["muted"],True)
    def draw_menu(self):
        w,h=self.screen.get_size(); self.draw_header(APP_TITLE,"Create, edit, save and play custom property board games")
        self.ui.rounded(self.screen,(w//2-225,120,450,80),COLORS["panel"],20,border=(255,255,255,30)); self.ui.text(self.screen,"Professional 2D Board Game Maker",(w//2,160),24,COLORS["accent"],True)
    def draw_add(self):
        self.draw_header("Add New Game","Create a JSON game with rules, board layout, timers and card decks")
        labels=["Game name","Players min / max","Starting money","Board square count","Pay when passing Start?","Start pass money","Use jail / waiting area?"]
        y=153; x=self.screen.get_size()[0]//2-370
        for i,l in enumerate(labels): self.ui.text(self.screen,l,(x,y+i*50),18,COLORS["text"])
        self.ui.text(self.screen,"Board layout: "+BOARD_TYPES[self.add_layout_index],(x,505),18,COLORS["muted"])
    def draw_gamelist(self):
        self.draw_header("Select Game","Stored JSON games in the games folder")
        w,h=self.screen.get_size(); y=130
        for idx,(p,g) in enumerate(self.games_cache[:7]):
            r=(55,y+idx*66,w-470,54); self.ui.rounded(self.screen,r,COLORS["panel"],14,border=(255,255,255,25))
            m=g.get("metadata",{}); s=g.get("settings",{})
            self.ui.text(self.screen,m.get("name","Untitled"),(75,y+idx*66+8),20,COLORS["text"],max_width=w-600)
            self.ui.text(self.screen,f"Created: {m.get('created_at','?')}  Players: {s.get('min_players',2)}-{s.get('max_players',6)}  Squares: {len(g.get('board',[]))}",(75,y+idx*66+32),14,COLORS["muted"],max_width=w-600)
    def draw_setup(self):
        g=self.setup_game; self.draw_header("Start Game",g["metadata"].get("name","Game")); self.ui.text(self.screen,f"Player count: {self.setup_count}",(self.screen.get_size()[0]//2,108),22,COLORS["accent"],True)
        for i in range(len(self.inputs)):
            self.inputs[i].rect.y=155+i*45; self.inputs[i].rect.x=self.screen.get_size()[0]//2-120
            if i>=self.setup_count: continue
            self.ui.text(self.screen,f"P{i+1}",(self.inputs[i].rect.x-45,self.inputs[i].rect.y+7),18,PLAYER_COLORS[i%len(PLAYER_COLORS)])
    def draw_editor(self):
        g=self.edit_game; self.draw_header("Game Editor",g["metadata"].get("name","Game"))
        if self.editor_tab in ("Board","Actions","Timers"):
            self.ui.text(self.screen,"Squares",(30,170),20,COLORS["accent"])
            for i,sq in enumerate(g["board"][:14]):
                r=pygame.Rect(30,185+i*32,520,28); self.ui.rounded(self.screen,r,COLORS["accent2"] if i==self.selected_square else COLORS["panel"],8,shadow=False)
                self.ui.text(self.screen,f"{i:02d} {sq['name']} | {sq['type']} | ${sq.get('price',0)} / rent {sq.get('rent',0)}",(40,190+i*32),14,COLORS["text"],max_width=500)
            sq=g["board"][self.selected_square]; self.buttons[-1].label="Type: "+sq.get("type","custom"); self.ui.text(self.screen,"Selected square: "+sq["name"],(620,135),22,COLORS["accent"])
            if self.editor_tab=="Board":
                for j,l in enumerate(["Name","Price","Rent","Color group","Description","Image path","Icon"]): self.ui.text(self.screen,l,(500,183+j*50),18,COLORS["muted"])
            if self.editor_tab=="Actions":
                act=sq["actions"][0]; self.ui.text(self.screen,"Square Action Editor",(620,135),22,COLORS["accent"]); self.ui.text(self.screen,"Current action: "+act.get("type","none"),(620,205),18,COLORS["muted"])
                for j,l in enumerate(["Amount","Target square/deck/player","Message"]): self.ui.text(self.screen,l,(430,228+j*50),18,COLORS["muted"])
                self.ui.wrap(self.screen,"Actions include buying, rent, cards, money transfer, movement, jail, waiting turns, auctions, messages, timers and next-turn actions.",pygame.Rect(620,370,460,90),16,COLORS["muted"])
            if self.editor_tab=="Timers":
                self.ui.text(self.screen,"Timer System",(620,135),22,COLORS["accent"]); self.ui.text(self.screen,"Enabled",(500,194),18,COLORS["muted"])
                for j,l in enumerate(["Timer value","Timer mode","Action when finished","Action amount"]): self.ui.text(self.screen,l,(430,248+j*50),18,COLORS["muted"])
                self.ui.wrap(self.screen,"Modes: seconds, turns, on_return, after_n_turns. Gameplay executes turn timers and shows debt/timer warnings in the log.",pygame.Rect(620,440,480,80),16,COLORS["muted"])
        elif self.editor_tab=="Cards":
            self.ui.text(self.screen,"Decks",(30,135),20,COLORS["accent"]); y=170
            for i,d in enumerate(g["card_decks"].keys()): self.ui.rounded(self.screen,(30,y+i*32,220,28),COLORS["accent2"] if d==self.selected_card_deck else COLORS["panel"],8,shadow=False); self.ui.text(self.screen,d,(40,y+i*32+5),14,COLORS["text"],max_width=200)
            self.ui.text(self.screen,"Cards",(270,135),20,COLORS["accent"]); deck=g["card_decks"].get(self.selected_card_deck,[])
            for i,c in enumerate(deck[:12]): self.ui.rounded(self.screen,(270,y+i*32,300,28),COLORS["accent2"] if i==self.selected_card else COLORS["panel"],8,shadow=False); self.ui.text(self.screen,c.get("name","Card"),(280,y+i*32+5),14,COLORS["text"],max_width=280)
            for j,l in enumerate(["Deck name","Card name","Card description","Action amount"]): self.ui.text(self.screen,l,(465,183+j*50 if j else 183),18,COLORS["muted"])
        elif self.editor_tab=="Rules":
            self.ui.text(self.screen,"Rules Editor",(60,135),24,COLORS["accent"])
            for i,k in enumerate(self.rule_keys): self.ui.text(self.screen,k.replace("_"," ").title(),(690,148+i*36),16,COLORS["text"])
            self.ui.text(self.screen,"Money / jail / debt / end condition",(1000,120),18,COLORS["accent"])
        else:
            self.ui.text(self.screen,self.editor_tab+" System",(60,140),28,COLORS["accent"])
            self.ui.wrap(self.screen,"This panel documents and stores trade/debt/asset options in JSON. The first version includes working money trades, loans with interest and due turns, default icons, missing-image fallback, player tokens, property ownership markers, and editable JSON fields.",pygame.Rect(60,190,800,160),20,COLORS["text"])
    def draw_settings(self):
        self.draw_header("Settings","Theme and resolution")
        self.ui.text(self.screen,"Theme: "+("Dark" if self.dark else "Light"),(self.screen.get_size()[0]//2,210),22,COLORS["text"],True)
    def draw_play(self):
        ps=self.play_state; w,h=self.screen.get_size(); self.ui.text(self.screen,ps.game["metadata"].get("name","Game"),(w//2,24),24,COLORS["text"],True,max_width=600)
        self.ui.text(self.screen,f"Turn {ps.turn_count} - {ps.current_player()['name']}'s turn",(w//2,52),16,COLORS["accent"],True)
        board_rect=pygame.Rect(30,85,w-390,h-160); self.ui.rounded(self.screen,board_rect,COLORS["panel"],18,border=(255,255,255,30))
        ps.draw_board(self.screen,self.ui,board_rect)
        side=pygame.Rect(w-335,85,305,h-160); self.ui.rounded(self.screen,side,COLORS["panel"],18,border=(255,255,255,30))
        self.ui.text(self.screen,"Players",(side.x+18,side.y+15),22,COLORS["accent"])
        y=side.y+50
        for i,p in enumerate(ps.players):
            col=PLAYER_COLORS[i%len(PLAYER_COLORS)]; rr=pygame.Rect(side.x+14,y,277,62); self.ui.rounded(self.screen,rr,(51,65,85) if i==ps.current else (38,50,70),12,shadow=False)
            if i==ps.current: pygame.draw.rect(self.screen,COLORS["accent"],rr,2,border_radius=12)
            pygame.draw.circle(self.screen,col,(rr.x+22,rr.y+29),12); self.ui.text(self.screen,p["name"],(rr.x+42,rr.y+8),17,COLORS["text"],max_width=150)
            debt_count=len(p.get("debts",[])); timer_count=len(p.get("timers",[]))
            self.ui.text(self.screen,f"${p['money']} Pos {p['pos']} Props {len(p['properties'])} Debt {debt_count} Timer {timer_count}",(rr.x+42,rr.y+32),14,COLORS["muted"],max_width=240)
            y+=70
        self.ui.text(self.screen,"Dice",(side.x+18,y+5),18,COLORS["accent"])
        d1,d2=ps.animated_dice(); self.draw_die(side.x+25,y+35,d1); self.draw_die(side.x+90,y+35,d2)
        self.ui.text(self.screen,"Log",(side.x+18,y+100),18,COLORS["accent"])
        yy=y+130
        for line in ps.logs[-6:]: self.ui.text(self.screen,line,(side.x+18,yy),13,COLORS["muted"],max_width=265); yy+=21
        if ps.winner:
            self.ui.rounded(self.screen,(w//2-250,h//2-70,500,140),COLORS["panel2"],20,border=COLORS["good"]); self.ui.text(self.screen,ps.winner+" wins!",(w//2,h//2),34,COLORS["good"],True)
    def draw_die(self,x,y,val):
        rect=pygame.Rect(x,y,50,50); self.ui.rounded(self.screen,rect,COLORS["white"],10,shadow=False); self.ui.text(self.screen,str(val),(x+25,y+25),30,COLORS["dark_text"],True)
    def run(self):
        while self.running:
            dt=self.clock.tick(60)/1000
            for e in pygame.event.get(): self.handle_event(e)
            self.update(dt); self.draw()
        pygame.quit()


class GameState:
    def __init__(self, game, names):
        self.game=game; self.players=[]; start=game["settings"].get("starting_money",1500)
        for i,n in enumerate(names): self.players.append({"id":i,"name":n,"money":start,"pos":0,"properties":[],"cards":[],"debts":[],"wait_turns":0,"bankrupt":False,"doubles":0})
        self.current=0; self.turn_count=1; self.last_roll=(1,1); self.rolling=False; self.roll_end=0; self.pending_steps=0; self.moving=False; self.move_timer=0; self.turn_rolled=False; self.logs=["Game started."]; self.winner=None; self.free_pool=0
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
                    if p["pos"]<old and self.game["rules"].get("pass_start_money_enabled"):
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
        if sq["type"] in ("property","railroad","utility"):
            owner=sq.get("owner")
            if owner is None: self.log("Available to buy or auction.")
            elif owner!=p["id"] and self.game["rules"].get("rent_enabled") and not sq.get("mortgaged"):
                rent=sq.get("rent",0)+sq.get("houses",0)*20+(100 if sq.get("hotel") else 0); self.pay(p,self.players[owner],rent,f"rent for {sq['name']}")
        for act in sq.get("actions",[]): self.apply_action(p,act,source=sq["name"])
        if self.last_roll[0] == self.last_roll[1] and self.game["rules"].get("double_reroll_enabled") and not p.get("wait_turns"):
            self.turn_rolled = False; self.log(f"{p['name']} rolled doubles and may roll again.")
        self.check_bankruptcy(); self.check_winner()
    def apply_action(self,p,act,source="Action"):
        t=act.get("type","none"); amt=int(act.get("amount",0) or 0); target=act.get("target")
        if t in ("none","buy","pay_rent"): return
        if t=="gain_money": p["money"]+=amt; self.log(f"{p['name']} gained {amt} from {source}.")
        elif t=="lose_money": p["money"]-=amt; self.log(f"{p['name']} paid {amt} for {source}.")
        elif t=="move_forward": self.move_direct(p, amt)
        elif t=="move_backward": self.move_direct(p, -amt)
        elif t=="go_to_square": self.move_to(p, int(target or 0))
        elif t=="go_to_jail": self.go_jail(p)
        elif t=="wait_turns": p["wait_turns"]+=max(1,amt); self.log(f"{p['name']} waits {amt} turns.")
        elif t=="reroll": self.turn_rolled=False; self.log("Roll again granted.")
        elif t=="draw_card": self.draw_card(p, target or "Chance")
        elif t=="collect_from_all":
            for o in self.players:
                if o["id"]!=p["id"] and not o["bankrupt"]: self.pay(o,p,amt,"card collection")
        elif t=="pay_all":
            for o in self.players:
                if o["id"]!=p["id"] and not o["bankrupt"]: self.pay(p,o,amt,"card payment")
        elif t=="repair_fee":
            owned=[self.square(i) for i in p["properties"]]; fee=sum(s.get("houses",0)*amt + (amt*4 if s.get("hotel") else 0) for s in owned)
            p["money"]-=fee; self.log(f"{p['name']} paid {fee} repair fees.")
        elif t=="transfer_to_player":
            target_id = int(target) if str(target).isdigit() else (p["id"] + 1) % len(self.players)
            other = self.players[target_id % len(self.players)]
            if other["id"] != p["id"] and not other["bankrupt"]: self.pay(p, other, amt, source)
        elif t=="jail_card": p["cards"].append({"name":"Get Out of Jail","action":make_action("message",message="Used jail card")}); self.log(f"{p['name']} received a get-out card.")
        elif t=="message": self.log(act.get("message") or f"Message from {source}")
        elif t=="timer": p.setdefault("timers",[]).append({"mode":"turns","due_turn":self.turn_count+max(1,amt),"action":make_action("gain_money",amt),"source":source}); self.log("Timer action scheduled.")
        elif t=="auction": self.log("Auction action is available through the Auction button.")
    def draw_card(self,p,deck_name):
        deck=self.game.get("card_decks",{}).get(deck_name,[])
        if not deck: self.log(deck_name+" deck is empty."); return
        card=random.choice(deck); self.log(f"Card drawn: {card.get('name','Card')} - {card.get('description','')}")
        if card.get("holdable"): p["cards"].append(card); self.log("Card kept in hand.")
        else: self.apply_action(p,card.get("action",make_action()),source=card.get("name","Card"))
    def pay(self,src,dst,amt,reason):
        src["money"]-=amt; dst["money"]+=amt; self.log(f"{src['name']} paid {dst['name']} {amt} ({reason}).")
    def move_direct(self,p,steps): p["pos"]=(p["pos"]+steps)%len(self.game["board"]); self.log(f"{p['name']} moved to {self.square(p['pos'])['name']}.")
    def move_to(self,p,pos): p["pos"]=pos%len(self.game["board"]); self.log(f"{p['name']} moved to {self.square(p['pos'])['name']}.")
    def go_jail(self,p):
        jail=next((i for i,s in enumerate(self.game["board"]) if s["type"]=="jail"),0); p["pos"]=jail; p["wait_turns"]=self.game["rules"].get("jail_turns",3); p["doubles"]=0; self.log(f"{p['name']} went to jail/waiting area.")
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
            if self.turn_count>=debt["due_turn"]:
                due=int(debt["principal"]*(1+debt.get("interest",0)/100)); p["money"]-=due; self.log(f"Debt due: {p['name']} paid {due}."); p["debts"].remove(debt)
            elif debt["due_turn"]-self.turn_count<=1: self.log(f"Debt warning for {p['name']}: due soon.")
    def check_bankruptcy(self):
        for p in self.players:
            if not p["bankrupt"] and p["money"]<0:
                p["bankrupt"]=True; self.log(f"{p['name']} is bankrupt.")
                for s in self.game["board"]:
                    if s.get("owner")==p["id"]: s["owner"]=None; s["houses"]=0; s["hotel"]=False; s["mortgaged"]=False
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
        layout=self.game["settings"].get("board_layout",BOARD_TYPES[0]); n=len(self.game["board"]); centers=[]
        if layout=="Circular path":
            cx,cy=rect.center; rad=min(rect.w,rect.h)*0.38
            for i in range(n):
                a=-math.pi/2+2*math.pi*i/n; centers.append((cx+math.cos(a)*rad,cy+math.sin(a)*rad))
        elif layout=="Free grid path":
            cols=math.ceil(math.sqrt(n)); rows=math.ceil(n/cols); cell=min(rect.w/(cols+1),rect.h/(rows+1))
            for i in range(n): centers.append((rect.x+cell*(1+i%cols),rect.y+cell*(1+i//cols)))
        else:
            per=max(1,n//4); left,right,top,bottom=rect.x+55,rect.right-55,rect.y+55,rect.bottom-55
            for i in range(n):
                side=i/per
                if side<1: t=(i%per)/per; centers.append((right-(right-left)*t,bottom))
                elif side<2: t=(i%per)/per; centers.append((left, bottom-(bottom-top)*t))
                elif side<3: t=(i%per)/per; centers.append((left+(right-left)*t,top))
                else: t=(i%per)/max(1,n-3*per); centers.append((right, top+(bottom-top)*t))
        for i,sq in enumerate(self.game["board"]):
            x,y=centers[i]; col=GROUP_COLORS.get(sq.get("color_group"),(100,116,139)); r=pygame.Rect(0,0,74,48); r.center=(x,y)
            ui.rounded(surf,r,(248,250,252),8,border=col,border_width=3,shadow=False)
            pygame.draw.rect(surf,col,(r.x,r.y,r.w,8),border_radius=4)
            ui.text(surf,sq["name"],(r.centerx,r.y+15),11,COLORS["dark_text"],True,max_width=66)
            if sq.get("owner") is not None:
                pygame.draw.circle(surf,PLAYER_COLORS[sq["owner"]%len(PLAYER_COLORS)],(r.right-10,r.bottom-10),6)
            if sq.get("houses",0): ui.text(surf,"H"+str(sq.get("houses")),(r.x+6,r.bottom-17),11,COLORS["good"])
            if sq.get("hotel"): ui.text(surf,"HOT",(r.x+6,r.bottom-17),11,COLORS["bad"])
        for idx,p in enumerate(self.players):
            if p["bankrupt"]: continue
            x,y=centers[p["pos"]]; off=((idx%3)-1)*12; oy=(idx//3)*12
            pulse=2 if idx==self.current and int(time.time()*4)%2==0 else 0
            pygame.draw.circle(surf,PLAYER_COLORS[idx%len(PLAYER_COLORS)],(int(x+off),int(y+oy)),11+pulse)
            ui.text(surf,str(idx+1),(x+off,y+oy),13,COLORS["white"],True)


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
