import json
from pathlib import Path
from typing import Dict, Any


def load_config_from_folder(folder: Path) -> Dict[str, Any]:
    board = json.loads((folder / "board.json").read_text(encoding="utf-8"))
    chance = json.loads((folder / "chance.json").read_text(encoding="utf-8"))
    community = json.loads((folder / "community_chest.json").read_text(encoding="utf-8"))
    return {"board": board, "chance": chance, "community_chest": community}


def save_config_to_folder(folder: Path, config: Dict[str, Any]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "board.json").write_text(json.dumps(config["board"], indent=2), encoding="utf-8")
    (folder / "chance.json").write_text(json.dumps(config["chance"], indent=2), encoding="utf-8")
    (folder / "community_chest.json").write_text(json.dumps(config["community_chest"], indent=2), encoding="utf-8")