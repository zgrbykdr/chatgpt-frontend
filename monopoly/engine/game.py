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

        self.house_costs: Dict[str, int] = config["board"].get("house_costs", {})
        self.bank_houses: int = config["board"].get("bank_houses", 32)
        self.bank_hotels: int = config["board"].get("bank_hotels", 12)

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
        self.must_roll_again: bool = False

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
                self.must_roll_again = False
                return {"actions": [], "dice": (d1, d2), "doubles": True, "landed": player.position, "extra_turn": False}
            else:
                self.must_roll_again = True
        else:
            self.doubles_in_row = 0
            self.must_roll_again = False
        passed_go = self._move_player(player, d1 + d2)
        if passed_go:
            self._collect_go(player)
        landed_index = player.position
        square = self.squares[landed_index]
        self.append_log(f"{player.name} landed on {square.get('name', square['type'])}.")
        actions = self._resolve_landing(player, landed_index)
        actions.update({"dice": (d1, d2), "doubles": doubles, "landed": landed_index, "extra_turn": self.must_roll_again})
        return actions

    def end_turn(self) -> None:
        if self.must_roll_again:
            self.append_log("You rolled doubles. Roll again before ending your turn.")
            return
        self.current_player_index = 1 - self.current_player_index
        self.doubles_in_row = 0
        self.must_roll_again = False

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
        if state.mortgaged:
            return {"actions": [], "message": "No rent on mortgaged property"}
        # pay rent
        rent = self._calculate_rent(index)
        if rent > 0:
            self._transfer_cash(self.current_player_index, state.owner_index, rent)
        return {"actions": [], "message": f"Paid rent {self.currency}{rent}"}

    def _calculate_rent(self, index: int) -> int:
        sq = self.squares[index]
        state = self.properties_state[index]
        if state.owner_index is None or state.mortgaged:
            return 0
        if sq["type"] == "railroad":
            owner = state.owner_index
            rr_owned = sum(1 for i, st in self.properties_state.items() if self.squares[i]["type"] == "railroad" and st.owner_index == owner and not st.mortgaged)
            return [25, 50, 100, 200][rr_owned - 1]
        if sq["type"] == "utility":
            owner = state.owner_index
            util_owned = sum(1 for i, st in self.properties_state.items() if self.squares[i]["type"] == "utility" and st.owner_index == owner and not st.mortgaged)
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

    def auction_buy(self, index: int, buyer_index: int, price: int) -> bool:
        sq = self.squares[index]
        state = self.properties_state[index]
        if state.owner_index is not None:
            return False
        buyer = self.players[buyer_index]
        if buyer.cash < price:
            return False
        buyer.cash -= price
        state.owner_index = buyer_index
        buyer.properties.append(index)
        self.append_log(f"{buyer.name} won auction for {sq.get('name')} at {self.currency}{price}.")
        return True

    # --- Build/Sell ---
    def can_build(self, index: int) -> Tuple[bool, str]:
        sq = self.squares[index]
        state = self.properties_state[index]
        if sq.get("type") != "property":
            return False, "Not a buildable property"
        if state.owner_index != self.current_player_index:
            return False, "Not your property"
        color = sq.get("color")
        if not self._has_monopoly(self.current_player_index, color):
            return False, "Need full color set"
        if any(self.properties_state[i].mortgaged for i, s in enumerate(self.squares) if s.get("color") == color):
            return False, "Group has a mortgaged property"
        cost = self.house_costs.get(color, 0)
        if cost <= 0:
            return False, "No house cost configured"
        if state.houses < 4:
            if self.bank_houses <= 0:
                return False, "No houses left in bank"
        else:
            if self.bank_hotels <= 0:
                return False, "No hotels left in bank"
        # even building check
        group_indices = [i for i, s in enumerate(self.squares) if s.get("color") == color]
        min_houses = min(self.properties_state[i].houses for i in group_indices)
        if state.houses > min_houses:
            return False, "Must build evenly across the group"
        return True, "OK"

    def build_house(self, index: int) -> bool:
        ok, _ = self.can_build(index)
        if not ok:
            return False
        sq = self.squares[index]
        state = self.properties_state[index]
        color = sq.get("color")
        cost = self.house_costs.get(color, 0)
        player = self.players[self.current_player_index]
        if player.cash < cost:
            return False
        if state.houses < 4:
            player.cash -= cost
            state.houses += 1
            self.bank_houses -= 1
            self.append_log(f"{player.name} built a house on {sq.get('name')} for {self.currency}{cost}.")
            return True
        # upgrade to hotel
        if self.bank_hotels <= 0:
            return False
        # When buying a hotel, return 4 houses to bank
        player.cash -= cost
        state.houses = 5
        self.bank_hotels -= 1
        self.bank_houses += 4
        self.append_log(f"{player.name} built a hotel on {sq.get('name')} for {self.currency}{cost}.")
        return True

    def can_sell_house(self, index: int) -> Tuple[bool, str]:
        sq = self.squares[index]
        state = self.properties_state[index]
        if sq.get("type") != "property":
            return False, "Not a buildable property"
        if state.owner_index != self.current_player_index:
            return False, "Not your property"
        if state.houses <= 0:
            return False, "No houses/hotel to sell"
        color = sq.get("color")
        group_indices = [i for i, s in enumerate(self.squares) if s.get("color") == color]
        max_houses = max(self.properties_state[i].houses for i in group_indices)
        if state.houses < max_houses:
            return False, "Must sell evenly across the group"
        if state.houses == 5 and self.bank_houses < 4:
            return False, "Bank lacks 4 houses to downgrade hotel"
        return True, "OK"

    def sell_house(self, index: int) -> bool:
        ok, _ = self.can_sell_house(index)
        if not ok:
            return False
        sq = self.squares[index]
        state = self.properties_state[index]
        color = sq.get("color")
        refund = self.house_costs.get(color, 0) // 2
        player = self.players[self.current_player_index]
        if state.houses == 5:
            # sell hotel -> 4 houses if available
            state.houses = 4
            self.bank_hotels += 1
            self.bank_houses -= 4
            player.cash += refund
            self.append_log(f"{player.name} sold a hotel on {sq.get('name')} and received {self.currency}{refund}.")
            return True
        # sell house
        state.houses -= 1
        self.bank_houses += 1
        player.cash += refund
        self.append_log(f"{player.name} sold a house on {sq.get('name')} and received {self.currency}{refund}.")
        return True

    # --- Mortgages ---
    def can_mortgage(self, index: int) -> Tuple[bool, str]:
        sq = self.squares[index]
        state = self.properties_state[index]
        if state.owner_index != self.current_player_index:
            return False, "Not your property"
        if state.mortgaged:
            return False, "Already mortgaged"
        if sq.get("type") == "property":
            color = sq.get("color")
            group_indices = [i for i, s in enumerate(self.squares) if s.get("color") == color]
            if any(self.properties_state[i].houses > 0 for i in group_indices):
                return False, "Sell buildings in the group first"
        if state.houses > 0:
            return False, "Sell buildings first"
        return True, "OK"

    def mortgage(self, index: int) -> bool:
        ok, _ = self.can_mortgage(index)
        if not ok:
            return False
        sq = self.squares[index]
        state = self.properties_state[index]
        player = self.players[self.current_player_index]
        mortgage_value = sq.get("price", 0) // 2
        state.mortgaged = True
        player.mortgaged.append(index)
        player.cash += mortgage_value
        self.append_log(f"{player.name} mortgaged {sq.get('name')} for {self.currency}{mortgage_value}.")
        return True

    def can_unmortgage(self, index: int) -> Tuple[bool, str, int]:
        sq = self.squares[index]
        state = self.properties_state[index]
        if state.owner_index != self.current_player_index:
            return False, "Not your property", 0
        if not state.mortgaged:
            return False, "Not mortgaged", 0
        base = sq.get("price", 0) // 2
        cost = base + (base // 10)
        return True, "OK", cost

    def unmortgage(self, index: int) -> bool:
        ok, _, cost = self.can_unmortgage(index)
        if not ok:
            return False
        player = self.players[self.current_player_index]
        if player.cash < cost:
            return False
        sq = self.squares[index]
        state = self.properties_state[index]
        player.cash -= cost
        state.mortgaged = False
        if index in player.mortgaged:
            player.mortgaged.remove(index)
        self.append_log(f"{player.name} unmortgaged {sq.get('name')} by paying {self.currency}{cost}.")
        return True

    # --- Taxes ---
    def _handle_tax(self, player: Player, sq: Dict[str, Any]) -> Dict[str, Any]:
        mode = sq.get("mode", "flat")
        if mode == "flat":
            amount = sq.get("amount", 0)
            self.pay_bank(self.current_player_index, amount)
            return {"actions": [], "message": f"Paid tax {self.currency}{amount}"}
        # either mode: pay amount or percent of total worth (simplified: cash+property price)
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
                # Use last rolled dice; if none, roll now
                if sum(self.last_dice) == 0:
                    d1, d2, _ = self.roll_dice()
                    self.last_dice = (d1, d2)
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
                d1, d2, _ = self.roll_dice()
                saved = self.last_dice
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
            # simplified per building owned
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

    def jail_roll(self) -> Dict[str, Any]:
        player = self.players[self.current_player_index]
        if not player.in_jail:
            return {"actions": []}
        d1, d2, doubles = self.roll_dice()
        self.append_log(f"{player.name} rolled {d1} and {d2} in Jail.")
        if doubles:
            player.in_jail = False
            player.jail_turns = 0
            self.last_dice = (d1, d2)
            passed_go = self._move_player(player, d1 + d2)
            if passed_go:
                self._collect_go(player)
            landed = player.position
            self.append_log(f"{player.name} leaves Jail and moves {d1+d2} spaces.")
            return self._resolve_landing(player, landed)
        player.jail_turns += 1
        if player.jail_turns >= 3:
            # must pay fine (or cannot? In official rules, you must pay) and move by roll
            fine = self.config["board"].get("jail_fine", 50)
            if player.cash >= fine:
                player.cash -= fine
            player.in_jail = False
            player.jail_turns = 0
            self.last_dice = (d1, d2)
            passed_go = self._move_player(player, d1 + d2)
            if passed_go:
                self._collect_go(player)
            landed = player.position
            self.append_log(f"{player.name} leaves Jail after 3 turns and pays {self.currency}{fine}.")
            return self._resolve_landing(player, landed)
        return {"actions": [], "message": "No doubles. Remain in Jail."}

    # --- Trading ---
    def apply_trade(self, offer: Dict[str, Any]) -> bool:
        # offer = {from: idx, to: idx, cash_from: int, cash_to: int, props_from: [idx], props_to: [idx], goj_from: int, goj_to: int}
        a = offer.get("from")
        b = offer.get("to")
        if a is None or b is None or a == b:
            return False
        pa = self.players[a]
        pb = self.players[b]
        cash_from = int(offer.get("cash_from", 0))
        cash_to = int(offer.get("cash_to", 0))
        if pa.cash < cash_from or pb.cash < cash_to:
            return False
        props_from: List[int] = list(offer.get("props_from", []))
        props_to: List[int] = list(offer.get("props_to", []))
        # Validate ownership
        if not all(self.properties_state[i].owner_index == a for i in props_from):
            return False
        if not all(self.properties_state[i].owner_index == b for i in props_to):
            return False
        # Exchange cash
        pa.cash -= cash_from
        pb.cash += cash_from
        pb.cash -= cash_to
        pa.cash += cash_to
        # Exchange properties
        for i in props_from:
            self.properties_state[i].owner_index = b
            if i in pa.properties:
                pa.properties.remove(i)
            pb.properties.append(i)
        for i in props_to:
            self.properties_state[i].owner_index = a
            if i in pb.properties:
                pb.properties.remove(i)
            pa.properties.append(i)
        # Exchange GOJ cards
        goj_from = int(offer.get("goj_from", 0))
        goj_to = int(offer.get("goj_to", 0))
        if pa.get_out_of_jail_cards < goj_from or pb.get_out_of_jail_cards < goj_to:
            return False
        pa.get_out_of_jail_cards -= goj_from
        pb.get_out_of_jail_cards += goj_from
        pb.get_out_of_jail_cards -= goj_to
        pa.get_out_of_jail_cards += goj_to
        self.append_log(f"Trade completed between {pa.name} and {pb.name}.")
        return True