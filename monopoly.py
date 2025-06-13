import json
import os
import random
import datetime

try:
    import pygame
except ImportError:  # pragma: no cover - dependency install
    print("pygame not found, attempting to install...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

BOARD_FILE = "board.json"
CHANCE_FILE = "chance.json"
COMMUNITY_FILE = "community.json"

DIAGNOSTIC = True
ERROR_LOG = "errorlog.txt"

ERROR_CODES = {
    "JSON_LOAD": 1001,
    "PYGAME_INIT": 1002,
    "RUN_LOOP": 1003,
    "UNEXPECTED": 1999,
}

def log_error(code, message):
    if not DIAGNOSTIC:
        return
    line = f"{datetime.datetime.now().isoformat()} {code} {message}\n"
    with open(ERROR_LOG, "a") as f:
        f.write(line)

# Utility functions to load config

def load_json(path, default):
    if not os.path.exists(path):
        log_error(ERROR_CODES["JSON_LOAD"], f"{path} not found")
        return default
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_error(ERROR_CODES["JSON_LOAD"], f"Failed to parse {path}: {e}")
        return default


def default_board():
    return load_json(BOARD_FILE, [])


def default_chance():
    return load_json(CHANCE_FILE, [])


def default_community():
    return load_json(COMMUNITY_FILE, [])


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.position = 0
        self.money = 1500
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail = 0


class Game:
    def __init__(self, board, chance, community, players):
        self.board = board
        self.chance = chance
        self.community = community
        self.players = players
        self.turn = 0

        # Pygame setup
        try:
            pygame.init()
        except Exception as e:
            log_error(ERROR_CODES["PYGAME_INIT"], str(e))
            raise
        info = pygame.display.Info()
        self.width, self.height = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Monopoly")
        self.font = pygame.font.SysFont(None, 24)
        self.clock = pygame.time.Clock()

        # Layout
        self.cell = min(self.width, self.height) // 11
        self.margin_x = (self.width - self.cell * 11) // 2
        self.margin_y = (self.height - self.cell * 11) // 2

    def square_pos(self, index):
        # Map square index to screen coordinates along board edge
        c = self.cell
        if index < 11:  # bottom row right->left
            x = self.margin_x + c * (10 - index)
            y = self.margin_y + c * 10
        elif index < 20:  # left column bottom->top
            x = self.margin_x
            y = self.margin_y + c * (20 - index)
        elif index < 30:  # top row left->right
            x = self.margin_x + c * (index - 20)
            y = self.margin_y
        else:  # right column top->bottom
            x = self.margin_x + c * 10
            y = self.margin_y + c * (index - 30)
        return x, y

    def draw_board(self):
        c = self.cell
        for i, sq in enumerate(self.board):
            x, y = self.square_pos(i)
            rect = pygame.Rect(x, y, c, c)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
            name_surf = self.font.render(sq.get('name', '')[:8], True, (255, 255, 255))
            self.screen.blit(name_surf, (x + 2, y + 2))

    def draw_players(self):
        for p in self.players:
            x, y = self.square_pos(p.position)
            token_size = self.cell // 4
            pygame.draw.circle(self.screen, p.color, (x + self.cell // 2, y + self.cell // 2), token_size)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.draw_board()
        self.draw_players()
        pygame.display.flip()

    def log(self, msg):
        print(msg)

    def roll_dice(self):
        return random.randint(1, 6), random.randint(1, 6)

    def move_player(self, player, steps):
        old = player.position
        player.position = (player.position + steps) % len(self.board)
        if old + steps >= len(self.board):
            player.money += 200
            self.log(f"{player.name} passed GO and collects $200")
        self.handle_square(player)

    def draw_card(self, player, deck):
        card = deck.pop(0)
        deck.append(card)
        self.log(f"{player.name} drew card: {card['text']}")
        if card.get('moveTo') is not None:
            player.position = card['moveTo']
            self.handle_square(player)
        if card.get('money'):
            player.money += card['money']
        if card.get('gotoJail'):
            player.position = 10
            player.in_jail = True
            player.jail_turns = 3

    def handle_square(self, player):
        sq = self.board[player.position]
        action = sq.get('action')
        if action:
            if 'money' in action:
                player.money += action['money']
                self.log(f"{player.name} {'receives' if action['money']>=0 else 'pays'} ${abs(action['money'])}")
            if 'moveBy' in action:
                self.move_player(player, action['moveBy'])
                return
            if 'moveTo' in action:
                player.position = action['moveTo'] % len(self.board)
                sq = self.board[player.position]
                self.log(f"{player.name} moves to {sq.get('name','')}")
            if action.get('gotoJail'):
                player.position = 10
                player.in_jail = True
                player.jail_turns = 3
                self.log(f"{player.name} was sent to Jail")
                return

        t = sq.get('type')
        if t == 'property':
            if sq.get('owner') is None:
                if player.money >= sq['price']:
                    player.money -= sq['price']
                    sq['owner'] = player.name
                    player.properties.append(player.position)
                    self.log(f"{player.name} bought {sq['name']} for ${sq['price']}")
            elif sq.get('owner') != player.name:
                rent = sq.get('rent', 0)
                player.money -= rent
                for p in self.players:
                    if p.name == sq['owner']:
                        p.money += rent
                self.log(f"{player.name} paid ${rent} rent for {sq['name']}")
        elif t == 'tax':
            tax = sq.get('price', 0)
            player.money -= tax
            self.log(f"{player.name} paid tax of ${tax}")
        elif t == 'chance':
            self.draw_card(player, self.chance)
        elif t == 'community':
            self.draw_card(player, self.community)
        elif t == 'gotojail':
            player.position = 10
            player.in_jail = True
            player.jail_turns = 3
            self.log(f"{player.name} was sent to Jail")

    def next_turn(self):
        player = self.players[self.turn]
        if player.in_jail:
            player.jail_turns -= 1
            if player.jail_turns <= 0:
                player.in_jail = False
            else:
                self.log(f"{player.name} is in jail")
                self.turn = (self.turn + 1) % len(self.players)
                return
        d1, d2 = self.roll_dice()
        self.log(f"{player.name} rolled {d1}+{d2}")
        self.move_player(player, d1 + d2)
        self.turn = (self.turn + 1) % len(self.players)

    def run(self):
        running = True
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.next_turn()
                self.draw()
                self.clock.tick(30)
        except Exception as e:
            log_error(ERROR_CODES["RUN_LOOP"], str(e))
            raise
        finally:
            pygame.quit()


if __name__ == "__main__":
    board = default_board()
    chance = default_chance()
    community = default_community()
    players = [
        Player("Player 1", (255, 0, 0)),
        Player("Player 2", (0, 255, 0))
    ]
    game = Game(board, chance, community, players)
    try:
        game.run()
    except Exception as e:
        log_error(ERROR_CODES["UNEXPECTED"], str(e))

