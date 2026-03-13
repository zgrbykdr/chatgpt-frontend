from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton, QHBoxLayout, QListWidget


class DashboardPanel(QWidget):
    quick_roll_requested = Signal(str)
    atmosphere_preset_requested = Signal(str)

    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.summary = QLabel()
        self.recent_notes = QListWidget()
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        summary_box = QGroupBox("Campaign Summary")
        s_l = QVBoxLayout(summary_box)
        s_l.addWidget(self.summary)

        quick_box = QGroupBox("Quick Actions")
        q_l = QHBoxLayout(quick_box)
        roll_btn = QPushButton("Quick d20 Roll")
        roll_btn.clicked.connect(lambda: self.quick_roll_requested.emit("1d20"))
        q_l.addWidget(roll_btn)
        for name in ["tavern", "dungeon", "battle"]:
            btn = QPushButton(name.title())
            btn.clicked.connect(lambda _, n=name: self.atmosphere_preset_requested.emit(n))
            q_l.addWidget(btn)

        notes_box = QGroupBox("Recent Session Notes")
        n_l = QVBoxLayout(notes_box)
        n_l.addWidget(self.recent_notes)

        layout.addWidget(summary_box)
        layout.addWidget(quick_box)
        layout.addWidget(notes_box, 1)

    def refresh(self, campaign) -> None:
        self.campaign = campaign
        lore_count = len(campaign.get("lore", []))
        notes = campaign.get("session_notes", [])
        self.summary.setText(f"Lore entries: {lore_count}\nOpen notes: {len(notes)}\nStory state: {campaign.get('story_state', {})}")
        self.recent_notes.clear()
        for note in notes[-10:][::-1]:
            self.recent_notes.addItem(note)
