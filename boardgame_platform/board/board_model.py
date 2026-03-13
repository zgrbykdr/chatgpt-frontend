from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .square_model import Square


@dataclass
class Board:
    name: str
    size: int
    squares: List[Square] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict) -> "Board":
        board_data = payload["board"] if "board" in payload else payload
        squares = [Square.from_dict(s) for s in board_data.get("squares", [])]
        size = board_data.get("size", len(squares))
        return cls(name=board_data["name"], size=size, squares=squares)

    def to_dict(self) -> Dict:
        return {
            "board": {
                "name": self.name,
                "size": self.size,
                "squares": [s.to_dict() for s in self.squares],
            }
        }

    def get_square(self, idx: int) -> Optional[Square]:
        if not self.squares:
            return None
        return self.squares[idx % self.size]
