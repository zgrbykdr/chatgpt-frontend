from pathlib import Path
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QLabel,
    QToolBar,
    QStatusBar,
    QMessageBox,
)

from modules.campaign_manager import CampaignManager
from modules.dashboard import DashboardPanel
from modules.gm_assistant import GMAssistantPanel
from modules.battle_map import BattleMapPanel
from modules.lore_manager import LoreManagerPanel
from modules.story_engine import StoryEnginePanel
from modules.atmosphere import AtmospherePanel
from modules.dice_lab import DiceLabPanel
from modules.settings_panel import SettingsPanel
from modules.shared.data_manager import DataManager
from modules.shared.ui_helpers import apply_dark_theme


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("D&D 3e GM Assistant Suite")
        self.resize(1520, 920)

        base_dir = Path(__file__).resolve().parent
        self.data = DataManager(base_dir)
        self.campaign_manager = CampaignManager(self.data)
        self.campaign = self.campaign_manager.load_active_campaign()

        self._build_ui()
        self._wire_signals()
        self.refresh_all()

    def _build_ui(self) -> None:
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        self.campaign_label = QLabel()
        toolbar.addWidget(self.campaign_label)

        central = QWidget()
        root = QHBoxLayout(central)
        self.setCentralWidget(central)

        self.nav = QListWidget()
        self.nav.setFixedWidth(220)
        for name in [
            "Dashboard",
            "GM Assistant",
            "Battle Map",
            "Lore Manager",
            "Story Engine",
            "Atmosphere",
            "Dice Lab",
            "Settings",
        ]:
            QListWidgetItem(name, self.nav)

        self.stack = QStackedWidget()
        self.dashboard = DashboardPanel(self.data, self.campaign)
        self.gm_assistant = GMAssistantPanel(self.data, self.campaign)
        self.battle_map = BattleMapPanel(self.data, self.campaign)
        self.lore_manager = LoreManagerPanel(self.data, self.campaign)
        self.story_engine = StoryEnginePanel(self.data, self.campaign)
        self.atmosphere = AtmospherePanel(self.data, self.campaign)
        self.dice_lab = DiceLabPanel(self.data, self.campaign)
        self.settings_panel = SettingsPanel(self.data)

        for panel in [
            self.dashboard,
            self.gm_assistant,
            self.battle_map,
            self.lore_manager,
            self.story_engine,
            self.atmosphere,
            self.dice_lab,
            self.settings_panel,
        ]:
            self.stack.addWidget(panel)

        root.addWidget(self.nav)
        root.addWidget(self.stack, 1)

        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Ready")
        self.nav.setCurrentRow(0)

    def _wire_signals(self) -> None:
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.gm_assistant.save_to_lore_requested.connect(self.lore_manager.add_external_record)
        self.gm_assistant.send_to_story_requested.connect(self.story_engine.add_external_event)
        self.gm_assistant.send_to_battle_requested.connect(self.battle_map.import_encounter)
        self.story_engine.save_to_lore_requested.connect(self.lore_manager.add_external_record)
        self.battle_map.export_event_requested.connect(self.lore_manager.add_external_record)
        self.dashboard.quick_roll_requested.connect(self.dice_lab.quick_roll)
        self.dashboard.atmosphere_preset_requested.connect(self.atmosphere.activate_preset)

    def refresh_all(self) -> None:
        self.campaign_label.setText(f"Active Campaign: {self.campaign.get('name', 'Unknown')}")
        self.dashboard.refresh(self.campaign)
        self.lore_manager.refresh(self.campaign)
        self.story_engine.refresh(self.campaign)
        self.battle_map.refresh(self.campaign)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        try:
            self.campaign_manager.save_campaign(self.campaign)
            self.data.save_settings(self.settings_panel.current_settings())
        except Exception as exc:  # pragma: no cover
            QMessageBox.warning(self, "Save warning", str(exc))
        event.accept()


def main() -> None:
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
