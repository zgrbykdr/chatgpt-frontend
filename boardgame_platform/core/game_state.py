from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from board.board_model import Board
from players.player_model import Player


@dataclass
class PropertyState:
    owner: int | None = None
    houses: int = 0
    hotel: int = 0
    mortgaged: bool = False

    def to_dict(self) -> Dict:
        return {
            "owner": self.owner,
            "houses": self.houses,
            "hotel": self.hotel,
            "mortgaged": self.mortgaged,
        }


@dataclass
class GameState:
    board: Board
    rules: Dict
    players: List[Player]
    current_player_index: int = 0
    turn_number: int = 1
    property_state: Dict[int, PropertyState] = field(default_factory=dict)
    game_over: bool = False
    winner: int | None = None
    messages: List[str] = field(default_factory=list)

    def ensure_property_map(self) -> None:
        for square in self.board.squares:
            if square.type in {"property", "railroad", "utility"} and square.id not in self.property_state:
                self.property_state[square.id] = PropertyState()

    def active_players(self) -> List[Player]:
        return [p for p in self.players if p.active and not p.bankrupt]
