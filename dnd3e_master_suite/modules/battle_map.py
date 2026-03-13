from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QListWidget, QFormLayout, QLineEdit, QSpinBox, QGroupBox, QLabel, QTextEdit
)


class BattleMapPanel(QWidget):
    export_event_requested = Signal(dict)

    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.grid = QTableWidget(20, 20)
        self.token_list = QListWidget()
        self.combat_log = QTextEdit()
        self.round_label = QLabel("Round 1")
        self.round = 1

        self.name = QLineEdit()
        self.side = QLineEdit("Enemy")
        self.hp = QSpinBox()
        self.ac = QSpinBox()
        self.init = QSpinBox()
        self.bab = QLineEdit("+0")
        self.saves = QLineEdit("Fort +0 / Ref +0 / Will +0")
        self.size = QLineEdit("Medium")
        self.speed = QLineEdit("30")
        self.init_mod = QLineEdit("+0")
        self.attack_notes = QLineEdit("Melee +0 / Ranged +0 / Grapple +0")
        self.ac_breakdown = QLineEdit("armor +0, shield +0, Dex +0, size +0, natural +0, deflection +0, misc +0")
        self.spellcaster = QLineEdit("no")
        self.caster_level = QLineEdit("")
        self.cr_note = QLineEdit("CR 1")
        self.xp_note = QLineEdit("XP by CR")

        self.hp.setRange(0, 999)
        self.ac.setRange(0, 99)
        self.init.setRange(-10, 50)
        self._build()

    def _build(self) -> None:
        layout = QHBoxLayout(self)
        left = QVBoxLayout()
        self.grid.setAlternatingRowColors(True)
        self.grid.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.grid.setVerticalScrollMode(QTableWidget.ScrollPerPixel)

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
        form.addRow("Name", self.name)
        form.addRow("Side", self.side)
        form.addRow("HP", self.hp)
        form.addRow("AC", self.ac)
        form.addRow("Initiative", self.init)
        form.addRow("Initiative Mod", self.init_mod)
        form.addRow("BAB", self.bab)
        form.addRow("Saves", self.saves)
        form.addRow("Size", self.size)
        form.addRow("Speed", self.speed)
        form.addRow("Attack Notes", self.attack_notes)
        form.addRow("AC Breakdown", self.ac_breakdown)
        form.addRow("Spellcaster", self.spellcaster)
        form.addRow("Caster Level", self.caster_level)
        form.addRow("CR Note", self.cr_note)
        form.addRow("XP Note", self.xp_note)

        add_btn = QPushButton("Add Token")
        add_btn.clicked.connect(self.add_token)
        form.addRow(add_btn)
        right.addWidget(token_box)

        right.addWidget(QLabel("Initiative / Token List"))
        right.addWidget(self.token_list, 1)
        right.addWidget(QLabel("Combat Log"))
        self.combat_log.setPlaceholderText("Round actions, conditions, damage and saving throw notes...")
        right.addWidget(self.combat_log, 1)

        export_btn = QPushButton("Export Combat Result to Lore")
        export_btn.clicked.connect(self.export_result)
        right.addWidget(export_btn)

        layout.addLayout(left, 3)
        layout.addLayout(right, 3)

    def _token_row(self, token: dict) -> str:
        return (
            f"{token['initiative']:>3} | {token['name']} ({token['side']}) | HP {token['hp']} | AC {token['ac']} | "
            f"InitMod {token['init_mod']} | {token['saves']} | BAB {token['bab']} | Size {token['size']} | Speed {token['speed']}"
        )

    def add_token(self) -> None:
        token = {
            "name": self.name.text().strip() or "Unnamed",
            "side": self.side.text().strip() or "Enemy",
            "hp": self.hp.value(),
            "ac": self.ac.value(),
            "initiative": self.init.value(),
            "init_mod": self.init_mod.text().strip(),
            "bab": self.bab.text().strip(),
            "saves": self.saves.text().strip(),
            "size": self.size.text().strip(),
            "speed": self.speed.text().strip(),
            "attack_notes": self.attack_notes.text().strip(),
            "ac_breakdown": self.ac_breakdown.text().strip(),
            "spellcaster": self.spellcaster.text().strip(),
            "caster_level": self.caster_level.text().strip(),
            "cr_note": self.cr_note.text().strip(),
            "xp_note": self.xp_note.text().strip(),
        }
        state = self.campaign.setdefault("battle_state", {"round": 1, "tokens": [], "log": []})
        state.setdefault("tokens", []).append(token)
        state["tokens"] = sorted(state["tokens"], key=lambda t: t.get("initiative", 0), reverse=True)
        self._refresh_tokens_from_state()

    def _refresh_tokens_from_state(self) -> None:
        self.token_list.clear()
        for token in self.campaign.get("battle_state", {}).get("tokens", []):
            self.token_list.addItem(self._token_row(token))

    def next_round(self) -> None:
        self.round += 1
        self.round_label.setText(f"Round {self.round} (flat-footed reminder first turn)")
        state = self.campaign.setdefault("battle_state", {"round": 1, "tokens": [], "log": []})
        state["round"] = self.round
        if self.combat_log.toPlainText().strip():
            state.setdefault("log", []).append(f"Round {self.round - 1}: {self.combat_log.toPlainText().strip()}")
            self.combat_log.clear()

    def import_encounter(self, payload: dict) -> None:
        title = payload.get("title", "Encounter")
        self.combat_log.append(f"Imported encounter: {title}")

    def export_result(self) -> None:
        notes = [self.token_list.item(i).text() for i in range(self.token_list.count())]
        if self.combat_log.toPlainText().strip():
            notes.append("--- Combat Log ---")
            notes.append(self.combat_log.toPlainText().strip())
        payload = {
            "id": f"combat_round_{self.round}",
            "title": f"Combat Snapshot Round {self.round}",
            "category": "Event",
            "summary": "Exported combat summary from Battle Map.",
            "notes": "\n".join(notes),
            "dnd3e": {
                "encounter_difficulty": "moderate",
                "xp_reward_note": "Determine by monster CR mix",
                "dungeon_room_notes": "Capture room-by-room progression from combat log.",
            },
        }
        self.export_event_requested.emit(payload)

    def refresh(self, campaign) -> None:
        self.campaign = campaign
        self.round = int(campaign.get("battle_state", {}).get("round", 1))
        self.round_label.setText(f"Round {self.round}")
        self._refresh_tokens_from_state()
