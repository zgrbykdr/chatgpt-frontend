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
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.last_event = {}
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        box = QGroupBox("Campaign Pressure Variables")
        form = QFormLayout(box)
        form.addRow(self.kingdom_unstable)
        form.addRow(self.cult_active)
        form.addRow(self.war_ongoing)

        gen = QPushButton("Generate Story Event")
        gen.clicked.connect(self.generate_event)
        save = QPushButton("Save Event to Lore")
        save.clicked.connect(lambda: self.save_to_lore_requested.emit(self.last_event))

        layout.addWidget(box)
        layout.addWidget(gen)
        layout.addWidget(save)
        layout.addWidget(self.output, 1)

    def refresh(self, campaign) -> None:
        self.campaign = campaign
        state = campaign.get("story_state", {})
        self.kingdom_unstable.setChecked(bool(state.get("kingdom_unstable")))
        self.cult_active.setChecked(bool(state.get("cult_active")))
        self.war_ongoing.setChecked(bool(state.get("war_ongoing")))

    def add_external_event(self, payload: dict) -> None:
        self.last_event = payload
        self.output.setPlainText(f"External event added:\n{payload}")

    def _persist_state(self) -> None:
        state = self.campaign.setdefault("story_state", {})
        state["kingdom_unstable"] = self.kingdom_unstable.isChecked()
        state["cult_active"] = self.cult_active.isChecked()
        state["war_ongoing"] = self.war_ongoing.isChecked()

    def generate_event(self) -> None:
        self._persist_state()
        pool = [
            "Temple corruption uncovered",
            "Faction envoy requests covert aid",
            "Undead raid on frontier hamlet",
            "Rumor network reveals hidden supply route",
        ]
        why_now = []

        if self.cult_active.isChecked():
            pool.append("Cult performs public omen ritual")
            why_now.append("cult influence has reached open agitation")
        if self.war_ongoing.isChecked():
            pool.append("Military conscription sparks revolt")
            why_now.append("war logistics are straining settlements")
        if self.kingdom_unstable.isChecked():
            pool.append("Border lord declares emergency levy")
            why_now.append("nobles are competing for control")

        title = random.choice(pool)
        why = "; ".join(why_now) if why_now else "multiple unresolved tensions are converging"
        self.last_event = {
            "id": f"story_{random.randint(1000,9999)}",
            "title": title,
            "category": "Event",
            "summary": "Dynamic campaign consequence triggered by current state.",
            "notes": (
                f"Why now: {why}. Related factions: Emberfall Watch, Ashen Lantern. "
                "Suggested consequences: disrupted supply lines, contested temple district, urgent side quest opportunities."
            ),
            "tags": ["story_engine", "generated_event"],
            "dnd3e": {"tension": "high", "encounter_difficulty": "moderate-hard"},
        }
        self.output.setPlainText("\n".join(f"{k}: {v}" for k, v in self.last_event.items()))
