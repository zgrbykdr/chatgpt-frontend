import json
from pathlib import Path


class DeckEditor:
    def __init__(self, deck_path: str | Path):
        self.deck_path = Path(deck_path)

    def load(self) -> dict:
        with self.deck_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, deck_payload: dict) -> None:
        self.deck_path.parent.mkdir(parents=True, exist_ok=True)
        with self.deck_path.open("w", encoding="utf-8") as handle:
            json.dump(deck_payload, handle, indent=2)

    def add_card(self, card_payload: dict) -> None:
        payload = self.load()
        payload.setdefault("cards", []).append(card_payload)
        self.save(payload)
