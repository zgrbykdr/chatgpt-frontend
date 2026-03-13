from __future__ import annotations

import random
from typing import List, Dict, Any

from board.board_loader import BoardLoader
from board.property_logic import PropertyLogic
from cards.deck_manager import DeckManager
from core.action_executor import ActionExecutor
from core.event_bus import EventBus
from core.game_state import GameState, PropertyState
from core.rule_engine import RuleEngine
from core.turn_manager import TurnManager
from players.player_model import Player


class GameEngine:
    def __init__(self, board_path: str, deck_paths: Dict[str, str], rules_path: str) -> None:
        board_json = BoardLoader.load(board_path)
        self.board = BoardLoader.load_board(board_path)
        self.rules = RuleEngine(board_json.get("rules", {}))
        if rules_path:
            import json
            with open(rules_path, "r", encoding="utf-8") as f:
                self.rules = RuleEngine(json.load(f))

        self.state = GameState(board_name=self.board.name)
        for sq in self.board.squares:
            if sq.type in {"property", "railroad", "utility"}:
                self.state.property_state[sq.id] = PropertyState()

        self.bus = EventBus()
        self.decks = DeckManager()
        for name, path in deck_paths.items():
            self.decks.load_deck(name, path)
        self.turns = TurnManager(self.state)
        self.actions = ActionExecutor(self)

    def add_players(self, players: List[Player]) -> None:
        self.state.players = players

    def current_player(self) -> Player:
        return self.state.players[self.state.current_turn]

    def push_message(self, msg: str) -> None:
        self.state.messages.append(msg)
        self.state.messages = self.state.messages[-8:]

    def roll_dice(self) -> List[int]:
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        self.state.last_roll = [d1, d2]
        return [d1, d2]

    def move_player(self, player: Player, steps: int) -> None:
        old = player.position
        size = len(self.board.squares)
        player.position = (player.position + steps) % size
        if steps > 0 and old + steps >= size:
            self.adjust_money(player, self.rules.get("go_reward", 200))
            self.push_message(f"{player.name} passed GO and collected reward")

    def move_player_to(self, player: Player, target: int) -> None:
        if target < player.position:
            self.adjust_money(player, self.rules.get("go_reward", 200))
        player.position = target

    def move_to_nearest_type(self, player: Player, target_type: str) -> None:
        pos = player.position
        for _ in range(len(self.board.squares)):
            pos = (pos + 1) % len(self.board.squares)
            if self.board.squares[pos].type == target_type:
                self.move_player_to(player, pos)
                return

    def adjust_money(self, player: Player, amount: int) -> None:
        player.money += amount
        if player.money < 0:
            player.bankrupt = True
            self.push_message(f"{player.name} is bankrupt")

    def pay_all_players(self, payer: Player, amount: int) -> None:
        for p in self.state.players:
            if p.player_id != payer.player_id and not p.bankrupt:
                payer.money -= amount
                p.money += amount

    def receive_from_all_players(self, receiver: Player, amount: int) -> None:
        for p in self.state.players:
            if p.player_id != receiver.player_id and not p.bankrupt:
                p.money -= amount
                receiver.money += amount

    def send_to_jail(self, player: Player) -> None:
        player.position = self.rules.get("jail_square", 10)
        player.in_jail = True
        player.jail_turns = 0
        self.push_message(f"{player.name} sent to jail")

    def draw_card(self, player: Player, deck_name: str | None) -> None:
        if not deck_name:
            return
        card = self.decks.draw(deck_name)
        self.push_message(f"Card: {card['title']}")
        for action in card.get("actions", []):
            self.actions.execute(action, player)
        self.bus.emit("card_drawn", card=card)

    def resolve_square(self, player: Player) -> None:
        sq = self.board.squares[player.position]
        if sq.type in {"property", "railroad", "utility"}:
            ps = self.state.property_state[sq.id]
            if ps.owner_id is None:
                self.push_message(f"{sq.name} available for ${sq.price}")
                self.state.turn_phase = "buy_or_auction"
            elif ps.owner_id != player.player_id:
                owner = next(p for p in self.state.players if p.player_id == ps.owner_id)
                due = PropertyLogic.rent_due(sq, ps.houses)
                self.adjust_money(player, -due)
                self.adjust_money(owner, due)
                self.push_message(f"{player.name} paid ${due} rent to {owner.name}")
        elif sq.type == "tax":
            amount = sq.tax or 100
            self.adjust_money(player, -amount)
            self.state.jail_pot += amount
            self.push_message(f"{player.name} paid tax ${amount}")
        elif sq.type == "card_draw":
            self.draw_card(player, sq.deck)
        elif sq.type == "go_to_jail":
            self.send_to_jail(player)
        elif sq.type == "free_parking" and self.rules.get("free_parking_rule", False):
            self.adjust_money(player, self.state.jail_pot)
            self.state.jail_pot = 0
        for action in sq.actions:
            self.actions.execute(action, player)

    def buy_current_property(self) -> None:
        p = self.current_player()
        sq = self.board.squares[p.position]
        if sq.type in {"property", "railroad", "utility"} and PropertyLogic.can_buy(p, sq, self.state):
            PropertyLogic.buy(p, sq, self.state)
            self.push_message(f"{p.name} bought {sq.name}")
        self.state.turn_phase = "idle"

    def end_turn(self) -> None:
        cp = self.current_player()
        if cp.skipped_turns > 0:
            cp.skipped_turns -= 1
        self.turns.advance()

    def take_turn(self) -> None:
        p = self.current_player()
        if p.bankrupt:
            self.end_turn()
            return
        if p.skipped_turns > 0:
            self.push_message(f"{p.name} skips turn")
            self.end_turn()
            return
        if p.in_jail:
            p.jail_turns += 1
            dice = self.roll_dice()
            if dice[0] == dice[1] or p.jail_turns >= 3:
                p.in_jail = False
                self.push_message(f"{p.name} leaves jail")
            else:
                self.push_message(f"{p.name} remains in jail")
                self.end_turn()
                return
        d1, d2 = self.roll_dice()
        self.move_player(p, d1 + d2)
        self.resolve_square(p)
        if d1 != d2 or self.state.turn_phase == "buy_or_auction":
            self.end_turn()
