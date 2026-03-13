from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict


DEFAULT_SETTINGS = {
    "edge_path": "",
    "profile_path": "",
    "profile_name": "Default",
    "edge_extra_args": "--new-tab",
    "theme": "dark",
}


class SettingsManager:
    """JSON dosyasında uygulama ayarlarını saklar."""

    def __init__(self, settings_path: Path) -> None:
        self.settings_path = settings_path
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self._settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self) -> None:
        if not self.settings_path.exists():
            self.save()
            return

        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            self._settings = merged
        except json.JSONDecodeError:
            self._settings = DEFAULT_SETTINGS.copy()
            self.save()

    def save(self) -> None:
        self.settings_path.write_text(
            json.dumps(self._settings, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get(self, key: str) -> str:
        return self._settings.get(key, "")

    def set(self, key: str, value: str) -> None:
        self._settings[key] = value

    def as_dict(self) -> Dict[str, str]:
        return dict(self._settings)


def guess_edge_path() -> str:
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return ""


def guess_edge_profile_path() -> str:
    candidate = os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data")
    return candidate if candidate and Path(candidate).exists() else ""
