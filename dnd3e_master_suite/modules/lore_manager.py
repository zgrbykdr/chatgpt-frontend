from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QTextEdit, QLineEdit, QPushButton,
    QComboBox, QLabel, QFormLayout, QGroupBox
)
from modules.shared.constants import LORE_CATEGORIES
from modules.shared.utils import now_iso


class LoreManagerPanel(QWidget):
    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.list_widget = QListWidget()
        self.title = QLineEdit(); self.category = QComboBox(); self.category.addItems(LORE_CATEGORIES)
        self.tags = QLineEdit(); self.summary = QTextEdit(); self.notes = QTextEdit()
        self.search = QLineEdit()
        self._build()

    def _build(self) -> None:
        root = QHBoxLayout(self)
        left = QVBoxLayout()
        left.addWidget(QLabel("Search")); left.addWidget(self.search)
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
        right.addWidget(form_box, 1)
        buttons = QHBoxLayout()
        save_btn = QPushButton("Create/Update")
        save_btn.clicked.connect(self.save_current)
        del_btn = QPushButton("Delete Selected")
        del_btn.clicked.connect(self.delete_selected)
        buttons.addWidget(save_btn); buttons.addWidget(del_btn)
        right.addLayout(buttons)
        root.addLayout(right, 3)

        self.list_widget.currentTextChanged.connect(self.load_selected)

    def refresh(self, campaign) -> None:
        self.campaign = campaign
        self.refresh_list()

    def refresh_list(self) -> None:
        query = self.search.text().strip().lower()
        self.list_widget.clear()
        for rec in self.campaign.get("lore", []):
            text = f"[{rec.get('category')}] {rec.get('title')}"
            if query and query not in text.lower() and query not in rec.get("summary", "").lower():
                continue
            self.list_widget.addItem(text)

    def add_external_record(self, payload: dict) -> None:
        if not payload:
            return
        payload.setdefault("created_date", now_iso())
        payload["updated_date"] = now_iso()
        self.campaign.setdefault("lore", []).append(payload)
        self.refresh_list()

    def save_current(self) -> None:
        new_rec = {
            "id": f"lore_{len(self.campaign.get('lore', [])) + 1}",
            "title": self.title.text().strip(),
            "category": self.category.currentText(),
            "summary": self.summary.toPlainText().strip(),
            "tags": [t.strip() for t in self.tags.text().split(",") if t.strip()],
            "notes": self.notes.toPlainText().strip(),
            "status": "active",
            "created_date": now_iso(),
            "updated_date": now_iso(),
            "favorite": False,
            "dnd3e": {},
        }
        self.campaign.setdefault("lore", []).append(new_rec)
        self.refresh_list()

    def load_selected(self, text: str) -> None:
        if not text:
            return
        for rec in self.campaign.get("lore", []):
            if rec.get("title") in text:
                self.title.setText(rec.get("title", ""))
                self.category.setCurrentText(rec.get("category", "NPC"))
                self.tags.setText(", ".join(rec.get("tags", [])))
                self.summary.setPlainText(rec.get("summary", ""))
                self.notes.setPlainText(rec.get("notes", ""))
                return

    def delete_selected(self) -> None:
        text = self.list_widget.currentItem().text() if self.list_widget.currentItem() else ""
        if not text:
            return
        self.campaign["lore"] = [r for r in self.campaign.get("lore", []) if f"[{r.get('category')}] {r.get('title')}" != text]
        self.refresh_list()
