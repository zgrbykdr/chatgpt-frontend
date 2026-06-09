from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QPen, QWheelEvent
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView


class GeometryView(QGraphicsView):
    part_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self._item_to_part: dict[object, str] = {}
        self._project = None

    def refresh(self, project) -> None:
        self._project = project
        self.scene.clear()
        self._item_to_part.clear()
        temps = [p.temperature_result for p in project.parts if p.temperature_result is not None]
        tmin = min(temps) if temps else None
        tmax = max(temps) if temps else None
        scale = 1000.0
        for part in project.parts:
            if not part.visible:
                continue
            color = self._temperature_color(part.temperature_result, tmin, tmax) if temps else QColor(part.color)
            pen = QPen(Qt.black, 1.5)
            brush = QBrush(color)
            if part.geometry_type == "circle":
                r = max(part.radius * scale, 2.0)
                item = QGraphicsEllipseItem((part.x * scale) - r, (part.y * scale) - r, 2 * r, 2 * r)
            else:
                item = QGraphicsRectItem(part.x * scale, part.y * scale, max(part.width * scale, 2.0), max(part.height * scale, 2.0))
            item.setPen(pen)
            item.setBrush(brush)
            item.setFlag(item.GraphicsItemFlag.ItemIsSelectable, True)
            item.setData(0, part.id)
            self.scene.addItem(item)
            label = QGraphicsTextItem(part.name)
            label.setPos(part.x * scale + 4, part.y * scale + 4)
            self.scene.addItem(label)
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-20, -20, 20, 20))

    def fit_view(self) -> None:
        rect = self.scene.itemsBoundingRect().adjusted(-20, -20, 20, 20)
        if rect.isValid():
            self.fitInView(rect, Qt.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent) -> None:
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            part_id = item.data(0)
            if part_id:
                self.part_selected.emit(part_id)

    def _temperature_color(self, temp, tmin, tmax) -> QColor:
        if temp is None or tmin is None or tmax is None or abs(tmax - tmin) < 1e-9:
            return QColor("#77aadd")
        ratio = max(0.0, min(1.0, (temp - tmin) / (tmax - tmin)))
        return QColor(int(50 + 205 * ratio), int(80 * (1 - ratio)), int(255 * (1 - ratio)))
