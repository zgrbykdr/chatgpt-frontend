import json
from pathlib import Path

from core.game_state import PropertyState
from players.player_model import Player


class SaveManager:
    def __init__(self, save_dir: str | Path):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def save_game(self, file_name: str, engine) -> Path:
        payload = {
            "board_name": engine.state.board.name,
            "rules": engine.state.rules,
            "players": [p.to_dict() for p in engine.state.players],
            "current_player_index": engine.state.current_player_index,
            "turn_number": engine.state.turn_number,
            "property_state": {str(k): v.to_dict() for k, v in engine.state.property_state.items()},
            "deck_state": engine.deck_manager.to_dict(),
        }
        path = self.save_dir / file_name
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        return path

    def load_into_engine(self, file_name: str, engine):
        path = self.save_dir / file_name
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        engine.state.rules = payload["rules"]
        engine.state.players = [Player.from_dict(p) for p in payload["players"]]
        engine.state.current_player_index = payload["current_player_index"]
        engine.state.turn_number = payload["turn_number"]
        engine.state.property_state = {
            int(k): PropertyState(**v) for k, v in payload["property_state"].items()
        }
        engine.deck_manager.from_dict(payload.get("deck_state", {}))
