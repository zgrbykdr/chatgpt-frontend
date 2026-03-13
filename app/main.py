from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .database import MusicDatabase
from .gui import MainWindow
from .settings_manager import SettingsManager


def app_data_dir() -> Path:
    # Uygulama verileri kullanıcı profili altında kalıcı şekilde saklanır.
    home = Path.home()
    return home / "YouTubeMuzikYoneticisi"


def main() -> int:
    data_dir = app_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    db = MusicDatabase(data_dir / "muzikler.db")
    settings = SettingsManager(data_dir / "ayarlar.json")

    app = QApplication(sys.argv)
    window = MainWindow(db, settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
