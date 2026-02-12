from __future__ import annotations
import json
from pathlib import Path
from copy import deepcopy
from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel,
    QLineEdit, QFormLayout, QSpinBox, QTextEdit, QTabWidget, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QComboBox
)

try:
    from py_app.core.models import Campaign, Character
    from py_app.core.modifier_engine import recalc_character
    from py_app.services.storage import save_campaign, load_campaign
    from py_app.services.txt_feat_parser import parse_feat_txt
    from py_app.services.feat_mapping import apply_mappings_to_feats
except ModuleNotFoundError:
    from ..core.models import Campaign, Character
    from ..core.modifier_engine import recalc_character
    from ..services.storage import save_campaign, load_campaign
    from ..services.txt_feat_parser import parse_feat_txt
    from ..services.feat_mapping import apply_mappings_to_feats


STARTER_FEAT = {
    "id": "feat_improved_initiative_srd",
    "name": "Improved Initiative",
    "source": "SRD 3.5",
    "summary": "+4 bonus on initiative checks.",
    "mappingStatus": "Mapped",
    "prerequisites": [],
    "modifiers": [{"target": "initiative", "value": 4, "bonusType": "untyped"}],
}

FATIGUED_CONDITION = {
    "id": "condition_fatigued",
    "name": "Fatigued",
    "type": "condition",
    "summary": "-2 Strength and -2 Dexterity",
    "defaultDurationRounds": 10,
    "modifiers": [
        {"target": "ability.STR", "value": -2, "bonusType": "penalty"},
        {"target": "ability.DEX", "value": -2, "bonusType": "penalty"},
    ],
}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("D&D 3E DM Manager (Python)")
        self.resize(1400, 900)
        self.campaign: Campaign = Campaign()
        self._load_default_packs()
        self.current_path: Optional[Path] = None
        self.selected_char_id: Optional[str] = self.campaign.characters[0].id

        self._build_ui()
        self.refresh_all()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)

        # Sidebar
        left = QVBoxLayout()
        self.char_search = QLineEdit()
        self.char_search.setPlaceholderText("Search characters...")
        self.char_search.textChanged.connect(self.refresh_character_list)
        left.addWidget(self.char_search)
        self.char_list = QListWidget()
        self.char_list.itemSelectionChanged.connect(self._on_char_selected)
        left.addWidget(self.char_list)
        add_char_btn = QPushButton("+ Character")
        add_char_btn.clicked.connect(self.add_character)
        left.addWidget(add_char_btn)

        # Main content
        main = QVBoxLayout()
        toolbar = QHBoxLayout()
        for text, handler in [
            ("New", self.new_campaign),
            ("Load", self.load_campaign_dialog),
            ("Save", self.save_campaign_dialog),
            ("Save As", self.save_as_dialog),
            ("Import Feats TXT", self.import_feats_txt),
            ("Import Mapping JSON", self.import_mapping_json),
        ]:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            toolbar.addWidget(btn)
        main.addLayout(toolbar)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_overview_tab(), "Overview")
        self.tabs.addTab(self._build_feats_tab(), "Feats & Features")
        self.tabs.addTab(self._build_effects_tab(), "Effects/Conditions")
        self.tabs.addTab(self._build_combat_tab(), "Combat Dashboard")
        self.tabs.addTab(self._build_notes_tab(), "Notes")
        main.addWidget(self.tabs)

        left_wrap = QWidget()
        left_wrap.setLayout(left)
        left_wrap.setMaximumWidth(280)
        layout.addWidget(left_wrap)

        main_wrap = QWidget()
        main_wrap.setLayout(main)
        layout.addWidget(main_wrap)

    def _build_overview_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self.name_edit = QLineEdit()
        self.player_edit = QLineEdit()
        self.race_edit = QLineEdit()
        self.type_combo = QComboBox(); self.type_combo.addItems(["PC", "NPC"])
        self.hp_max = QSpinBox(); self.hp_max.setRange(-999, 9999)
        self.hp_current = QSpinBox(); self.hp_current.setRange(-999, 9999)
        self.hp_temp = QSpinBox(); self.hp_temp.setRange(0, 9999)
        self.hp_nonlethal = QSpinBox(); self.hp_nonlethal.setRange(0, 9999)
        self.ac_armor = QSpinBox(); self.ac_armor.setRange(-20, 50)
        self.ac_shield = QSpinBox(); self.ac_shield.setRange(-20, 50)
        self.ac_natural = QSpinBox(); self.ac_natural.setRange(-20, 50)
        self.init_misc = QSpinBox(); self.init_misc.setRange(-20, 50)

        for lbl, widget in [
            ("Name", self.name_edit), ("Player", self.player_edit), ("Race", self.race_edit), ("Type", self.type_combo),
            ("HP Max", self.hp_max), ("HP Current", self.hp_current), ("Temp HP", self.hp_temp), ("Nonlethal", self.hp_nonlethal),
            ("AC Armor", self.ac_armor), ("AC Shield", self.ac_shield), ("AC Natural", self.ac_natural), ("Initiative Misc", self.init_misc),
        ]:
            form.addRow(lbl, widget)

        self.derived_label = QLabel("Derived stats")
        form.addRow(self.derived_label)

        controls = QHBoxLayout()
        self.delta_hp = QSpinBox(); self.delta_hp.setRange(1, 999)
        dmg_btn = QPushButton("Apply Damage")
        heal_btn = QPushButton("Apply Heal")
        undo_btn = QPushButton("Undo HP")
        fat_btn = QPushButton("Apply Fatigued (10 rounds)")
        dmg_btn.clicked.connect(lambda: self.adjust_hp(-self.delta_hp.value()))
        heal_btn.clicked.connect(lambda: self.adjust_hp(self.delta_hp.value()))
        undo_btn.clicked.connect(self.undo_hp)
        fat_btn.clicked.connect(self.apply_fatigued)
        controls.addWidget(self.delta_hp); controls.addWidget(dmg_btn); controls.addWidget(heal_btn); controls.addWidget(undo_btn); controls.addWidget(fat_btn)
        form.addRow(controls)

        for widget in [self.name_edit, self.player_edit, self.race_edit]:
            widget.editingFinished.connect(self.push_overview_changes)
        self.type_combo.currentTextChanged.connect(self.push_overview_changes)
        for widget in [self.hp_max, self.hp_current, self.hp_temp, self.hp_nonlethal, self.ac_armor, self.ac_shield, self.ac_natural, self.init_misc]:
            widget.valueChanged.connect(self.push_overview_changes)

        return w

    def _build_feats_tab(self) -> QWidget:
        w = QWidget(); layout = QHBoxLayout(w)
        left = QVBoxLayout(); right = QVBoxLayout()
        self.feat_search = QLineEdit(); self.feat_search.setPlaceholderText("Search feats...")
        self.feat_search.textChanged.connect(self.refresh_feats)
        self.feat_list = QListWidget()
        add_btn = QPushButton("Select Feat for Character")
        add_btn.clicked.connect(self.add_selected_feat_to_character)
        left.addWidget(self.feat_search); left.addWidget(self.feat_list); left.addWidget(add_btn)

        self.selected_feats = QListWidget()
        right.addWidget(QLabel("Selected Feats")); right.addWidget(self.selected_feats)
        right.addWidget(QLabel("Feat Rules Mapper"))
        self.map_target = QLineEdit("initiative")
        self.map_value = QSpinBox(); self.map_value.setRange(-20, 20)
        self.map_type = QLineEdit("untyped")
        save_map_btn = QPushButton("Save Mapping")
        save_map_btn.clicked.connect(self.save_mapping)
        right.addWidget(QLabel("Target")); right.addWidget(self.map_target)
        right.addWidget(QLabel("Value")); right.addWidget(self.map_value)
        right.addWidget(QLabel("Bonus Type")); right.addWidget(self.map_type)
        right.addWidget(save_map_btn)

        layout.addLayout(left); layout.addLayout(right)
        return w

    def _build_effects_tab(self) -> QWidget:
        w = QWidget(); layout = QVBoxLayout(w)
        end_btn = QPushButton("End Round (decrement durations)")
        end_btn.clicked.connect(self.end_round)
        self.effects_list = QListWidget()
        layout.addWidget(end_btn); layout.addWidget(self.effects_list)
        return w

    def _build_combat_tab(self) -> QWidget:
        w = QWidget(); layout = QVBoxLayout(w)
        self.combat_table = QTableWidget(0, 6)
        self.combat_table.setHorizontalHeaderLabels(["Name", "Init", "HP", "AC", "Saves", "Conditions"])
        layout.addWidget(self.combat_table)
        return w

    def _build_notes_tab(self) -> QWidget:
        w = QWidget(); layout = QFormLayout(w)
        self.char_note = QTextEdit(); self.session_note = QTextEdit(); self.global_note = QTextEdit()
        self.char_note.textChanged.connect(self.push_notes_changes)
        self.session_note.textChanged.connect(self.push_notes_changes)
        self.global_note.textChanged.connect(self.push_notes_changes)
        layout.addRow("Character Notes", self.char_note)
        layout.addRow("Session Notes", self.session_note)
        layout.addRow("Campaign Global Notes", self.global_note)
        return w

    def _repo_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def _read_json_if_exists(self, path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _apply_mappings_to_feats(self, mappings: List[Dict[str, Any]]) -> int:
        return apply_mappings_to_feats(self.campaign.libraries.get("feats", []), mappings)

    def _load_default_packs(self, merge: bool = False) -> None:
        packs_dir = self._repo_root() / "data" / "packs"
        feats_pack = self._read_json_if_exists(packs_dir / "feats.json") or {"feats": []}
        conditions_pack = self._read_json_if_exists(packs_dir / "conditions.json") or {"conditions": []}
        mappings_pack = self._read_json_if_exists(packs_dir / "feat_mappings.json") or {"mappings": []}

        if not merge:
            self.campaign.libraries["feats"] = deepcopy(feats_pack.get("feats", [])) or [deepcopy(STARTER_FEAT)]
            self.campaign.libraries["conditions"] = deepcopy(conditions_pack.get("conditions", [])) or [deepcopy(FATIGUED_CONDITION)]
            self.campaign.libraries["imports"]["mappings"] = deepcopy(mappings_pack.get("mappings", []))
        else:
            existing_feats = self.campaign.libraries.setdefault("feats", [])
            for feat in feats_pack.get("feats", []):
                if not any(f.get("name") == feat.get("name") and f.get("source") == feat.get("source") for f in existing_feats):
                    existing_feats.append(deepcopy(feat))

            existing_conds = self.campaign.libraries.setdefault("conditions", [])
            for cond in conditions_pack.get("conditions", []):
                if not any(c.get("id") == cond.get("id") for c in existing_conds):
                    existing_conds.append(deepcopy(cond))

            mappings_bucket = self.campaign.libraries.setdefault("imports", {}).setdefault("mappings", [])
            for mapping in mappings_pack.get("mappings", []):
                if not any((m.get("featId") and m.get("featId") == mapping.get("featId")) or
                           (m.get("featName") == mapping.get("featName") and m.get("source") == mapping.get("source"))
                           for m in mappings_bucket):
                    mappings_bucket.append(deepcopy(mapping))

        self._apply_mappings_to_feats(self.campaign.libraries.get("imports", {}).get("mappings", []))

    def selected_char(self) -> Optional[Character]:
        for c in self.campaign.characters:
            if c.id == self.selected_char_id:
                return c
        return None

    def refresh_all(self) -> None:
        self.campaign.characters = [recalc_character(c) for c in self.campaign.characters]
        self.refresh_character_list(); self.refresh_overview(); self.refresh_feats(); self.refresh_effects(); self.refresh_combat(); self.refresh_notes()

    def refresh_character_list(self) -> None:
        q = self.char_search.text().strip().lower()
        self.char_list.blockSignals(True)
        self.char_list.clear()
        for c in self.campaign.characters:
            name = c.identity["name"]
            if q and q not in name.lower():
                continue
            self.char_list.addItem(f"{name} ({c.type})|{c.id}")
        self.char_list.blockSignals(False)

    def _on_char_selected(self) -> None:
        item = self.char_list.currentItem()
        if not item:
            return
        txt = item.text()
        self.selected_char_id = txt.split("|")[-1]
        self.refresh_all()

    def refresh_overview(self) -> None:
        c = self.selected_char()
        if not c:
            return
        self.name_edit.setText(c.identity["name"])
        self.player_edit.setText(c.identity.get("player", ""))
        self.race_edit.setText(c.identity.get("race", ""))
        self.type_combo.setCurrentText(c.type)
        self.hp_max.setValue(int(c.hp["max"])); self.hp_current.setValue(int(c.hp["current"])); self.hp_temp.setValue(int(c.hp["temp"])); self.hp_nonlethal.setValue(int(c.hp["nonlethal"]))
        self.ac_armor.setValue(int(c.combat["ac"]["armor"])); self.ac_shield.setValue(int(c.combat["ac"]["shield"])); self.ac_natural.setValue(int(c.combat["ac"]["natural"])); self.init_misc.setValue(int(c.combat["initiativeMisc"]))
        d = c.derived
        self.derived_label.setText(f"Init {d['initiative']} | AC {d['armorClass']['total']} (Touch {d['armorClass']['touch']}, Flat {d['armorClass']['flatFooted']}) | Fort {d['saves']['Fort']} Ref {d['saves']['Ref']} Will {d['saves']['Will']}")

    def push_overview_changes(self) -> None:
        c = self.selected_char()
        if not c:
            return
        c.identity["name"] = self.name_edit.text().strip() or "Unnamed"
        c.identity["player"] = self.player_edit.text().strip()
        c.identity["race"] = self.race_edit.text().strip()
        c.type = self.type_combo.currentText()
        c.hp["max"] = self.hp_max.value(); c.hp["current"] = self.hp_current.value(); c.hp["temp"] = self.hp_temp.value(); c.hp["nonlethal"] = self.hp_nonlethal.value()
        c.combat["ac"]["armor"] = self.ac_armor.value(); c.combat["ac"]["shield"] = self.ac_shield.value(); c.combat["ac"]["natural"] = self.ac_natural.value(); c.combat["initiativeMisc"] = self.init_misc.value()
        self.refresh_all()

    def adjust_hp(self, delta: int) -> None:
        c = self.selected_char()
        if not c:
            return
        c.hp["log"].append({"before": c.hp["current"], "delta": delta})
        c.hp["current"] += delta
        self.refresh_all()

    def undo_hp(self) -> None:
        c = self.selected_char()
        if not c or not c.hp["log"]:
            return
        last = c.hp["log"].pop()
        c.hp["current"] = last["before"]
        self.refresh_all()

    def apply_fatigued(self) -> None:
        c = self.selected_char()
        if not c:
            return
        c.effects.append({
            **FATIGUED_CONDITION,
            "active": True,
            "source": "Quick Apply",
            "startRound": self.campaign.currentRound,
            "remainingRounds": 10,
        })
        self.refresh_all()

    def end_round(self) -> None:
        self.campaign.currentRound += 1
        for c in self.campaign.characters:
            kept = []
            for fx in c.effects:
                rem = fx.get("remainingRounds")
                if rem is None or fx.get("active", True) is False:
                    kept.append(fx); continue
                fx["remainingRounds"] = rem - 1
                if fx["remainingRounds"] > 0:
                    kept.append(fx)
            c.effects = kept
        self.refresh_all()

    def refresh_feats(self) -> None:
        q = self.feat_search.text().strip().lower()
        feats = [f for f in self.campaign.libraries["feats"] if q in f["name"].lower()]
        self.feat_list.clear()
        for f in feats:
            self.feat_list.addItem(f"{f['name']} | {f['source']} | {f['mappingStatus']} | {f['id']}")

        self.selected_feats.clear()
        c = self.selected_char()
        if c:
            for f in c.featChoices:
                self.selected_feats.addItem(f"{f['name']} ({f['mappingStatus']})")

    def add_selected_feat_to_character(self) -> None:
        c = self.selected_char(); item = self.feat_list.currentItem()
        if not c or not item:
            return
        feat_id = item.text().split("|")[-1].strip()
        feat = next((f for f in self.campaign.libraries["feats"] if f["id"] == feat_id), None)
        if not feat:
            return
        if any(x.get("id") == feat["id"] for x in c.featChoices):
            return
        c.featChoices.append(dict(feat))
        if feat.get("mappingStatus") != "Mapped":
            QMessageBox.warning(self, "Unmapped feat", "This feat is Unmapped and will not modify stats until mapped.")
        self.refresh_all()

    def save_mapping(self) -> None:
        item = self.feat_list.currentItem()
        if not item:
            QMessageBox.information(self, "Select feat", "Select a feat in Feat Library first.")
            return
        feat_id = item.text().split("|")[-1].strip()
        feat = next((f for f in self.campaign.libraries["feats"] if f["id"] == feat_id), None)
        if not feat:
            return
        mapping = {
            "featId": feat["id"], "featName": feat["name"], "source": feat["source"],
            "prerequisites": [],
            "modifiers": [{"target": self.map_target.text().strip(), "value": self.map_value.value(), "bonusType": self.map_type.text().strip() or "untyped"}],
        }
        feat["mappingStatus"] = "Mapped"
        feat["modifiers"] = mapping["modifiers"]
        self.campaign.libraries["imports"]["mappings"].append(mapping)
        self._apply_mappings_to_feats([mapping])
        self.refresh_all()

    def import_feats_txt(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(self, "Import Feats TXT", "", "Text Files (*.txt *.tsv *.csv)")
        if not path_str:
            return
        raw = Path(path_str).read_text(encoding="utf-8")
        parsed = parse_feat_txt(raw, path_str)
        self.campaign.libraries["imports"]["sourceFiles"].append({"filePath": path_str})
        for row in parsed["rows"]:
            self.campaign.libraries["imports"]["featRows"].append(row)
            if not any(f["name"] == row["name"] and f["source"] == row["source"] for f in self.campaign.libraries["feats"]):
                self.campaign.libraries["feats"].append(row)

        mappings = self.campaign.libraries.get("imports", {}).get("mappings", [])
        mapped_now = self._apply_mappings_to_feats(mappings)

        QMessageBox.information(self, "Import complete", f"Imported {len(parsed['rows'])} feats. Auto-mapped {mapped_now} feats.")
        self.refresh_all()

    def import_mapping_json(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(self, "Import Feat Mapping JSON", "", "JSON (*.json)")
        if not path_str:
            return
        payload = json.loads(Path(path_str).read_text(encoding="utf-8"))
        mappings = payload.get("mappings", [])
        self.campaign.libraries["imports"].setdefault("mappings", []).extend(mappings)
        mapped = self._apply_mappings_to_feats(mappings)
        QMessageBox.information(self, "Mapping import", f"Loaded {len(mappings)} mappings. Applied {mapped} feat mappings.")
        self.refresh_all()

    def refresh_effects(self) -> None:
        self.effects_list.clear()
        c = self.selected_char()
        if not c:
            return
        for fx in c.effects:
            rem = fx.get("remainingRounds", "Permanent")
            self.effects_list.addItem(f"{fx.get('name')} ({fx.get('type')}) - {rem}")

    def refresh_combat(self) -> None:
        chars = sorted([recalc_character(c) for c in self.campaign.characters], key=lambda x: x.derived["initiative"], reverse=True)
        self.combat_table.setRowCount(len(chars))
        for r, c in enumerate(chars):
            self.combat_table.setItem(r, 0, QTableWidgetItem(c.identity["name"]))
            self.combat_table.setItem(r, 1, QTableWidgetItem(str(c.derived["initiative"])))
            self.combat_table.setItem(r, 2, QTableWidgetItem(f"{c.hp['current']}/{c.hp['max']} (+{c.hp['temp']})"))
            self.combat_table.setItem(r, 3, QTableWidgetItem(str(c.derived["armorClass"]["total"])))
            saves = c.derived["saves"]
            self.combat_table.setItem(r, 4, QTableWidgetItem(f"F {saves['Fort']} R {saves['Ref']} W {saves['Will']}"))
            conds = ", ".join(fx.get("name", "") for fx in c.effects if fx.get("active", True))
            self.combat_table.setItem(r, 5, QTableWidgetItem(conds))

    def refresh_notes(self) -> None:
        c = self.selected_char()
        if not c:
            return
        self.char_note.blockSignals(True); self.session_note.blockSignals(True); self.global_note.blockSignals(True)
        self.char_note.setPlainText(c.notes.get("persistent", ""))
        self.session_note.setPlainText(c.notes.get("session", ""))
        self.global_note.setPlainText(self.campaign.globalNotes)
        self.char_note.blockSignals(False); self.session_note.blockSignals(False); self.global_note.blockSignals(False)

    def push_notes_changes(self) -> None:
        c = self.selected_char()
        if not c:
            return
        c.notes["persistent"] = self.char_note.toPlainText()
        c.notes["session"] = self.session_note.toPlainText()
        self.campaign.globalNotes = self.global_note.toPlainText()

    def add_character(self) -> None:
        self.campaign.characters.append(Character())
        self.selected_char_id = self.campaign.characters[-1].id
        self.refresh_all()

    def new_campaign(self) -> None:
        self.campaign = Campaign()
        self._load_default_packs()
        self.selected_char_id = self.campaign.characters[0].id
        self.current_path = None
        self.refresh_all()

    def save_as_dialog(self) -> None:
        path_str, _ = QFileDialog.getSaveFileName(self, "Save Campaign", "campaign.json", "JSON (*.json)")
        if not path_str:
            return
        self.current_path = Path(path_str)
        self.save_campaign_dialog()

    def save_campaign_dialog(self) -> None:
        if self.current_path is None:
            self.save_as_dialog(); return
        save_campaign(self.campaign, self.current_path)
        QMessageBox.information(self, "Saved", f"Saved to {self.current_path}")

    def load_campaign_dialog(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(self, "Load Campaign", "", "JSON (*.json)")
        if not path_str:
            return
        self.current_path = Path(path_str)
        self.campaign = load_campaign(self.current_path)
        self._load_default_packs(merge=True)
        self.selected_char_id = self.campaign.characters[0].id if self.campaign.characters else None
        self.refresh_all()
