from PySide6.QtGui import QPalette, QColor


def apply_dark_theme(app) -> None:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(32, 34, 37))
    palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.Base, QColor(24, 25, 26))
    palette.setColor(QPalette.AlternateBase, QColor(44, 47, 51))
    palette.setColor(QPalette.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.Button, QColor(54, 57, 63))
    palette.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    palette.setColor(QPalette.Highlight, QColor(88, 101, 242))
    app.setPalette(palette)
