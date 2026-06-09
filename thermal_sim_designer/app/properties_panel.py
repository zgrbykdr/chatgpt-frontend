from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QLineEdit, QPushButton, QVBoxLayout, QWidget


class PropertiesPanel(QWidget):
    apply_requested = Signal(dict)
    add_boundary_requested = Signal()
    add_interface_requested = Signal()
    predict_h_requested = Signal()
    run_solver_requested = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        group = QGroupBox("Part Properties")
        form = QFormLayout(group)
        self.name = QLineEdit()
        self.geometry_type = QComboBox(); self.geometry_type.addItems(["rectangle", "circle"])
        self.x = self._spin(-1e6, 1e6, 0)
        self.y = self._spin(-1e6, 1e6, 0)
        self.width = self._spin(1e-9, 1e6, 0.1)
        self.height = self._spin(1e-9, 1e6, 0.05)
        self.radius = self._spin(1e-9, 1e6, 0.025)
        self.thickness = self._spin(1e-9, 1e6, 0.005)
        self.material = QComboBox()
        self.heat_power = self._spin(-1e9, 1e9, 0)
        self.initial_temperature = self._spin(-273, 1e6, 25)
        for label, widget in [("Name", self.name), ("Geometry Type", self.geometry_type), ("X", self.x), ("Y", self.y), ("Width", self.width), ("Height", self.height), ("Radius", self.radius), ("Thickness", self.thickness), ("Material", self.material), ("Heat Power", self.heat_power), ("Initial Temperature", self.initial_temperature)]:
            form.addRow(label, widget)
        layout.addWidget(group)
        self.apply_button = QPushButton("Apply Changes")
        self.assign_button = QPushButton("Assign Material")
        self.boundary_button = QPushButton("Add Boundary")
        self.interface_button = QPushButton("Add Interface")
        self.predict_button = QPushButton("Predict h")
        self.solve_button = QPushButton("Run Solver")
        for button in [self.apply_button, self.assign_button, self.boundary_button, self.interface_button, self.predict_button, self.solve_button]:
            layout.addWidget(button)
        layout.addStretch(1)
        self.apply_button.clicked.connect(self._emit_apply)
        self.assign_button.clicked.connect(self._emit_apply)
        self.boundary_button.clicked.connect(self.add_boundary_requested.emit)
        self.interface_button.clicked.connect(self.add_interface_requested.emit)
        self.predict_button.clicked.connect(self.predict_h_requested.emit)
        self.solve_button.clicked.connect(self.run_solver_requested.emit)
        self.current_part_id = None

    def _spin(self, low, high, value):
        spin = QDoubleSpinBox(); spin.setRange(low, high); spin.setDecimals(8); spin.setValue(value); return spin

    def set_materials(self, materials) -> None:
        current = self.material.currentText()
        self.material.clear(); self.material.addItems([m.name for m in materials])
        if current:
            self.material.setCurrentText(current)

    def load_part(self, part) -> None:
        self.current_part_id = part.id if part else None
        enabled = part is not None
        self.setEnabled(enabled)
        if not part:
            return
        self.name.setText(part.name)
        self.geometry_type.setCurrentText(part.geometry_type)
        self.x.setValue(part.x); self.y.setValue(part.y); self.width.setValue(part.width); self.height.setValue(part.height)
        self.radius.setValue(part.radius); self.thickness.setValue(part.thickness)
        self.material.setCurrentText(part.material_name)
        self.heat_power.setValue(part.heat_power); self.initial_temperature.setValue(part.initial_temperature)

    def _emit_apply(self) -> None:
        if not self.current_part_id:
            return
        self.apply_requested.emit({
            "id": self.current_part_id, "name": self.name.text().strip() or "Part", "geometry_type": self.geometry_type.currentText(),
            "x": self.x.value(), "y": self.y.value(), "width": self.width.value(), "height": self.height.value(),
            "radius": self.radius.value(), "thickness": self.thickness.value(), "material_name": self.material.currentText(),
            "heat_power": self.heat_power.value(), "initial_temperature": self.initial_temperature.value(),
        })
