from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from thermal2d.io.project_io import load_project
from thermal2d.mesher import StructuredMesher
from thermal2d.solver import HeatSolver


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Thermal2D Studio")
        self.resize(1200, 700)

        root = QWidget()
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)

        split = QSplitter(Qt.Horizontal)
        self.table = QTableWidget(30, 30)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        split.addWidget(self.table)
        split.addWidget(self.log)
        lay.addWidget(QLabel("Thermal field preview / log"))
        lay.addWidget(split)

        open_action = QAction("Open Project", self)
        open_action.triggered.connect(self.open_project)
        run_action = QAction("Run", self)
        run_action.triggered.connect(self.run_project)

        m = self.menuBar().addMenu("File")
        m.addAction(open_action)
        m.addAction(run_action)

        self.project_path: str | None = None

    def open_project(self) -> None:
        p, _ = QFileDialog.getOpenFileName(self, "Open Project", str(Path.cwd()), "Project (*.json)")
        if p:
            self.project_path = p
            self.log.appendPlainText(f"Loaded: {p}")

    def run_project(self) -> None:
        if not self.project_path:
            QMessageBox.warning(self, "No project", "Open a project file first.")
            return
        project = load_project(self.project_path)
        mesh = StructuredMesher().generate(project)
        solver = HeatSolver(project, mesh)
        result = solver.solve_steady() if project.solver.mode == "steady" else solver.solve_transient()
        arr = result.temperature
        arr = (arr - np.min(arr)) / (np.ptp(arr) + 1e-9)
        ny, nx = result.temperature.shape
        self.table.setRowCount(ny)
        self.table.setColumnCount(nx)
        for j in range(ny):
            for i in range(nx):
                v = arr[j, i]
                it = QTableWidgetItem(f"{result.temperature[j, i]:.1f}")
                color = int(255 * v)
                it.setBackground(Qt.GlobalColor.red if color > 127 else Qt.GlobalColor.cyan)
                self.table.setItem(j, i, it)
        self.log.appendPlainText("Simulation complete")


def run_gui() -> None:
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
