from PySide6.QtWidgets import QWidget, QFormLayout, QComboBox, QCheckBox, QLineEdit, QSpinBox


class SettingsPanel(QWidget):
    def __init__(self, data_manager) -> None:
        super().__init__()
        self.data = data_manager
        settings = self.data.load_settings()
        self.theme = QComboBox(); self.theme.addItems(["dark", "system"]); self.theme.setCurrentText(settings.get("theme", "dark"))
        self.autosave = QCheckBox(); self.autosave.setChecked(settings.get("autosave", True))
        self.save_path = QLineEdit(settings.get("default_save_path", ""))
        self.sound_dir = QLineEdit(settings.get("sound_dir", ""))
        self.token_dir = QLineEdit(settings.get("token_dir", ""))
        self.grid = QSpinBox(); self.grid.setRange(16, 128); self.grid.setValue(int(settings.get("grid_size", 40)))
        self.startup_campaign = QLineEdit(settings.get("startup_campaign", "sample_campaign"))
        self.debug = QCheckBox(); self.debug.setChecked(settings.get("debug_logging", False))
        self._build()

    def _build(self) -> None:
        form = QFormLayout(self)
        form.addRow("Theme", self.theme)
        form.addRow("Autosave", self.autosave)
        form.addRow("Default Save Path", self.save_path)
        form.addRow("Sound Directory", self.sound_dir)
        form.addRow("Token Directory", self.token_dir)
        form.addRow("Grid Size", self.grid)
        form.addRow("Startup Campaign", self.startup_campaign)
        form.addRow("Debug Logging", self.debug)

    def current_settings(self):
        return {
            "theme": self.theme.currentText(),
            "autosave": self.autosave.isChecked(),
            "default_save_path": self.save_path.text().strip(),
            "sound_dir": self.sound_dir.text().strip(),
            "token_dir": self.token_dir.text().strip(),
            "grid_size": self.grid.value(),
            "startup_campaign": self.startup_campaign.text().strip(),
            "debug_logging": self.debug.isChecked(),
        }
