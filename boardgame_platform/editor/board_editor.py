import json
from pathlib import Path


class BoardEditor:
    def __init__(self, board_path: str | Path):
        self.board_path = Path(board_path)

    def load(self) -> dict:
        with self.board_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, board_payload: dict) -> None:
        self.board_path.parent.mkdir(parents=True, exist_ok=True)
        with self.board_path.open("w", encoding="utf-8") as handle:
            json.dump(board_payload, handle, indent=2)

    def add_square(self, square_payload: dict) -> None:
        data = self.load()
        data["board"]["squares"].append(square_payload)
        data["board"]["size"] = len(data["board"]["squares"])
        self.save(data)
