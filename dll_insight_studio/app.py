from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from dll_insight_studio.gui.main_window import MainWindow
from dll_insight_studio.services.application_context import ApplicationContext


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("DLL Insight Studio")
    app.setOrganizationName("DLL Insight")

    base_dir = Path.cwd()
    context = ApplicationContext(base_dir=base_dir)
    window = MainWindow(context)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
