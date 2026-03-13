from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QTextEdit, QLineEdit, QPushButton,
    QComboBox, QLabel, QFormLayout, QGroupBox, QCheckBox
)

from modules.shared.constants import LORE_CATEGORIES
from modules.shared.utils import now_iso


class LoreManagerPanel(QWidget):
    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.selected_id: Optional[str] = None

        self.list_widget = QListWidget()
        self.title = QLineEdit()
        self.category = QComboBox()
        self.category.addItems(LORE_CATEGORIES)
        self.tags = QLineEdit()
        self.summary = QTextEdit()
        self.notes = QTextEdit()

        self.alignment = QLineEdit()
        self.bab = QLineEdit()
        self.saves = QLineEdit("Fort +0 / Ref +0 / Will +0")
        self.size = QLineEdit("Medium")
        self.speed = QLineEdit("30")
        self.spellcaster = QCheckBox("Spellcaster")
        self.caster_level = QLineEdit()

        self.search = QLineEdit()
        self._build()

    def _build(self) -> None:
        root = QHBoxLayout(self)
        left = QVBoxLayout()
        left.addWidget(QLabel("Search"))
        left.addWidget(self.search)
        self.search.textChanged.connect(self.refresh_list)
        left.addWidget(self.list_widget, 1)
        root.addLayout(left, 2)

        right = QVBoxLayout()
        form_box = QGroupBox("Lore Record")
        form = QFormLayout(form_box)
        form.addRow("Title", self.title)
        form.addRow("Category", self.category)
        form.addRow("Tags (comma)", self.tags)
        form.addRow("Summary", self.summary)
        form.addRow("Notes", self.notes)
        form.addRow("Alignment", self.alignment)
        form.addRow("BAB", self.bab)
        form.addRow("Saves", self.saves)
        form.addRow("Size", self.size)
        form.addRow("Speed", self.speed)
        form.addRow(self.spellcaster)
        form.addRow("Caster Level", self.caster_level)
        right.addWidget(form_box, 1)

        buttons = QHBoxLayout()
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.clear_editor)
        save_btn = QPushButton("Create/Update")
        save_btn.clicked.connect(self.save_current)
        del_btn = QPushButton("Delete Selected")
        del_btn.clicked.connect(self.delete_selected)
        buttons.addWidget(new_btn)
        buttons.addWidget(save_btn)
        buttons.addWidget(del_btn)
        right.addLayout(buttons)
        root.addLayout(right, 3)

        self.list_widget.currentTextChanged.connect(self.load_selected)

    def refresh(self, campaign) -> None:
        self.campaign = campaign
        self.refresh_list()

    def _record_label(self, rec: dict) -> str:
        return f"[{rec.get('category', 'Unknown')}] {rec.get('title', 'Untitled')}"

    def refresh_list(self) -> None:
        query = self.search.text().strip().lower()
        self.list_widget.clear()
        for rec in self.campaign.get("lore", []):
            text = self._record_label(rec)
            hay = f"{text} {rec.get('summary', '')} {' '.join(rec.get('tags', []))}".lower()
            if query and query not in hay:
                continue
            self.list_widget.addItem(text)

    def add_external_record(self, payload: dict) -> None:
        if not payload:
            return
        payload = dict(payload)
        payload.setdefault("id", f"lore_{len(self.campaign.get('lore', [])) + 1}")
        payload.setdefault("created_date", now_iso())
        payload["updated_date"] = now_iso()
        payload.setdefault("favorite", False)
        payload.setdefault("tags", ["imported"])
        payload.setdefault("related_records", [])
        self.campaign.setdefault("lore", []).append(payload)
        self.refresh_list()

    def _find_selected_record(self) -> Optional[dict]:
        if not self.selected_id:
            return None
        for rec in self.campaign.get("lore", []):
            if rec.get("id") == self.selected_id:
                return rec
        return None

    def save_current(self) -> None:
        existing = self._find_selected_record()
        dnd3e_data = {
            "alignment": self.alignment.text().strip(),
            "bab": self.bab.text().strip(),
            "saves": self.saves.text().strip(),
            "size": self.size.text().strip(),
            "speed": self.speed.text().strip(),
            "spellcaster": "yes" if self.spellcaster.isChecked() else "no",
            "caster_level": self.caster_level.text().strip(),
        }

        if existing is None:
            record = {
                "id": f"lore_{len(self.campaign.get('lore', [])) + 1}",
                "title": self.title.text().strip() or "Untitled",
                "category": self.category.currentText(),
                "summary": self.summary.toPlainText().strip(),
                "tags": [t.strip() for t in self.tags.text().split(",") if t.strip()],
                "related_records": [],
                "notes": self.notes.toPlainText().strip(),
                "status": "active",
                "created_date": now_iso(),
                "updated_date": now_iso(),
                "favorite": False,
                "dnd3e": dnd3e_data,
            }
            self.campaign.setdefault("lore", []).append(record)
            self.selected_id = record["id"]
        else:
            existing["title"] = self.title.text().strip() or existing.get("title", "Untitled")
            existing["category"] = self.category.currentText()
            existing["summary"] = self.summary.toPlainText().strip()
            existing["tags"] = [t.strip() for t in self.tags.text().split(",") if t.strip()]
            existing["notes"] = self.notes.toPlainText().strip()
            existing["updated_date"] = now_iso()
            existing.setdefault("dnd3e", {}).update(dnd3e_data)

        self.refresh_list()

    def load_selected(self, text: str) -> None:
        if not text:
            return
        for rec in self.campaign.get("lore", []):
            if self._record_label(rec) == text:
                self.selected_id = rec.get("id")
                d = rec.get("dnd3e", {})
                self.title.setText(rec.get("title", ""))
                self.category.setCurrentText(rec.get("category", "NPC"))
                self.tags.setText(", ".join(rec.get("tags", [])))
                self.summary.setPlainText(rec.get("summary", ""))
                self.notes.setPlainText(rec.get("notes", ""))
                self.alignment.setText(d.get("alignment", ""))
                self.bab.setText(d.get("bab", ""))
                self.saves.setText(d.get("saves", "Fort +0 / Ref +0 / Will +0"))
                self.size.setText(d.get("size", "Medium"))
                self.speed.setText(d.get("speed", "30"))
                self.spellcaster.setChecked(d.get("spellcaster", "no") == "yes")
                self.caster_level.setText(d.get("caster_level", ""))
                return

    def clear_editor(self) -> None:
        self.selected_id = None
        self.title.clear()
        self.category.setCurrentIndex(0)
        self.tags.clear()
        self.summary.clear()
        self.notes.clear()
        self.alignment.clear()
        self.bab.clear()
        self.saves.setText("Fort +0 / Ref +0 / Will +0")
        self.size.setText("Medium")
        self.speed.setText("30")
        self.spellcaster.setChecked(False)
        self.caster_level.clear()

    def delete_selected(self) -> None:
        if not self.selected_id:
            return
        self.campaign["lore"] = [r for r in self.campaign.get("lore", []) if r.get("id") != self.selected_id]
        self.clear_editor()
        self.refresh_list()
