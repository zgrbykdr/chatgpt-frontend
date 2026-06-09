from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class ResultsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.summary = QLabel("Solver henüz çalıştırılmadı.")
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Part Name", "Material", "Heat Power W", "Temperature C", "Warnings"])
        layout.addWidget(self.summary)
        layout.addWidget(self.table)

    def refresh(self, project) -> None:
        res = project.results or {}
        self.summary.setText(
            f"Total Heat In: {res.get('energy_in', 0):.3f} W | "
            f"Total Heat Out: {res.get('energy_out', 0):.3f} W | "
            f"Energy Balance Error: {res.get('energy_error_percent', 0):.3f}% | "
            f"Solver Status: {res.get('solver_status', 'Çalışmadı')}"
        )
        warnings = "; ".join(res.get("warnings", []))
        self.table.setRowCount(len(project.parts))
        for row, part in enumerate(project.parts):
            values = [part.name, part.material_name, f"{part.heat_power:.3f}", "" if part.temperature_result is None else f"{part.temperature_result:.3f}", warnings]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.table.resizeColumnsToContents()
