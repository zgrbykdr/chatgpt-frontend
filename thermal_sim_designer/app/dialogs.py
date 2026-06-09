from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLineEdit, QTextEdit, QVBoxLayout

from core.boundary import BoundaryCondition
from core.interface import Interface


class BoundaryDialog(QDialog):
    def __init__(self, project, part_id: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Boundary Condition")
        self.part_id = part_id
        layout = QFormLayout(self)
        self.face = QComboBox(); self.face.addItems(["left", "right", "top", "bottom", "front", "back", "all"])
        self.type = QComboBox(); self.type.addItems(["adiabatic", "fixed_temperature", "heat_flux", "heat_power", "convection"])
        self.value = QDoubleSpinBox(); self.value.setRange(-1e9, 1e9); self.value.setValue(25)
        self.ambient = QDoubleSpinBox(); self.ambient.setRange(-273, 1e6); self.ambient.setValue(25)
        self.h = QDoubleSpinBox(); self.h.setRange(0.001, 1e6); self.h.setValue(10)
        self.fluid = QComboBox(); self.fluid.addItems([f.name for f in project.fluids])
        for label, widget in [("Face", self.face), ("Type", self.type), ("Value", self.value), ("Ambient C", self.ambient), ("Fluid", self.fluid), ("h W/m²K", self.h)]:
            layout.addRow(label, widget)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def boundary(self) -> BoundaryCondition:
        return BoundaryCondition(part_id=self.part_id, face=self.face.currentText(), type=self.type.currentText(), value=self.value.value(), ambient_temperature=self.ambient.value(), fluid_name=self.fluid.currentText(), h_value=self.h.value())


class InterfaceDialog(QDialog):
    def __init__(self, project, part_id: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interface")
        layout = QFormLayout(self)
        self.part_a = QComboBox(); self.part_b = QComboBox()
        for part in project.parts:
            self.part_a.addItem(part.name, part.id); self.part_b.addItem(part.name, part.id)
        self.part_a.setCurrentIndex(max(0, self.part_a.findData(part_id)))
        if self.part_b.count() > 1 and self.part_b.currentData() == part_id:
            self.part_b.setCurrentIndex(1)
        self.type = QComboBox(); self.type.addItems(["perfect_contact", "contact_resistance", "thermal_pad", "air_gap", "adiabatic"])
        self.area = QDoubleSpinBox(); self.area.setRange(1e-12, 1e6); self.area.setDecimals(8); self.area.setValue(0.001)
        self.r = QDoubleSpinBox(); self.r.setRange(1e-12, 1e9); self.r.setDecimals(8); self.r.setValue(0.1)
        self.thickness = QDoubleSpinBox(); self.thickness.setRange(1e-9, 1e3); self.thickness.setDecimals(8); self.thickness.setValue(0.001)
        self.material = QComboBox(); self.material.addItems([m.name for m in project.materials])
        for label, widget in [("Part A", self.part_a), ("Part B", self.part_b), ("Type", self.type), ("Area m²", self.area), ("R K/W", self.r), ("Thickness m", self.thickness), ("Material", self.material)]:
            layout.addRow(label, widget)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def interface(self) -> Interface:
        return Interface(part_a_id=self.part_a.currentData(), part_b_id=self.part_b.currentData(), type=self.type.currentText(), contact_area=self.area.value(), contact_resistance=self.r.value(), thickness=self.thickness.value(), material_name=self.material.currentText())


class LibraryDialog(QDialog):
    def __init__(self, title: str, rows: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        text = QTextEdit(); text.setReadOnly(True); text.setText("\n".join(rows))
        layout.addWidget(text)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok); buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
