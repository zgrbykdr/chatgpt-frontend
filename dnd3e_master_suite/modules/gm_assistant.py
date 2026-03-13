import random
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QPushButton, QTextEdit, QHBoxLayout, QGroupBox
)

from modules.shared.utils import now_iso


class GMAssistantPanel(QWidget):
    save_to_lore_requested = Signal(dict)
    send_to_story_requested = Signal(dict)
    send_to_battle_requested = Signal(dict)

    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.generator_type = QComboBox()
        self.tone = QComboBox(); self.region = QComboBox(); self.danger = QComboBox()
        self.output = QTextEdit(); self.output.setReadOnly(True)
        self.last_payload = {}
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        form_box = QGroupBox("Generator Controls")
        form = QFormLayout(form_box)
        self.generator_type.addItems(["NPC", "Quest", "Encounter", "Rumor", "Treasure", "Trap Hook"])
        self.tone.addItems(["Heroic", "Dark", "Mysterious", "Political", "Grim"])
        self.region.addItems(["City", "Village", "Dungeon", "Forest", "Ruins", "Swamp"])
        self.danger.addItems(["Low", "Moderate", "High", "Deadly"])
        form.addRow("Generator", self.generator_type)
        form.addRow("Tone", self.tone)
        form.addRow("Region", self.region)
        form.addRow("Danger", self.danger)
        gen_btn = QPushButton("Generate")
        gen_btn.clicked.connect(self.generate)
        form.addRow(gen_btn)

        action_row = QHBoxLayout()
        lore_btn = QPushButton("Save to Lore")
        lore_btn.clicked.connect(lambda: self.save_to_lore_requested.emit(self.last_payload))
        story_btn = QPushButton("Add to Story Engine")
        story_btn.clicked.connect(lambda: self.send_to_story_requested.emit(self.last_payload))
        battle_btn = QPushButton("Send to Battle Map")
        battle_btn.clicked.connect(lambda: self.send_to_battle_requested.emit(self.last_payload))
        action_row.addWidget(lore_btn); action_row.addWidget(story_btn); action_row.addWidget(battle_btn)

        layout.addWidget(form_box)
        layout.addLayout(action_row)
        layout.addWidget(self.output, 1)

    def generate(self) -> None:
        g = self.generator_type.currentText()
        tone = self.tone.currentText()
        region = self.region.currentText()
        danger = self.danger.currentText()

        names = ["Aldren", "Vaelis", "Mara", "Torvek", "Ilyra"]
        factions = ["Ashen Lantern", "Emberfall Watch", "Silent Coin Guild"]
        if g == "NPC":
            payload = {
                "id": f"npc_{random.randint(1000,9999)}",
                "title": f"{random.choice(names)} of {region}",
                "category": "NPC",
                "summary": f"{tone} contact with {danger.lower()} risk profile.",
                "notes": "Race: Human | Class: Rogue | Level: 4 | Alignment: CN | BAB: +3 | Saves: Fort +2 Ref +6 Will +1 | Size: Medium | Speed: 30 | Spellcaster: No | CR note: ~3",
                "dnd3e": {
                    "alignment": "Chaotic Neutral", "bab": "+3", "size": "Medium", "speed": "30",
                    "fort": "+2", "ref": "+6", "will": "+1", "initiative_mod": "+3", "ac_breakdown": "armor +3, shield +0, Dex +3, size +0, natural +0, deflection +0, misc +1",
                    "attack_notes": "Melee +5 short sword, Ranged +6 shortbow, Grapple +3",
                    "spellcaster": "no", "caster_level": "", "skill_highlights": "Hide +8, Move Silently +8", "feat_highlights": "Weapon Finesse, Point Blank Shot",
                    "xp_reward_note": "~900 XP group split", "challenge_rating_note": "CR 3"
                }
            }
        elif g == "Quest":
            payload = {
                "id": f"quest_{random.randint(1000,9999)}",
                "title": f"Shadows in the {region}",
                "category": "Quest",
                "summary": f"Patron requests aid; {tone.lower()} tone; hidden betrayal.",
                "notes": "Objective: secure relic. Obstacles: cult scouts, trapped vault. Suggested level 3-5. EL guidance: 4-6.",
                "dnd3e": {"encounter_difficulty": danger, "treasure_parcel_notes": "1 minor magic, coin cache, lore map"}
            }
        else:
            payload = {
                "id": f"enc_{random.randint(1000,9999)}",
                "title": f"{tone} {region} Skirmish",
                "category": "Event",
                "summary": "Enemy composition: 4 raiders + 1 adept leader.",
                "notes": "Approx EL 5. Tactical flavor: choke-point ambush. Trap hook: spring-loaded darts near entry.",
                "dnd3e": {"encounter_difficulty": danger, "dungeon_room_notes": "Room 3: cracked idol chamber, hidden switch."}
            }
        self.last_payload = payload
        self.output.setPlainText("\n".join(f"{k}: {v}" for k, v in payload.items()) + f"\nGenerated: {now_iso()}")
