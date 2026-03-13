import random
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QCheckBox, QPushButton, QTextEdit


class StoryEnginePanel(QWidget):
    save_to_lore_requested = Signal(dict)

    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.kingdom_unstable = QCheckBox("Kingdom unstable")
        self.cult_active = QCheckBox("Cult active")
        self.war_ongoing = QCheckBox("War ongoing")
        self.output = QTextEdit(); self.output.setReadOnly(True)
        self.last_event = {}
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        box = QGroupBox("Campaign Pressure Variables")
        form = QFormLayout(box)
        form.addRow(self.kingdom_unstable); form.addRow(self.cult_active); form.addRow(self.war_ongoing)
        gen = QPushButton("Generate Story Event")
        gen.clicked.connect(self.generate_event)
        save = QPushButton("Save Event to Lore")
        save.clicked.connect(lambda: self.save_to_lore_requested.emit(self.last_event))
        layout.addWidget(box)
        layout.addWidget(gen)
        layout.addWidget(save)
        layout.addWidget(self.output, 1)

    def refresh(self, campaign) -> None:
        state = campaign.get("story_state", {})
        self.kingdom_unstable.setChecked(bool(state.get("kingdom_unstable")))
        self.cult_active.setChecked(bool(state.get("cult_active")))

    def add_external_event(self, payload: dict) -> None:
        self.last_event = payload
        self.output.setPlainText(f"External event added:\n{payload}")

    def generate_event(self) -> None:
        pool = ["Temple corruption uncovered", "Faction envoy requests covert aid", "Undead raid on frontier hamlet"]
        if self.cult_active.isChecked():
            pool.append("Cult performs public omen ritual")
        if self.war_ongoing.isChecked():
            pool.append("Military conscription sparks revolt")
        title = random.choice(pool)
        self.last_event = {
            "id": f"story_{random.randint(1000,9999)}",
            "title": title,
            "category": "Event",
            "summary": "Dynamic campaign consequence triggered by current state.",
            "notes": "Why now: pressure is rising among factions. Suggested consequence: supply lines disrupted.",
            "dnd3e": {"tension": "high", "encounter_difficulty": "moderate-hard"},
        }
        self.output.setPlainText("\n".join(f"{k}: {v}" for k, v in self.last_event.items()))
