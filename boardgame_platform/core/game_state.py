from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


@dataclass
class PropertyState:
    owner_id: Optional[int] = None
    houses: int = 0
    mortgaged: bool = False


@dataclass
class GameState:
    board_name: str
    current_turn: int = 0
    last_roll: List[int] = field(default_factory=lambda: [0, 0])
    players: List[Any] = field(default_factory=list)
    property_state: Dict[int, PropertyState] = field(default_factory=dict)
    decks: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    jail_pot: int = 0
    winner_id: Optional[int] = None
    turn_phase: str = "idle"
    messages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "board_name": self.board_name,
            "current_turn": self.current_turn,
            "last_roll": self.last_roll,
            "players": [p.to_dict() for p in self.players],
            "property_state": {str(k): asdict(v) for k, v in self.property_state.items()},
            "decks": self.decks,
            "jail_pot": self.jail_pot,
            "winner_id": self.winner_id,
            "turn_phase": self.turn_phase,
            "messages": self.messages,
        }
