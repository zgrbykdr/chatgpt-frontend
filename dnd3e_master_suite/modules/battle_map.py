from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QListWidget, QFormLayout, QLineEdit, QSpinBox, QGroupBox, QLabel
)


class BattleMapPanel(QWidget):
    export_event_requested = Signal(dict)

    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.grid = QTableWidget(20, 20)
        self.token_list = QListWidget()
        self.round_label = QLabel("Round 1")
        self.round = 1
        self.name = QLineEdit(); self.side = QLineEdit("Enemy"); self.hp = QSpinBox(); self.ac = QSpinBox(); self.init = QSpinBox()
        self.hp.setRange(0, 999); self.ac.setRange(0, 99); self.init.setRange(-10, 50)
        self._build()

    def _build(self) -> None:
        layout = QHBoxLayout(self)
        left = QVBoxLayout()
        self.grid.setAlternatingRowColors(True)
        for r in range(20):
            self.grid.setRowHeight(r, 26)
            for c in range(20):
                self.grid.setColumnWidth(c, 26)
                self.grid.setItem(r, c, QTableWidgetItem(""))
        left.addWidget(self.grid, 1)
        left.addWidget(self.round_label)
        nxt = QPushButton("Next Round")
        nxt.clicked.connect(self.next_round)
        left.addWidget(nxt)

        right = QVBoxLayout()
        token_box = QGroupBox("Token / Combatant")
        form = QFormLayout(token_box)
        form.addRow("Name", self.name); form.addRow("Side", self.side)
        form.addRow("HP", self.hp); form.addRow("AC", self.ac); form.addRow("Initiative", self.init)
        add_btn = QPushButton("Add Token")
        add_btn.clicked.connect(self.add_token)
        form.addRow(add_btn)
        right.addWidget(token_box)
        right.addWidget(QLabel("Initiative / Token List"))
        right.addWidget(self.token_list, 1)
        export_btn = QPushButton("Export Combat Result to Lore")
        export_btn.clicked.connect(self.export_result)
        right.addWidget(export_btn)

        layout.addLayout(left, 3)
        layout.addLayout(right, 2)

    def add_token(self) -> None:
        row = f"{self.init.value():>3} | {self.name.text()} | HP {self.hp.value()} | AC {self.ac.value()} | Fort/Ref/Will +2/+2/+0 | BAB +1 | Speed 30"
        self.token_list.addItem(row)

    def next_round(self) -> None:
        self.round += 1
        self.round_label.setText(f"Round {self.round} (flat-footed reminder first turn)")

    def import_encounter(self, payload: dict) -> None:
        title = payload.get("title", "Encounter")
        self.token_list.addItem(f"Imported encounter: {title}")

    def export_result(self) -> None:
        payload = {
            "id": f"combat_round_{self.round}",
            "title": f"Combat Snapshot Round {self.round}",
            "category": "Event",
            "summary": "Exported combat summary from Battle Map.",
            "notes": "\n".join(self.token_list.item(i).text() for i in range(self.token_list.count())),
            "dnd3e": {"encounter_difficulty": "moderate", "xp_reward_note": "Determine by monster CR mix"},
        }
        self.export_event_requested.emit(payload)

    def refresh(self, campaign) -> None:
        self.campaign = campaign
