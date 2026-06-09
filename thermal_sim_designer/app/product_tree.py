from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


class ProductTree(QTreeWidget):
    part_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.setHeaderLabel("Product Tree")
        self.itemSelectionChanged.connect(self._on_selection)

    def refresh(self, project) -> None:
        self.clear()
        root = QTreeWidgetItem([project.project_name])
        parts = QTreeWidgetItem(["Parts"])
        interfaces = QTreeWidgetItem(["Interfaces"])
        boundaries = QTreeWidgetItem(["Boundaries"])
        fluids = QTreeWidgetItem(["Fluids"])
        results = QTreeWidgetItem(["Results"])
        root.addChildren([parts, interfaces, boundaries, fluids, results])
        for part in project.parts:
            item = QTreeWidgetItem([part.name])
            item.setData(0, 256, part.id)
            parts.addChild(item)
        for interface in project.interfaces:
            interfaces.addChild(QTreeWidgetItem([f"{interface.type} ({interface.face_a}-{interface.face_b})"]))
        for boundary in project.boundaries:
            boundaries.addChild(QTreeWidgetItem([f"{boundary.type} {boundary.face}"]))
        for fluid in project.fluids[:20]:
            fluids.addChild(QTreeWidgetItem([fluid.name]))
        if project.results:
            results.addChild(QTreeWidgetItem([project.results.get("solver_status", "Sonuçlar")]))
        self.addTopLevelItem(root)
        self.expandAll()

    def select_part(self, part_id: str) -> None:
        for item in self.findItems("*", 1 | 2):
            if item.data(0, 256) == part_id:
                self.setCurrentItem(item)
                return

    def _on_selection(self) -> None:
        item = self.currentItem()
        if item:
            part_id = item.data(0, 256)
            if part_id:
                self.part_selected.emit(part_id)
