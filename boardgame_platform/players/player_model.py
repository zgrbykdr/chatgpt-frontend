from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class Player:
    player_id: int
    name: str
    token: str
    color: List[int]
    money: int
    position: int = 0
    in_jail: bool = False
    jail_turns: int = 0
    skipped_turns: int = 0
    bankrupt: bool = False
    inventory: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "name": self.name,
            "token": self.token,
            "color": self.color,
            "money": self.money,
            "position": self.position,
            "in_jail": self.in_jail,
            "jail_turns": self.jail_turns,
            "skipped_turns": self.skipped_turns,
            "bankrupt": self.bankrupt,
            "inventory": self.inventory,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Player":
        return Player(**d)
