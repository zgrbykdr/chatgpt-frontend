from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton, QHBoxLayout, QListWidget


class DashboardPanel(QWidget):
    quick_roll_requested = Signal(str)
    atmosphere_preset_requested = Signal(str)
    quick_generate_requested = Signal(str)

    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.summary = QLabel()
        self.recent_notes = QListWidget()
        self.open_quests = QListWidget()
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

        for gen_type in ["NPC", "Quest", "Encounter"]:
            gen_btn = QPushButton(f"Quick {gen_type}")
            gen_btn.clicked.connect(lambda _, g=gen_type: self.quick_generate_requested.emit(g))
            q_l.addWidget(gen_btn)

        for name in ["tavern", "dungeon", "battle"]:
            btn = QPushButton(name.title())
            btn.clicked.connect(lambda _, n=name: self.atmosphere_preset_requested.emit(n))
            q_l.addWidget(btn)

        notes_box = QGroupBox("Recent Session Notes")
        n_l = QVBoxLayout(notes_box)
        n_l.addWidget(self.recent_notes)

        quests_box = QGroupBox("Open Quests")
        q2_l = QVBoxLayout(quests_box)
        q2_l.addWidget(self.open_quests)

        layout.addWidget(summary_box)
        layout.addWidget(quick_box)
        layout.addWidget(notes_box, 1)
        layout.addWidget(quests_box, 1)

    def refresh(self, campaign) -> None:
        self.campaign = campaign
        lore = campaign.get("lore", [])
        notes = campaign.get("session_notes", [])
        quests = [r for r in lore if r.get("category") == "Quest"]

        self.summary.setText(
            f"Lore entries: {len(lore)}\n"
            f"Session notes: {len(notes)}\n"
            f"Open quests: {len(quests)}\n"
            f"Story state: {campaign.get('story_state', {})}"
        )

        self.recent_notes.clear()
        for note in notes[-10:][::-1]:
            self.recent_notes.addItem(note)

        self.open_quests.clear()
        for quest in quests[-10:][::-1]:
            self.open_quests.addItem(quest.get("title", "Untitled Quest"))
