from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from engine import MapEngine


@dataclass
class ViewState:
    zoom_percent: int = 100


def bootstrap_demo_output() -> Path:
    out = Path("output")
    out.mkdir(exist_ok=True)
    engine = MapEngine(seed=123)
    heightmap = engine.generate_tectonic_heightmap(2048, 2048, plates=20)
    heightmap = engine.erode(heightmap, iterations=55)
    climate = engine.generate_climate(heightmap)
    rivers = engine.generate_rivers(heightmap, count=160)
    biome = engine.biome_map(heightmap, climate)
    composite = engine.render_composite(biome, rivers, lighting_strength=0.45)
    engine.export_png(composite, out / "demo_world.png")
    engine.export_heightmap(heightmap, out / "demo_height_16bit.png")
    return out


def run_gui() -> None:
    from PIL import ImageQt
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QAction, QIcon, QPainter, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QDockWidget,
        QFileDialog,
        QFormLayout,
        QGraphicsPixmapItem,
        QGraphicsScene,
        QGraphicsView,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSlider,
        QSpinBox,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )

    class InfiniteCanvasView(QGraphicsView):
        def __init__(self, scene: QGraphicsScene, state: ViewState, parent: QWidget | None = None) -> None:
            super().__init__(scene, parent)
            self.state = state
            self.setRenderHint(QPainter.Antialiasing, True)
            self.setRenderHint(QPainter.SmoothPixmapTransform, True)
            self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setBackgroundBrush(Qt.black)
            self.setSceneRect(-200000, -200000, 400000, 400000)

        def wheelEvent(self, event) -> None:
            factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            current = self.state.zoom_percent
            target = int(np.clip(current * factor, 10, 800))
            factor = target / max(current, 1)
            self.state.zoom_percent = target
            self.scale(factor, factor)

    class RPGMapStudio(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("AetherForge Cartographer - AAA RPG World Builder")
            self.resize(1600, 950)
            self.engine = MapEngine(seed=77)
            self.view_state = ViewState()

            self.scene = QGraphicsScene(self)
            self.canvas = InfiniteCanvasView(self.scene, self.view_state, self)
            self.setCentralWidget(self.canvas)
            self.image_item = QGraphicsPixmapItem()
            self.scene.addItem(self.image_item)

            self.current_heightmap: np.ndarray | None = None
            self.current_preview: np.ndarray | None = None

            self._build_toolbar()
            self._build_docks()
            self._apply_dark_theme()
            self._refresh_status()

        def _build_toolbar(self) -> None:
            toolbar = QToolBar("Main")
            toolbar.setMovable(False)
            self.addToolBar(toolbar)

            generate_action = QAction(QIcon(), "Generate World", self)
            generate_action.triggered.connect(self.generate_world)
            toolbar.addAction(generate_action)

            export_action = QAction(QIcon(), "Export PNG", self)
            export_action.triggered.connect(self.export_png)
            toolbar.addAction(export_action)

            export_height_action = QAction(QIcon(), "Export 16-bit Heightmap", self)
            export_height_action.triggered.connect(self.export_heightmap)
            toolbar.addAction(export_height_action)

            self.status_label = QLabel("Zoom 100%")
            toolbar.addSeparator()
            toolbar.addWidget(self.status_label)

        def _build_docks(self) -> None:
            self._build_generation_dock()
            self._build_layers_dock()
            self._build_assets_dock()

        def _build_generation_dock(self) -> None:
            dock = QDockWidget("World Generation", self)
            dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            wrapper = QWidget()
            form = QFormLayout(wrapper)

            self.resolution_spin = QSpinBox()
            self.resolution_spin.setRange(1024, 16384)
            self.resolution_spin.setSingleStep(1024)
            self.resolution_spin.setValue(4096)
            form.addRow("Resolution", self.resolution_spin)

            self.plate_spin = QSpinBox()
            self.plate_spin.setRange(4, 40)
            self.plate_spin.setValue(18)
            form.addRow("Tectonic Plates", self.plate_spin)

            self.erosion_slider = QSlider(Qt.Horizontal)
            self.erosion_slider.setRange(1, 90)
            self.erosion_slider.setValue(45)
            form.addRow("Erosion Iterations", self.erosion_slider)

            self.river_spin = QSpinBox()
            self.river_spin.setRange(10, 500)
            self.river_spin.setValue(120)
            form.addRow("River Seeds", self.river_spin)

            self.lighting_slider = QSlider(Qt.Horizontal)
            self.lighting_slider.setRange(0, 100)
            self.lighting_slider.setValue(40)
            form.addRow("Atmospheric Lighting", self.lighting_slider)

            generate_button = QPushButton("Generate Cinematic World")
            generate_button.clicked.connect(self.generate_world)
            form.addRow(generate_button)

            dock.setWidget(wrapper)
            self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        def _build_layers_dock(self) -> None:
            dock = QDockWidget("Layer Stack", self)
            dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            widget = QWidget()
            layout = QVBoxLayout(widget)
            self.layer_list = QListWidget()
            self.layer_list.addItems([
                "Base Heightmap (non-destructive)",
                "Biome Blend Layer",
                "River Network Overlay",
                "Kingdom Border Simulation",
                "Faction Influence Heatmap",
                "Weather Animation Layer",
                "Volumetric Cloud Lighting",
            ])
            layout.addWidget(self.layer_list)
            row = QHBoxLayout()
            row.addWidget(QPushButton("Add Layer"))
            row.addWidget(QPushButton("Duplicate"))
            row.addWidget(QPushButton("Group"))
            layout.addLayout(row)
            dock.setWidget(widget)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)

        def _build_assets_dock(self) -> None:
            dock = QDockWidget("Assets & Simulation", self)
            dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            widget = QWidget()
            layout = QVBoxLayout(widget)
            asset_list = QListWidget()
            asset_list.addItems([
                "City Generator (village/town/capital)",
                "Architectural Themes: medieval/elven/dwarven/desert/oriental/steampunk",
                "Trade Route AI",
                "Procedural Name Generator",
                "Culture & Language Profiles",
                "Political Tension Overlay",
                "Warfront Simulation Visualizer",
                "Hex/Square/Grid Tools",
            ])
            layout.addWidget(asset_list)
            layout.addWidget(QPushButton("Import Symbol Pack"))
            layout.addWidget(QPushButton("API Export Settings"))
            dock.setWidget(widget)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)

        def generate_world(self) -> None:
            resolution = self.resolution_spin.value()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            hm = self.engine.generate_tectonic_heightmap(resolution, resolution, plates=self.plate_spin.value())
            hm = self.engine.erode(hm, iterations=self.erosion_slider.value())
            climate = self.engine.generate_climate(hm)
            rivers = self.engine.generate_rivers(hm, count=self.river_spin.value())
            biome = self.engine.biome_map(hm, climate)
            composite = self.engine.render_composite(biome, rivers, lighting_strength=self.lighting_slider.value() / 100.0)
            QApplication.restoreOverrideCursor()

            self.current_heightmap = hm
            self.current_preview = composite
            qimage = ImageQt.ImageQt(composite)
            pixmap = QPixmap.fromImage(qimage)
            self.image_item.setPixmap(pixmap)
            self.image_item.setOffset(QPointF(-pixmap.width() / 2, -pixmap.height() / 2))
            self._refresh_status(f"Generated {resolution}x{resolution} map")

        def export_png(self) -> None:
            if self.current_preview is None:
                QMessageBox.warning(self, "Nothing to Export", "Generate a world first.")
                return
            target, _ = QFileDialog.getSaveFileName(self, "Export PNG", "world_map.png", "PNG (*.png)")
            if target:
                self.engine.export_png(self.current_preview, target)
                self._refresh_status(f"Exported PNG: {target}")

        def export_heightmap(self) -> None:
            if self.current_heightmap is None:
                QMessageBox.warning(self, "Nothing to Export", "Generate a world first.")
                return
            target, _ = QFileDialog.getSaveFileName(self, "Export Heightmap", "world_height.png", "PNG 16-bit (*.png)")
            if target:
                self.engine.export_heightmap(self.current_heightmap, target)
                self._refresh_status(f"Exported 16-bit: {target}")

        def _apply_dark_theme(self) -> None:
            self.setStyleSheet(
                "QMainWindow { background: #11131a; color: #d8dbe6; }"
                "QDockWidget { color: #d8dbe6; font-size: 12px; }"
                "QWidget { background: #171a22; color: #d8dbe6; }"
                "QListWidget, QSpinBox, QSlider, QPushButton { background: #222737; border: 1px solid #30364a; border-radius: 6px; padding: 5px; }"
                "QToolBar { background: #151925; spacing: 8px; border-bottom: 1px solid #2f3446; }"
                "QPushButton:hover { background: #2a3250; }"
            )

        def _refresh_status(self, text: str | None = None) -> None:
            message = text or "Ready for high-fidelity world generation"
            self.status_label.setText(f"{message} | Zoom {self.view_state.zoom_percent}%")

    app = QApplication(sys.argv)
    win = RPGMapStudio()
    win.show()
    sys.exit(app.exec())


def main() -> None:
    if "--generate-demo" in sys.argv:
        folder = bootstrap_demo_output()
        print(f"Generated demo outputs in: {folder.resolve()}")
        return
    run_gui()


if __name__ == "__main__":
    main()
