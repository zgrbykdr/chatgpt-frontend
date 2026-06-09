from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QMainWindow, QMessageBox, QPushButton, QSplitter, QTabWidget, QToolBar, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from app.dialogs import BoundaryDialog, InterfaceDialog, LibraryDialog
from app.geometry_view import GeometryView
from app.product_tree import ProductTree
from app.properties_panel import PropertiesPanel
from app.results_view import ResultsView
from core.boundary import BoundaryCondition
from core.convection_predictor import ConvectionPredictor
from core.fluid import fluid_by_name
from core.project import Project, ensure_default_data
from core.solver import ThermalResistanceSolver
from post.heat_flux_plot import create_heat_flux_figure
from post.temperature_plot import create_temperature_figure


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ensure_default_data()
        self.project = Project.new_project()
        self.project_path: Path | None = None
        self.dirty = False
        self.selected_part_id = self.project.parts[0].id if self.project.parts else None
        self.setWindowTitle("ThermalSim Designer")
        self.resize(1300, 800)
        self._build_ui()
        self._build_menus()
        self.refresh_all()
        QTimer.singleShot(200, self.geometry_view.fit_view)

    def _build_ui(self) -> None:
        self.tree = ProductTree(); self.geometry_view = GeometryView(); self.properties = PropertiesPanel(); self.results = ResultsView()
        self.properties.set_materials(self.project.materials)
        toolbar = QToolBar("Geometry Tools")
        fit = QPushButton("Fit View"); fit.clicked.connect(self.geometry_view.fit_view); toolbar.addWidget(fit); self.addToolBar(toolbar)
        splitter = QSplitter(); splitter.addWidget(self.tree)
        center = QTabWidget(); geo_page = QWidget(); geo_layout = QVBoxLayout(geo_page); geo_layout.addWidget(self.geometry_view); center.addTab(geo_page, "2D Geometry View"); center.addTab(self.results, "Results / Post Processing")
        splitter.addWidget(center); splitter.addWidget(self.properties); splitter.setSizes([250, 750, 300])
        self.setCentralWidget(splitter)
        self.tree.part_selected.connect(self.select_part); self.geometry_view.part_selected.connect(self.select_part)
        self.properties.apply_requested.connect(self.apply_part_changes); self.properties.add_boundary_requested.connect(self.add_boundary)
        self.properties.add_interface_requested.connect(self.add_interface); self.properties.predict_h_requested.connect(self.predict_h); self.properties.run_solver_requested.connect(self.run_solver)

    def _build_menus(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        self._add_action(file_menu, "New Project", self.new_project); self._add_action(file_menu, "Open Project", self.open_project); self._add_action(file_menu, "Save Project", self.save_project); self._add_action(file_menu, "Save Project As", self.save_project_as); self._add_action(file_menu, "Exit", self.close)
        geo_menu = menu.addMenu("Geometry")
        self._add_action(geo_menu, "New Part", lambda: self.new_part("rectangle")); self._add_action(geo_menu, "Delete Part", self.delete_part); self._add_action(geo_menu, "Rectangle Part", lambda: self.new_part("rectangle")); self._add_action(geo_menu, "Circle Part", lambda: self.new_part("circle"))
        mat_menu = menu.addMenu("Materials")
        self._add_action(mat_menu, "Material Library", self.show_material_library); self._add_action(mat_menu, "Assign Material", self.properties._emit_apply)
        fluid_menu = menu.addMenu("Fluids")
        self._add_action(fluid_menu, "Fluid Library", self.show_fluid_library); self._add_action(fluid_menu, "Assign Fluid", self.add_boundary)
        b_menu = menu.addMenu("Boundary")
        self._add_action(b_menu, "Add Boundary Condition", self.add_boundary); self._add_action(b_menu, "Add Interface", self.add_interface)
        solve_menu = menu.addMenu("Solve")
        self._add_action(solve_menu, "Run Thermal Resistance Solver", self.run_solver); self._add_action(solve_menu, "Predict Convection Coefficient", self.predict_h)
        res_menu = menu.addMenu("Results")
        self._add_action(res_menu, "Temperature Map", self.show_temperature_plot); self._add_action(res_menu, "Heat Flux View", self.show_heat_flux_plot); self._add_action(res_menu, "Result Table", lambda: self.results.refresh(self.project))
        help_menu = menu.addMenu("Help"); self._add_action(help_menu, "About", self.about)

    def _add_action(self, menu, title, callback):
        action = menu.addAction(title); action.triggered.connect(callback); return action

    def refresh_all(self) -> None:
        self.properties.set_materials(self.project.materials)
        self.tree.refresh(self.project); self.geometry_view.refresh(self.project); self.results.refresh(self.project)
        self.select_part(self.selected_part_id, emit_tree=False)

    def select_part(self, part_id: str, emit_tree: bool = True) -> None:
        part = self.project.get_part_by_id(part_id) if part_id else None
        if not part and self.project.parts:
            part = self.project.parts[0]
        self.selected_part_id = part.id if part else None
        self.properties.load_part(part)
        if emit_tree and part:
            self.tree.select_part(part.id)

    def mark_dirty(self): self.dirty = True

    def maybe_save(self) -> bool:
        if not self.dirty: return True
        reply = QMessageBox.question(self, "Kaydedilmemiş değişiklik", "Projeyi kaydetmek ister misiniz?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if reply == QMessageBox.Cancel: return False
        if reply == QMessageBox.Yes: return self.save_project()
        return True

    def new_project(self):
        if self.maybe_save():
            self.project = Project.new_project(); self.project_path = None; self.dirty = False; self.selected_part_id = self.project.parts[0].id; self.refresh_all()

    def open_project(self):
        if not self.maybe_save(): return
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", str(Path.cwd()), "JSON (*.json)")
        if path:
            try:
                self.project = Project.load_from_file(path); self.project_path = Path(path); self.dirty = False; self.selected_part_id = self.project.parts[0].id if self.project.parts else None; self.refresh_all()
            except Exception as exc:
                QMessageBox.warning(self, "Açma hatası", str(exc))

    def save_project(self) -> bool:
        if not self.project_path: return self.save_project_as()
        try:
            self.project.save_to_file(self.project_path); self.dirty = False; return True
        except Exception as exc:
            QMessageBox.warning(self, "Kayıt hatası", str(exc)); return False

    def save_project_as(self) -> bool:
        path, _ = QFileDialog.getSaveFileName(self, "Save Project As", "thermal_project.json", "JSON (*.json)")
        if not path: return False
        self.project_path = Path(path); return self.save_project()

    def new_part(self, geometry_type: str):
        part = self.project.add_part(geometry_type); self.selected_part_id = part.id; self.mark_dirty(); self.refresh_all()

    def delete_part(self):
        if self.selected_part_id and self.project.delete_part(self.selected_part_id):
            self.selected_part_id = self.project.parts[0].id if self.project.parts else None; self.mark_dirty(); self.refresh_all()

    def apply_part_changes(self, data: dict):
        part = self.project.get_part_by_id(data.pop("id"))
        if not part: return
        for key, value in data.items(): setattr(part, key, value)
        self.project.touch(); self.mark_dirty(); self.refresh_all()

    def add_boundary(self):
        if not self.selected_part_id: return
        dialog = BoundaryDialog(self.project, self.selected_part_id, self)
        if dialog.exec():
            self.project.add_boundary(dialog.boundary()); self.mark_dirty(); self.refresh_all()

    def add_interface(self):
        if len(self.project.parts) < 2:
            QMessageBox.information(self, "Interface", "Interface için en az iki parça gerekir."); return
        dialog = InterfaceDialog(self.project, self.selected_part_id, self)
        if dialog.exec():
            interface = dialog.interface()
            if interface.part_a_id == interface.part_b_id:
                QMessageBox.warning(self, "Interface", "İki farklı parça seçin."); return
            self.project.add_interface(interface); self.mark_dirty(); self.refresh_all()

    def run_solver(self):
        result = ThermalResistanceSolver().solve(self.project)
        self.mark_dirty(); self.refresh_all()
        (QMessageBox.information if result.success else QMessageBox.warning)(self, "Solver", result.message)

    def predict_h(self):
        fluid = fluid_by_name(self.project.fluids, "Air")
        part = self.project.get_part_by_id(self.selected_part_id) if self.selected_part_id else None
        length = part.characteristic_length() if part else 0.1
        try:
            pred = ConvectionPredictor().predict(fluid, "forced_external_flat_plate", velocity=1.0, characteristic_length=length)
            QMessageBox.information(self, "Predict h", f"h = {pred.h_value:.3f} W/m²K\n{pred.correlation_name}\nRe={pred.Re:.2f}, Nu={pred.Nu:.2f}")
        except Exception as exc:
            QMessageBox.warning(self, "Predict h", str(exc))

    def _show_plot(self, figure_factory, title: str):
        try:
            figure = figure_factory(self.project)
        except Exception as exc:
            QMessageBox.warning(self, title, str(exc)); return
        window = QMainWindow(self); window.setWindowTitle(title); window.setCentralWidget(FigureCanvasQTAgg(figure)); window.resize(700, 500); window.show()

    def show_temperature_plot(self): self._show_plot(create_temperature_figure, "Temperature Map")
    def show_heat_flux_plot(self): self._show_plot(create_heat_flux_figure, "Heat Flux View")
    def show_material_library(self): LibraryDialog("Material Library", [f"{m.name} | {m.category} | k={m.thermal_conductivity}" for m in self.project.materials], self).exec()
    def show_fluid_library(self): LibraryDialog("Fluid Library", [f"{f.name} | k={f.thermal_conductivity} | Pr={f.prandtl_number}" for f in self.project.fluids], self).exec()
    def about(self): QMessageBox.about(self, "About", "ThermalSim Designer MVP\n2D termal direnç tabanlı mühendislik uygulaması.")

    def closeEvent(self, event):
        if self.maybe_save(): event.accept()
        else: event.ignore()
