import json
from pathlib import Path
from typing import Dict, Any
from board.board_model import Board


class BoardLoader:
    @staticmethod
    def load(path: str) -> Dict[str, Any]:
        with Path(path).open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_board(path: str) -> Board:
        return Board.from_dict(BoardLoader.load(path))
