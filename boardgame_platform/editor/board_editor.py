import json
from pathlib import Path


class BoardEditor:
    @staticmethod
    def add_square(board_json, square):
        board_json["board"]["squares"].append(square)
        board_json["board"]["size"] = len(board_json["board"]["squares"])

    @staticmethod
    def remove_square(board_json, square_id):
        board_json["board"]["squares"] = [s for s in board_json["board"]["squares"] if s["id"] != square_id]
        for idx, sq in enumerate(board_json["board"]["squares"]):
            sq["id"] = idx
        board_json["board"]["size"] = len(board_json["board"]["squares"])

    @staticmethod
    def save(path: str, board_json):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(board_json, f, indent=2)
