import json
import random
from pathlib import Path
from typing import Dict, List, Any


class DeckManager:
    def __init__(self) -> None:
        self.decks: Dict[str, List[Dict[str, Any]]] = {}

    def load_deck(self, name: str, path: str) -> None:
        with Path(path).open("r", encoding="utf-8") as f:
            self.decks[name] = json.load(f)["cards"]
        random.shuffle(self.decks[name])

    def draw(self, name: str) -> Dict[str, Any]:
        card = self.decks[name].pop(0)
        self.decks[name].append(card)
        return card
