from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class Player:
    name: str
    token: str
    cash: int = 1500
    position: int = 0
    in_jail: bool = False
    jail_turns: int = 0
    get_out_of_jail_cards: int = 0
    properties: List[int] = field(default_factory=list)
    mortgaged: List[int] = field(default_factory=list)


@dataclass
class PropertyState:
    owner_index: Optional[int] = None
    houses: int = 0  # 0-4 houses, 5 == hotel
    mortgaged: bool = False


class Game:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.squares: List[Dict[str, Any]] = config["board"]["squares"]
        self.num_squares = len(self.squares)
        self.currency = config["board"].get("currency", "$")
        self.go_salary = config["board"].get("go_salary", 200)
        self.jail_index = self._find_square_index("jail")
        self.go_to_jail_index = self._find_square_index("go_to_jail")

        # State
        self.players: List[Player] = [
            Player(name="Player 1", token="🚗"),
            Player(name="Player 2", token="🐶"),
        ]
        self.current_player_index = 0
        self.properties_state: Dict[int, PropertyState] = {
            i: PropertyState() for i, sq in enumerate(self.squares) if sq["type"] in {"property", "railroad", "utility"}
        }
        self.doubles_in_row: int = 0
        self.last_dice: Tuple[int, int] = (0, 0)

        # Decks
        self.chance_deck = list(self.config["chance"])  # shallow copy
        self.community_deck = list(self.config["community_chest"])  # shallow copy
        random.shuffle(self.chance_deck)
        random.shuffle(self.community_deck)

        # UI event log
        self.log: List[str] = []

    # --- Helpers ---
    def _find_square_index(self, square_type: str) -> int:
        for idx, sq in enumerate(self.squares):
            if sq["type"] == square_type:
                return idx
        return -1

    def append_log(self, message: str) -> None:
        self.log.append(message)

    # --- Turn / Dice ---
    def roll_dice(self) -> Tuple[int, int, bool]:
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        doubles = die1 == die2
        return die1, die2, doubles

    def take_turn(self) -> Dict[str, Any]:
        player = self.players[self.current_player_index]
        if player.in_jail:
            return {"phase": "jail"}
        d1, d2, doubles = self.roll_dice()
        self.last_dice = (d1, d2)
        self.append_log(f"{player.name} rolled {d1} and {d2}{' (doubles)' if doubles else ''}.")
        if doubles:
            self.doubles_in_row += 1
            if self.doubles_in_row >= 3:
                # go to jail immediately
                self.append_log(f"{player.name} rolled three doubles in a row and is sent to Jail.")
                self._handle_go_to_jail(player)
                self.doubles_in_row = 0
                return {"actions": [], "dice": (d1, d2), "doubles": True, "landed": player.position}
        else:
            self.doubles_in_row = 0
        passed_go = self._move_player(player, d1 + d2)
        if passed_go:
            self._collect_go(player)
        landed_index = player.position
        square = self.squares[landed_index]
        self.append_log(f"{player.name} landed on {square.get('name', square['type'])}.")
        actions = self._resolve_landing(player, landed_index)
        actions.update({"dice": (d1, d2), "doubles": doubles, "landed": landed_index})
        return actions

    def end_turn(self) -> None:
        self.current_player_index = 1 - self.current_player_index
        self.doubles_in_row = 0

    # --- Movement ---
    def _move_player(self, player: Player, steps: int) -> bool:
        start = player.position
        new_pos = (player.position + steps) % self.num_squares
        player.position = new_pos
        return new_pos < start

    def _collect_go(self, player: Player) -> None:
        player.cash += self.go_salary
        self.append_log(f"{player.name} collected {self.currency}{self.go_salary} for passing GO.")

    # --- Landing resolution ---
    def _resolve_landing(self, player: Player, index: int) -> Dict[str, Any]:
        sq = self.squares[index]
        t = sq["type"]
        if t in {"property", "railroad", "utility"}:
            return self._handle_property_like(player, index)
        if t == "tax":
            return self._handle_tax(player, sq)
        if t == "chance":
            return self._draw_card(player, deck="chance")
        if t == "community_chest":
            return self._draw_card(player, deck="community")
        if t == "go_to_jail":
            return self._handle_go_to_jail(player)
        # go, jail, free_parking etc.
        return {"actions": [], "message": "No action"}

    # --- Property / Rent ---
    def _handle_property_like(self, player: Player, index: int) -> Dict[str, Any]:
        state = self.properties_state[index]
        sq = self.squares[index]
        if state.owner_index is None:
            price = sq.get("price", 0)
            can_buy = player.cash >= price
            return {"actions": ["buy", "auction"], "price": price, "can_buy": can_buy}
        if state.owner_index == self.current_player_index:
            return {"actions": [], "message": "Own property"}
        # pay rent
        rent = self._calculate_rent(index)
        if rent > 0:
            self._transfer_cash(self.current_player_index, state.owner_index, rent)
        return {"actions": [], "message": f"Paid rent {self.currency}{rent}"}

    def _calculate_rent(self, index: int) -> int:
        sq = self.squares[index]
        state = self.properties_state[index]
        if sq["type"] == "railroad":
            owner = state.owner_index
            rr_owned = sum(1 for i, st in self.properties_state.items() if self.squares[i]["type"] == "railroad" and st.owner_index == owner)
            return [25, 50, 100, 200][rr_owned - 1]
        if sq["type"] == "utility":
            owner = state.owner_index
            util_owned = sum(1 for i, st in self.properties_state.items() if self.squares[i]["type"] == "utility" and st.owner_index == owner)
            mult = 0 if owner is None else (4 if util_owned == 1 else 10)
            return mult * sum(self.last_dice) if mult else 0
        # properties
        houses = state.houses
        rent_table = sq.get("rent", [0, 0, 0, 0, 0, 0])
        # 0: base, 1-4: with houses, 5: hotel
        rent = rent_table[min(houses, 5)]
        # monopoly (no houses): double rent
        if houses == 0 and self._has_monopoly(state.owner_index, sq.get("color")):
            rent *= 2
        return rent

    def _has_monopoly(self, owner_index: Optional[int], color: Optional[str]) -> bool:
        if owner_index is None or not color:
            return False
        group_indices = [i for i, s in enumerate(self.squares) if s.get("color") == color]
        return all(self.properties_state[i].owner_index == owner_index for i in group_indices)

    # --- Cash / Banking ---
    def _transfer_cash(self, payer_index: int, receiver_index: int, amount: int) -> None:
        payer = self.players[payer_index]
        receiver = self.players[receiver_index]
        payer.cash -= amount
        receiver.cash += amount
        self.append_log(f"{payer.name} paid {self.currency}{amount} to {receiver.name}.")

    def pay_bank(self, player_index: int, amount: int) -> None:
        player = self.players[player_index]
        player.cash -= amount
        self.append_log(f"{player.name} paid bank {self.currency}{amount}.")

    def receive_from_bank(self, player_index: int, amount: int) -> None:
        player = self.players[player_index]
        player.cash += amount
        self.append_log(f"{player.name} received {self.currency}{amount} from bank.")

    # --- Property actions ---
    def buy_property(self, index: int) -> bool:
        player = self.players[self.current_player_index]
        sq = self.squares[index]
        price = sq.get("price", 0)
        if self.properties_state[index].owner_index is not None:
            return False
        if player.cash < price:
            return False
        player.cash -= price
        self.properties_state[index].owner_index = self.current_player_index
        player.properties.append(index)
        self.append_log(f"{player.name} bought {sq.get('name')} for {self.currency}{price}.")
        return True

    # --- Taxes ---
    def _handle_tax(self, player: Player, sq: Dict[str, Any]) -> Dict[str, Any]:
        mode = sq.get("mode", "flat")
        if mode == "flat":
            amount = sq.get("amount", 0)
            self.pay_bank(self.current_player_index, amount)
            return {"actions": [], "message": f"Paid tax {self.currency}{amount}"}
        # either mode: pay amount or percent of total worth (simplified: cash only)
        amount = sq.get("amount", 200)
        percent = sq.get("percent", 10)
        percent_amount = int(self.total_worth(self.current_player_index) * percent / 100)
        return {"actions": ["choose_tax"], "flat": amount, "percent": percent_amount}

    def choose_tax(self, choice: str) -> None:
        player_index = self.current_player_index
        sq = self.squares[self.players[player_index].position]
        amount = sq.get("amount", 200)
        percent_amount = int(self.total_worth(player_index) * sq.get("percent", 10) / 100)
        pay = amount if choice == "flat" else percent_amount
        self.pay_bank(player_index, pay)

    def total_worth(self, player_index: int) -> int:
        player = self.players[player_index]
        prop_value = sum(self.squares[i].get("price", 0) for i in player.properties)
        return player.cash + prop_value

    # --- Cards ---
    def _draw_card(self, player: Player, deck: str) -> Dict[str, Any]:
        if deck == "chance":
            card = self.chance_deck.pop(0)
            self.chance_deck.append(card)
        else:
            card = self.community_deck.pop(0)
            self.community_deck.append(card)
        self.append_log(f"{player.name} drew: {card['description']}")
        return self._execute_card(player, card)

    def _execute_card(self, player: Player, card: Dict[str, Any]) -> Dict[str, Any]:
        ctype = card["type"]
        if ctype == "collect":
            self.receive_from_bank(self.current_player_index, card["amount"])
            return {"actions": []}
        if ctype == "pay":
            self.pay_bank(self.current_player_index, card["amount"])
            return {"actions": []}
        if ctype == "move_to":
            passed_go = self._move_to(player, card["target"])  # move without dice
            if passed_go:
                self._collect_go(player)
            return self._resolve_landing(player, player.position)
        if ctype == "nearest_railroad":
            idx = self._nearest_of_type(player.position, "railroad")
            passed_go = self._move_to(player, idx)
            if passed_go:
                self._collect_go(player)
            # pay double rent if owned
            state = self.properties_state[idx]
            if state.owner_index is not None and state.owner_index != self.current_player_index:
                rent = self._calculate_rent(idx) * 2
                self._transfer_cash(self.current_player_index, state.owner_index, rent)
            return {"actions": []}
        if ctype == "nearest_utility":
            idx = self._nearest_of_type(player.position, "utility")
            passed_go = self._move_to(player, idx)
            if passed_go:
                self._collect_go(player)
            # If owned, pay 10x dice
            state = self.properties_state[idx]
            if state.owner_index is not None and state.owner_index != self.current_player_index:
                saved = self.last_dice
                # roll dice to determine payment
                d1, d2, _ = self.roll_dice()
                self.last_dice = (d1, d2)
                mult = 10
                rent = mult * (d1 + d2)
                self._transfer_cash(self.current_player_index, state.owner_index, rent)
                self.last_dice = saved
            return {"actions": []}
        if ctype == "out_of_jail_free":
            player.get_out_of_jail_cards += 1
            return {"actions": []}
        if ctype == "go_to_jail":
            return self._handle_go_to_jail(player)
        if ctype == "repairs":
            # simplified: charge per house/hotel owned
            house_cost = card.get("house", 25)
            hotel_cost = card.get("hotel", 100)
            total_houses = sum(1 for st in self.properties_state.values() if st.houses in (1, 2, 3, 4))
            total_hotels = sum(1 for st in self.properties_state.values() if st.houses >= 5)
            amount = total_houses * house_cost + total_hotels * hotel_cost
            self.pay_bank(self.current_player_index, amount)
            return {"actions": []}
        if ctype == "pay_each_player":
            amount = card["amount"]
            for i, _ in enumerate(self.players):
                if i == self.current_player_index:
                    continue
                self._transfer_cash(self.current_player_index, i, amount)
            return {"actions": []}
        if ctype == "collect_from_each_player":
            amount = card["amount"]
            for i, _ in enumerate(self.players):
                if i == self.current_player_index:
                    continue
                self._transfer_cash(i, self.current_player_index, amount)
            return {"actions": []}
        if ctype == "move_back":
            steps = card["spaces"]
            player.position = (player.position - steps) % self.num_squares
            return self._resolve_landing(player, player.position)
        return {"actions": []}

    def _move_to(self, player: Player, target_index: int) -> bool:
        start = player.position
        player.position = target_index
        return target_index < start

    def _nearest_of_type(self, start_index: int, t: str) -> int:
        for offset in range(1, self.num_squares + 1):
            idx = (start_index + offset) % self.num_squares
            if self.squares[idx]["type"] == t:
                return idx
        return start_index

    # --- Jail ---
    def _handle_go_to_jail(self, player: Player) -> Dict[str, Any]:
        player.in_jail = True
        player.position = self.jail_index if self.jail_index >= 0 else player.position
        player.jail_turns = 0
        self.append_log(f"{player.name} was sent to Jail.")
        return {"actions": []}

    def pay_jail_fine(self) -> bool:
        player = self.players[self.current_player_index]
        fine = self.config["board"].get("jail_fine", 50)
        if player.cash < fine:
            return False
        player.cash -= fine
        player.in_jail = False
        player.jail_turns = 0
        self.append_log(f"{player.name} paid jail fine {self.currency}{fine}.")
        return True

    def use_get_out_of_jail(self) -> bool:
        player = self.players[self.current_player_index]
        if player.get_out_of_jail_cards <= 0:
            return False
        player.get_out_of_jail_cards -= 1
        player.in_jail = False
        player.jail_turns = 0
        self.append_log(f"{player.name} used a Get Out of Jail Free card.")
        return True