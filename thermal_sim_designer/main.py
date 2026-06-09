from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main_window import MainWindow  # noqa: E402
from core.project import ensure_default_data  # noqa: E402


def main() -> int:
    try:
        ensure_default_data()
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as exc:
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "ThermalSim Designer", f"Uygulama başlatılamadı:\n{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
