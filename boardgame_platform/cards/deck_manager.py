import json
import random
from pathlib import Path
from typing import Dict, List

from .card_model import Card


class DeckManager:
    def __init__(self, deck_dir: str | Path):
        self.deck_dir = Path(deck_dir)
        self.decks: Dict[str, List[Card]] = {}
        self.indices: Dict[str, int] = {}

    def load_deck(self, file_name: str) -> str:
        path = self.deck_dir / file_name
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        deck_name = payload["name"]
        cards = [Card.from_dict(c) for c in payload.get("cards", [])]
        random.shuffle(cards)
        self.decks[deck_name] = cards
        self.indices[deck_name] = 0
        return deck_name

    def draw(self, deck_name: str) -> Card:
        cards = self.decks[deck_name]
        idx = self.indices[deck_name]
        card = cards[idx % len(cards)]
        self.indices[deck_name] = (idx + 1) % len(cards)
        return card

    def to_dict(self) -> Dict:
        return {
            "decks": {
                name: [card.to_dict() for card in cards] for name, cards in self.decks.items()
            },
            "indices": self.indices,
        }

    def from_dict(self, payload: Dict) -> None:
        self.decks = {
            name: [Card.from_dict(card) for card in cards]
            for name, cards in payload.get("decks", {}).items()
        }
        self.indices = payload.get("indices", {name: 0 for name in self.decks})
