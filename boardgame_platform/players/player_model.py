from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Player:
    name: str
    token: str
    color: tuple[int, int, int]
    position: int = 0
    money: int = 1500
    owned_properties: List[int] = field(default_factory=list)
    in_jail: bool = False
    jail_turns: int = 0
    skip_turns: int = 0
    active: bool = True
    bankrupt: bool = False
    doubles_rolled: int = 0

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "token": self.token,
            "color": list(self.color),
            "position": self.position,
            "money": self.money,
            "owned_properties": self.owned_properties,
            "in_jail": self.in_jail,
            "jail_turns": self.jail_turns,
            "skip_turns": self.skip_turns,
            "active": self.active,
            "bankrupt": self.bankrupt,
            "doubles_rolled": self.doubles_rolled,
        }

    @classmethod
    def from_dict(cls, payload: Dict) -> "Player":
        payload = dict(payload)
        payload["color"] = tuple(payload.get("color", [255, 255, 255]))
        return cls(**payload)
