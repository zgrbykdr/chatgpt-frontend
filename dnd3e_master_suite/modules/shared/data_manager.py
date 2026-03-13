from pathlib import Path
from typing import Any, Dict

from .utils import safe_json_read, safe_json_write


class DataManager:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.data_dir = base_dir / "data"
        self.save_dir = base_dir / "saves" / "campaigns"
        self.settings_path = self.data_dir / "sample" / "settings.json"
        self._ensure_structure()

    def _ensure_structure(self) -> None:
        for folder in [
            self.data_dir / "generators",
            self.data_dir / "presets",
            self.data_dir / "templates",
            self.data_dir / "reference",
            self.data_dir / "sample",
            self.save_dir,
        ]:
            folder.mkdir(parents=True, exist_ok=True)

    def read_json(self, rel_path: str, default: Any) -> Any:
        return safe_json_read(self.base_dir / rel_path, default)

    def write_json(self, rel_path: str, payload: Any) -> None:
        safe_json_write(self.base_dir / rel_path, payload)

    def load_settings(self) -> Dict[str, Any]:
        defaults = {
            "theme": "dark",
            "autosave": True,
            "default_save_path": str(self.save_dir),
            "sound_dir": str(self.base_dir / "assets" / "sounds"),
            "token_dir": str(self.base_dir / "assets" / "tokens"),
            "grid_size": 40,
            "startup_campaign": "sample_campaign",
            "debug_logging": False,
        }
        loaded = safe_json_read(self.settings_path, {})
        if not isinstance(loaded, dict):
            loaded = {}
        return {**defaults, **loaded}

    def save_settings(self, settings: Dict[str, Any]) -> None:
        safe_json_write(self.settings_path, settings)
