from __future__ import annotations

import json
from pathlib import Path

from board.square_actions import execute_square_type
from cards.card_executor import CardExecutor
from cards.deck_manager import DeckManager
from core.action_executor import ActionExecutor
from core.game_state import GameState, PropertyState
from core.rule_engine import RuleEngine
from core.turn_manager import TurnManager


class GameEngine:
    def __init__(self, state: GameState, deck_dir: str | Path):
        self.state = state
        self.rule_engine = RuleEngine(state.rules)
        self.turn_manager = TurnManager()
        self.action_executor = ActionExecutor(self)
        self.deck_manager = DeckManager(deck_dir)
        self.card_executor = CardExecutor(self)
        self.state.ensure_property_map()

    @classmethod
    def from_files(cls, board, rules_file: str, deck_dir: str | Path):
        with open(rules_file, "r", encoding="utf-8") as handle:
            rules = json.load(handle)
        state = GameState(board=board, rules=rules, players=[])
        return cls(state, deck_dir)

    def add_player(self, player):
        self.state.players.append(player)

    def setup_default_decks(self):
        for candidate in ["chance.json", "community_chest.json"]:
            self.deck_manager.load_deck(candidate)

    def current_player(self):
        return self.state.players[self.state.current_player_index]

    def next_turn(self):
        if self.state.game_over:
            return
        idx = self.state.current_player_index
        for _ in range(len(self.state.players)):
            idx = (idx + 1) % len(self.state.players)
            if self.state.players[idx].active and not self.state.players[idx].bankrupt:
                self.state.current_player_index = idx
                break
        self.state.turn_number += 1

    def play_turn(self):
        player = self.current_player()
        if player.skip_turns > 0:
            player.skip_turns -= 1
            self.state.messages.append(f"{player.name} skips a turn.")
            self.next_turn()
            return

        if player.in_jail:
            player.jail_turns += 1
            if player.jail_turns >= self.state.rules.get("jail_exit_methods", {}).get("wait_turns", 3):
                player.money -= self.state.rules.get("jail_exit_methods", {}).get("pay_money", 50)
                player.in_jail = False
                player.jail_turns = 0
            else:
                self.state.messages.append(f"{player.name} is in jail.")
                self.next_turn()
                return

        die1, die2 = self.turn_manager.roll_dice()
        steps = die1 + die2
        self.move_player_steps(player, steps)

        square = self.state.board.get_square(player.position)
        if square:
            execute_square_type(self, player, square.id)
            for action in square.actions:
                self.action_executor.execute(player, {"type": action.type, **action.params})

        self.check_bankruptcy(player)
        self.check_winner()

        if not self.turn_manager.is_double() or not self.state.rules.get("double_roll_extra_turn", True):
            self.next_turn()

    def move_player_steps(self, player, steps: int):
        board_size = self.state.board.size
        start = player.position
        end = (start + steps) % board_size
        if steps > 0 and start + steps >= board_size:
            player.money += self.rule_engine.go_reward
            self.state.messages.append(f"{player.name} passed GO (+{self.rule_engine.go_reward}).")
        player.position = end

    def move_player_to(self, player, target: int, collect_go: bool = True):
        if collect_go and target < player.position:
            player.money += self.rule_engine.go_reward
        player.position = target

    def handle_property_landing(self, player, square):
        prop = self.state.property_state.setdefault(square.id, PropertyState())
        if prop.owner is None:
            if player.money >= square.price:
                player.money -= square.price
                prop.owner = self.state.players.index(player)
                player.owned_properties.append(square.id)
                self.state.messages.append(f"{player.name} bought {square.name} for {square.price}.")
        elif prop.owner != self.state.players.index(player):
            owner = self.state.players[prop.owner]
            rent_index = min(prop.houses + (1 if prop.hotel else 0), max(0, len(square.rent) - 1))
            rent = square.rent[rent_index] if square.rent else max(10, square.price // 10)
            self.transfer_money(player, owner, rent)
            self.state.messages.append(f"{player.name} paid {rent} rent to {owner.name}.")

    def draw_and_apply_card(self, player, deck_name: str):
        if deck_name not in self.deck_manager.decks:
            return
        card = self.deck_manager.draw(deck_name)
        self.card_executor.apply(player, card)

    def transfer_money(self, src, dst, amount: int):
        src.money -= amount
        dst.money += amount
        self.check_bankruptcy(src)

    def charge_player(self, player, amount: int, reason: str = ""):
        player.money -= amount
        self.state.messages.append(f"{player.name} pays {amount}. {reason}")
        self.check_bankruptcy(player)

    def send_player_to_jail(self, player):
        player.position = self.rule_engine.jail_square
        player.in_jail = True
        player.jail_turns = 0
        self.state.messages.append(f"{player.name} sent to Jail.")

    def check_bankruptcy(self, player):
        if player.money >= 0:
            return
        player.bankrupt = True
        player.active = False
        for prop_id in list(player.owned_properties):
            self.state.property_state[prop_id].owner = None
        player.owned_properties.clear()
        self.state.messages.append(f"{player.name} is bankrupt!")

    def check_winner(self):
        remaining = [i for i, p in enumerate(self.state.players) if p.active and not p.bankrupt]
        if len(remaining) == 1 and len(self.state.players) > 1:
            self.state.game_over = True
            self.state.winner = remaining[0]
