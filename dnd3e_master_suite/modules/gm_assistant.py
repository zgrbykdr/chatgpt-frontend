import random
from typing import Dict, Any

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
        self.tone = QComboBox()
        self.region = QComboBox()
        self.danger = QComboBox()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.last_payload: Dict[str, Any] = {}
        self.tables = self.data.read_json("data/generators/tables.json", {})
        self.reference = self.data.read_json("data/reference/dnd3e_reference.json", {})
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        form_box = QGroupBox("Generator Controls")
        form = QFormLayout(form_box)
        self.generator_type.addItems([
            "NPC", "Quest", "Encounter", "Rumor", "Treasure", "Trap Hook",
            "Tavern", "Settlement", "Faction Hook", "Fantasy Name", "Dungeon Hook", "Monster Group"
        ])
        self.tone.addItems(["Heroic", "Dark", "Mysterious", "Political", "Grim", "Serious"])
        self.region.addItems(["City", "Village", "Dungeon", "Forest", "Ruins", "Swamp", "Mountains"])
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
        action_row.addWidget(lore_btn)
        action_row.addWidget(story_btn)
        action_row.addWidget(battle_btn)

        layout.addWidget(form_box)
        layout.addLayout(action_row)
        layout.addWidget(self.output, 1)

    def generate_from_dashboard(self, generator_name: str) -> None:
        index = self.generator_type.findText(generator_name)
        if index >= 0:
            self.generator_type.setCurrentIndex(index)
        self.generate()

    def _npc_payload(self, tone: str, region: str, danger: str) -> Dict[str, Any]:
        names = ["Aldren", "Vaelis", "Mara", "Torvek", "Ilyra", "Drennen", "Kaelith"]
        race = random.choice(self.reference.get("races", ["Human"]))
        cls = random.choice(self.reference.get("classes", ["Fighter"]))
        alignment = random.choice(self.reference.get("alignments", ["True Neutral"]))
        level = random.randint(2, 8)
        bab = f"+{max(1, level - 1)}"
        cr_note = f"CR {max(1, level - 1)}"

        return {
            "id": f"npc_{random.randint(1000,9999)}",
            "title": f"{random.choice(names)} of {region}",
            "category": "NPC",
            "summary": f"{tone} {race} {cls} with {danger.lower()} encounter pressure.",
            "notes": (
                f"Race: {race} | Class: {cls} | Level: {level} | Alignment: {alignment} | "
                f"BAB: {bab} | Saves: Fort +3 Ref +2 Will +1 | Size: Medium | Speed: 30 | "
                f"Spellcaster: {'Yes' if cls in ['Wizard', 'Cleric', 'Druid', 'Sorcerer', 'Bard'] else 'No'} | CR note: {cr_note}"
            ),
            "tags": ["generated", "npc", region.lower(), tone.lower()],
            "dnd3e": {
                "alignment": alignment,
                "race": race,
                "class": cls,
                "level": str(level),
                "bab": bab,
                "size": "Medium",
                "speed": "30",
                "fort": "+3",
                "ref": "+2",
                "will": "+1",
                "initiative_mod": "+2",
                "ac_breakdown": "armor +4, shield +1, Dex +2, size +0, natural +0, deflection +0, misc +1",
                "attack_notes": "Melee +6 longsword, Ranged +4 shortbow, Grapple +5",
                "spellcaster": "yes" if cls in ["Wizard", "Cleric", "Druid", "Sorcerer", "Bard"] else "no",
                "caster_level": str(level if cls in ["Wizard", "Cleric", "Druid", "Sorcerer", "Bard"] else 0),
                "prepared_spells_notes": "Prepared list: utility, control, one offensive option",
                "skill_highlights": "Spot +6, Diplomacy +5, Knowledge(local) +4",
                "feat_highlights": "Alertness, Iron Will",
                "xp_reward_note": "Approx 600-1200 XP split by party size",
                "challenge_rating_note": cr_note,
            },
        }

    def _quest_payload(self, tone: str, region: str, danger: str) -> Dict[str, Any]:
        hook = random.choice(self.tables.get("quest_hooks", ["Recover a stolen heirloom"]))
        loot = random.choice(self.tables.get("loot_table", ["Coin purse and trinket cache"]))
        return {
            "id": f"quest_{random.randint(1000,9999)}",
            "title": f"{tone} Mission in the {region}",
            "category": "Quest",
            "summary": hook,
            "notes": (
                "Patron: nervous magistrate. Objective: secure evidence. Obstacles: cult patrols, trapped route. "
                "Suggested level range: 3-6. Approx EL guidance: 4-7. Hidden complication: false ally embedded with patron."
            ),
            "tags": ["generated", "quest", region.lower()],
            "dnd3e": {
                "encounter_difficulty": danger,
                "treasure_parcel_notes": loot,
                "xp_reward_note": "Quest completion bonus + encounter XP",
            },
        }

    def generate(self) -> None:
        g = self.generator_type.currentText()
        tone = self.tone.currentText()
        region = self.region.currentText()
        danger = self.danger.currentText()

        if g == "NPC":
            payload = self._npc_payload(tone, region, danger)
        elif g == "Quest":
            payload = self._quest_payload(tone, region, danger)
        elif g in {"Encounter", "Monster Group", "Dungeon Hook"}:
            group = random.choice(self.tables.get("monster_groups", ["Bandit skirmishers and one elite"] ))
            trap = random.choice(self.tables.get("trap_hooks", ["Tripwire alarm bell"] ))
            env = random.choice(self.reference.get("encounter_environments", [region.lower()]))
            payload = {
                "id": f"enc_{random.randint(1000,9999)}",
                "title": f"{tone} {region} Skirmish",
                "category": "Event",
                "summary": f"Environment: {env}. Enemy composition: {group}.",
                "notes": f"Approx EL 5. Tactical flavor: pressure front line and retreat to cover. Trap hook: {trap}.",
                "tags": ["generated", "encounter", region.lower()],
                "dnd3e": {
                    "encounter_difficulty": danger,
                    "challenge_rating_note": "Primary foes CR 2-4",
                    "dungeon_room_notes": "Room 2: chokepoint with elevation advantage.",
                    "xp_reward_note": "Calculate by CR mix and party size",
                },
            }
        elif g in {"Treasure", "Trap Hook", "Rumor", "Tavern", "Settlement", "Faction Hook", "Fantasy Name"}:
            settlement = random.choice(self.tables.get("settlement_templates", ["Busy river town with tense guild politics"]))
            trap = random.choice(self.tables.get("trap_hooks", ["False floor pit"] ))
            payload = {
                "id": f"misc_{random.randint(1000,9999)}",
                "title": f"{g}: {tone} {region} lead",
                "category": "Rumor" if g in {"Rumor", "Faction Hook"} else "Event",
                "summary": f"{settlement}.",
                "notes": f"Lead detail: {trap}. Suggested use: seed next session prep.",
                "tags": ["generated", g.lower().replace(' ', '_')],
                "dnd3e": {"encounter_difficulty": danger},
            }
        else:
            payload = {
                "id": f"entry_{random.randint(1000,9999)}",
                "title": f"{g} output",
                "category": "Event",
                "summary": "Generated content",
                "notes": "No additional notes.",
                "dnd3e": {},
            }

        self.last_payload = payload
        self.campaign.setdefault("generator_history", []).append(payload)
        self.output.setPlainText("\n".join(f"{k}: {v}" for k, v in payload.items()) + f"\nGenerated: {now_iso()}")
