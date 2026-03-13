import json
from pathlib import Path


class DeckEditor:
    @staticmethod
    def create_deck(name: str):
        return {"name": name, "cards": []}

    @staticmethod
    def add_card(deck_json, card):
        deck_json["cards"].append(card)

    @staticmethod
    def save(path: str, deck_json):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(deck_json, f, indent=2)
