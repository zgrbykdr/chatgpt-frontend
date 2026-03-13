import json
from pathlib import Path
from typing import Any, Dict

from .board_model import Board


class BoardLoader:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def load_board(self, board_file: str) -> Board:
        path = self.base_dir / board_file
        with path.open("r", encoding="utf-8") as handle:
            payload: Dict[str, Any] = json.load(handle)
        return Board.from_dict(payload)

    def save_board(self, board: Board, board_file: str) -> None:
        path = self.base_dir / board_file
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(board.to_dict(), handle, indent=2)
