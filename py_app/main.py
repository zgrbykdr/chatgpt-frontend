from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication

try:
    # Running from repository root: python -m py_app.main
    from py_app.ui.main_window import MainWindow
except ModuleNotFoundError:
    # Running from inside py_app folder: python -m main
    from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
