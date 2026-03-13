import json
from pathlib import Path
from typing import Dict, Any

from players.player_model import Player
from core.game_state import PropertyState


class SaveManager:
    @staticmethod
    def save(path: str, engine) -> None:
        payload = {
            "state": engine.state.to_dict(),
            "rules": engine.rules.rules,
            "board": {
                "name": engine.board.name,
                "theme": engine.board.theme,
                "size": engine.board.size,
                "squares": [s.__dict__ for s in engine.board.squares],
            },
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    @staticmethod
    def load(path: str, engine) -> None:
        with Path(path).open("r", encoding="utf-8") as f:
            payload: Dict[str, Any] = json.load(f)
        s = payload["state"]
        engine.state.current_turn = s["current_turn"]
        engine.state.last_roll = s["last_roll"]
        engine.state.players = [Player.from_dict(p) for p in s["players"]]
        engine.state.property_state = {int(k): PropertyState(**v) for k, v in s["property_state"].items()}
        engine.state.decks = s.get("decks", {})
        engine.state.jail_pot = s["jail_pot"]
        engine.state.winner_id = s.get("winner_id")
        engine.state.turn_phase = s.get("turn_phase", "idle")
        engine.state.messages = s.get("messages", [])
