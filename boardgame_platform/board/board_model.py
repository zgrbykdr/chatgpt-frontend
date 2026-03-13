from dataclasses import dataclass, field
from typing import List, Dict, Any
from board.square_model import Square


@dataclass
class Board:
    name: str
    theme: str
    size: int
    squares: List[Square] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Board":
        b = data["board"]
        return Board(
            name=b["name"],
            theme=b.get("theme", "classic"),
            size=b["size"],
            squares=[Square.from_dict(s) for s in b["squares"]],
        )
