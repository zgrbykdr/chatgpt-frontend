from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from .project_manager import GUIDANCE_TEXT, ProjectManager


SCREEN_NAMES = [
    "Welcome / Home",
    "Project Import",
    "Package Overview",
    "XML Domain Explorer",
    "DLL Analyzer",
    "Interface Discovery",
    "Variable Catalog",
    "Guided Review",
    "Runtime Probing",
    "Sensitivity Analysis",
    "Lookup Builder",
    "Report Preview / Export",
    "Logs / Diagnostics",
    "Settings",
    "About / Help",
]


class ImportWorker(QThread):
    done = Signal(dict)
    error = Signal(str)

    def __init__(self, manager: ProjectManager, name: str, source: Path):
        super().__init__()
        self.manager = manager
        self.name = name
        self.source = source

    def run(self):
        try:
            result = self.manager.create_project(self.name, self.source)
            self.done.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class StudioWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CasCalc I/O Reverse Engineering Studio")
        self.resize(1600, 900)
        self.manager = ProjectManager(Path.cwd() / "workspace")
        self.current_project_id: int | None = None
        self.import_source: Path | None = None
        self.page_outputs: dict[str, QPlainTextEdit] = {}

        root = QWidget()
        root_layout = QVBoxLayout(root)
        self.splitter = QSplitter()
        root_layout.addWidget(self.splitter)

        self.sidebar = QListWidget()
        for name in SCREEN_NAMES:
            self.sidebar.addItem(QListWidgetItem(name))
        self.sidebar.currentRowChanged.connect(self._switch_screen)

        self.stack = QStackedWidget()
        self.pages = [self._build_page(name) for name in SCREEN_NAMES]
        for p in self.pages:
            self.stack.addWidget(p)

        self.help_panel = QPlainTextEdit()
        self.help_panel.setReadOnly(True)
        self.help_panel.setPlainText("\n".join(f"• {line}" for line in GUIDANCE_TEXT))

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.stack)
        self.splitter.addWidget(self.help_panel)
        self.splitter.setSizes([220, 980, 380])

        self.setCentralWidget(root)
        self.status = QStatusBar()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status.addPermanentWidget(self.progress)
        self.setStatusBar(self.status)
        self.sidebar.setCurrentRow(0)

    def _build_page(self, name: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel(f"<h2>{name}</h2>"))
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText(f"{name} is connected and ready.")
        layout.addWidget(text)
        self.page_outputs[name] = text

        if name == "Project Import":
            self.project_name = QLineEdit("CasCalc Analysis Project")
            self.project_source = QLineEdit()
            browse = QPushButton("Select CasCalc.zip or folder")
            browse.clicked.connect(self._choose_source)
            run_btn = QPushButton("Import Package")
            run_btn.clicked.connect(self._run_import)
            layout.addWidget(QLabel("Project Name"))
            layout.addWidget(self.project_name)
            layout.addWidget(self.project_source)
            layout.addWidget(browse)
            layout.addWidget(run_btn)
            self.import_log = text
        elif name == "Welcome / Home":
            btn = QPushButton("🚀 One-Click Semi-Auto Run")
            btn.clicked.connect(self._one_click_semi_auto)
            layout.addWidget(btn)
        elif name == "Package Overview":
            btn = QPushButton("Refresh Summary")
            btn.clicked.connect(self._refresh_overview)
            layout.addWidget(btn)
            self.overview_text = text
        elif name == "XML Domain Explorer":
            btn = QPushButton("Run XML Mining")
            btn.clicked.connect(self._refresh_xml_domain)
            layout.addWidget(btn)
        elif name == "DLL Analyzer":
            btn = QPushButton("Analyze DLL Roles")
            btn.clicked.connect(self._refresh_dll_findings)
            layout.addWidget(btn)
        elif name == "Interface Discovery":
            btn = QPushButton("Refresh Interface Candidates")
            btn.clicked.connect(self._refresh_interface_candidates)
            layout.addWidget(btn)
        elif name == "Variable Catalog":
            btn = QPushButton("Refresh Variable Catalog")
            btn.clicked.connect(self._refresh_variable_catalog)
            layout.addWidget(btn)
        elif name == "Guided Review":
            btn1 = QPushButton("Start Base Scenario Guidance")
            btn1.clicked.connect(self._guided_base_scenario)
            btn2 = QPushButton("Show Runtime Readiness Guidance")
            btn2.clicked.connect(self._guided_runtime_readiness)
            layout.addWidget(btn1)
            layout.addWidget(btn2)
        elif name == "Runtime Probing":
            probe = QPushButton("Run Direct Probe (safe)")
            probe.clicked.connect(self._run_probe)
            layout.addWidget(probe)
            self.runtime_text = text
        elif name == "Sensitivity Analysis":
            btn = QPushButton("Run Sensitivity (from runtime observations)")
            btn.clicked.connect(self._run_sensitivity)
            layout.addWidget(btn)
        elif name == "Lookup Builder":
            btn = QPushButton("Generate R290 2-Phase 1D Lookup Suite")
            btn.clicked.connect(self._run_lookup_build)
            layout.addWidget(btn)
        elif name == "Report Preview / Export":
            report = QPushButton("Generate Reports")
            report.clicked.connect(self._run_report)
            layout.addWidget(report)
            self.report_text = text
        elif name == "Logs / Diagnostics":
            btn = QPushButton("Show Recent Logs")
            btn.clicked.connect(self._show_logs)
            layout.addWidget(btn)
        elif name == "Settings":
            btn = QPushButton("Show Workspace Settings")
            btn.clicked.connect(self._show_settings)
            layout.addWidget(btn)
        elif name == "About / Help":
            btn = QPushButton("Show Product Scope")
            btn.clicked.connect(self._show_about)
            layout.addWidget(btn)
        return page

    def _switch_screen(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def _choose_source(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CasCalc.zip", str(Path.cwd()), "Zip (*.zip);;All files (*)")
        if not path:
            folder = QFileDialog.getExistingDirectory(self, "Select extracted CasCalc folder", str(Path.cwd()))
            if folder:
                path = folder
        if path:
            self.import_source = Path(path)
            self.project_source.setText(path)

    def _run_import(self):
        if not self.import_source:
            QMessageBox.warning(self, "Missing source", "Select CasCalc.zip or extracted folder first.")
            return
        self.progress.setValue(20)
        self.worker = ImportWorker(self.manager, self.project_name.text().strip(), self.import_source)
        self.worker.done.connect(self._import_done)
        self.worker.error.connect(self._import_error)
        self.worker.start()
        self.status.showMessage("Import running in background...")

    def _import_done(self, result: dict):
        self.current_project_id = result["project_id"]
        self.import_log.setPlainText(json.dumps(result, indent=2))
        self.progress.setValue(100)
        self.status.showMessage("Import complete")

    def _import_error(self, msg: str):
        QMessageBox.critical(self, "Import failed", msg)
        self.progress.setValue(0)

    def _refresh_overview(self):
        if not self.current_project_id:
            self.overview_text.setPlainText("No imported project yet.")
            return
        summary = self.manager.quick_summary(self.current_project_id)
        self.overview_text.setPlainText(json.dumps(summary, indent=2))

    def _run_probe(self):
        if not self.current_project_id:
            self.runtime_text.setPlainText("Import project first.")
            return
        root = Path(self.manager.db.execute("SELECT root_path FROM projects WHERE id=?", (self.current_project_id,)).fetchone()[0])
        result = self.manager.runtime.direct_probe(root, {"InTempSide1": 20.0, "InTempSide2": 40.0})
        session = self.manager.db.execute(
            "INSERT INTO runtime_sessions(project_id, mode, base_case_json) VALUES(?,?,?)",
            (self.current_project_id, "direct_api", json.dumps({"InTempSide1": 20.0, "InTempSide2": 40.0})),
        ).lastrowid
        self.manager.db.execute(
            "INSERT INTO runtime_observations(session_id, inputs_json, outputs_json, status, error_text) VALUES(?,?,?,?,?)",
            (
                session,
                json.dumps({"InTempSide1": 20.0, "InTempSide2": 40.0}),
                json.dumps(result.get("outputs", {})),
                result.get("status", "unknown"),
                result.get("error", ""),
            ),
        )
        self.runtime_text.setPlainText(json.dumps(result, indent=2))

    def _run_report(self):
        if not self.current_project_id:
            self.report_text.setPlainText("Import project first.")
            return
        c = self.manager.db.conn.cursor()
        dll_roles = c.execute("SELECT dll_name, probable_role, confidence FROM dll_findings WHERE project_id=?", (self.current_project_id,)).fetchall()
        inputs = [r[0] for r in c.execute("SELECT canonical_name FROM variable_mappings WHERE project_id=? AND category LIKE '%input%' LIMIT 200", (self.current_project_id,)).fetchall()]
        outputs = [r[0] for r in c.execute("SELECT canonical_name FROM variable_mappings WHERE project_id=? AND category LIKE '%output%' LIMIT 200", (self.current_project_id,)).fetchall()]
        interfaces = c.execute("SELECT dll_name, function_name, probable_purpose FROM interface_candidates WHERE project_id=?", (self.current_project_id,)).fetchall()
        paths = self.manager.reports.build_reports(
            project_name=f"project_{self.current_project_id}",
            findings={"dll_roles": dll_roles, "inputs": inputs, "outputs": outputs, "interfaces": interfaces, "sensitivity": []},
            out_dir=self.manager.workspace / "reports",
        )
        self.report_text.setPlainText("\n".join([f"{k}: {v}" for k, v in paths.items()]))

    def _active_text(self, screen_name: str) -> QPlainTextEdit:
        return self.page_outputs[screen_name]

    def _refresh_xml_domain(self):
        if not self.current_project_id:
            self._active_text("XML Domain Explorer").setPlainText("Import project first.")
            return
        rows = self.manager.db.execute(
            "SELECT name, source_file, category, dtype, confidence FROM xml_variables WHERE project_id=? ORDER BY confidence DESC, name LIMIT 300",
            (self.current_project_id,),
        ).fetchall()
        self._active_text("XML Domain Explorer").setPlainText(
            "\n".join([f"{r[0]} | {r[2]} | {r[3]} | conf={r[4]:.2f} | {r[1]}" for r in rows]) or "No XML variables found."
        )

    def _refresh_dll_findings(self):
        if not self.current_project_id:
            self._active_text("DLL Analyzer").setPlainText("Import project first.")
            return
        rows = self.manager.db.execute(
            "SELECT dll_name, architecture, string_clue_count, probable_role, confidence, why FROM dll_findings WHERE project_id=? ORDER BY confidence DESC",
            (self.current_project_id,),
        ).fetchall()
        self._active_text("DLL Analyzer").setPlainText(
            "\n".join([f"{r[0]} | arch={r[1]} | clues={r[2]} | role={r[3]} | conf={r[4]:.2f} | {r[5]}" for r in rows]) or "No DLL findings."
        )

    def _refresh_interface_candidates(self):
        if not self.current_project_id:
            self._active_text("Interface Discovery").setPlainText("Import project first.")
            return
        rows = self.manager.db.execute(
            "SELECT dll_name, function_name, probable_purpose, call_order_guess, confidence FROM interface_candidates WHERE project_id=? ORDER BY call_order_guess, confidence DESC",
            (self.current_project_id,),
        ).fetchall()
        self._active_text("Interface Discovery").setPlainText(
            "\n".join([f"{r[0]}::{r[1]} | {r[2]} | step={r[3]} | conf={r[4]:.2f}" for r in rows]) or "No interface candidates found."
        )

    def _refresh_variable_catalog(self):
        if not self.current_project_id:
            self._active_text("Variable Catalog").setPlainText("Import project first.")
            return
        rows = self.manager.db.execute(
            "SELECT canonical_name, category, data_type, confidence, sweepable FROM variable_mappings WHERE project_id=? ORDER BY confidence DESC, canonical_name LIMIT 500",
            (self.current_project_id,),
        ).fetchall()
        self._active_text("Variable Catalog").setPlainText(
            "\n".join([f"{r[0]} | {r[1]} | {r[2]} | conf={r[3]:.2f} | sweepable={bool(r[4])}" for r in rows]) or "No variable mappings found."
        )

    def _guided_base_scenario(self):
        self._active_text("Guided Review").setPlainText(
            "Base Scenario Guide:\n"
            "1) Start with one-phase mode.\n"
            "2) Select common fluid (e.g., Water) from General/FLUID.\n"
            "3) Keep design geometry fixed for initial runs.\n"
            "4) Change one input at a time.\n"
            "5) Keep failed combinations as invalid samples."
        )

    def _guided_runtime_readiness(self):
        self._active_text("Guided Review").setPlainText(
            "Runtime Readiness:\n"
            "- Direct API probing: use when AlfaCalcInterface clues are present.\n"
            "- Host-assisted probing: use if function signatures are uncertain.\n"
            "- Static-only mode: continue with XML + DLL evidence when runtime is blocked."
        )

    def _run_sensitivity(self):
        if not self.current_project_id:
            self._active_text("Sensitivity Analysis").setPlainText("Import project first.")
            return
        rows = self.manager.db.execute(
            "SELECT inputs_json, outputs_json FROM runtime_observations ro JOIN runtime_sessions rs ON ro.session_id=rs.id WHERE rs.project_id=?",
            (self.current_project_id,),
        ).fetchall()
        runs: list[dict] = []
        for inp, out in rows:
            obj = {}
            obj.update(json.loads(inp or "{}"))
            obj.update({k: v for k, v in json.loads(out or "{}").items() if isinstance(v, (int, float))})
            runs.append(obj)
        if len(runs) < 2:
            self._active_text("Sensitivity Analysis").setPlainText(
                "Need at least two runtime observations with numeric outputs.\nRun Runtime Probing multiple times with different inputs."
            )
            return
        matrix = self.manager.sensitivity.influence_matrix(runs, ["InTempSide1", "InTempSide2"], ["echo_input_count"])
        lines = []
        for _, row in matrix.iterrows():
            self.manager.db.execute(
                "INSERT INTO sensitivity_results(project_id, input_var, output_var, influence, evidence_source, notes) VALUES(?,?,?,?,?,?)",
                (self.current_project_id, row["input_var"], row["output_var"], float(row["influence"]), row["evidence_source"], row["notes"]),
            )
            lines.append(f"{row['input_var']} -> {row['output_var']}: {row['influence']:.3f}")
        self._active_text("Sensitivity Analysis").setPlainText("\n".join(lines))

    def _run_lookup_build(self):
        if not self.current_project_id:
            self._active_text("Lookup Builder").setPlainText("Import project first.")
            return
        self.status.showMessage("Generating R290 two-phase 1D high-density lookup suite...")
        result = self.manager.build_r290_two_phase_1d_lookup(self.current_project_id)
        self._active_text("Lookup Builder").setPlainText(json.dumps(result, indent=2))
        self.status.showMessage("R290 two-phase lookup suite completed.")

    def _show_logs(self):
        if not self.current_project_id:
            self._active_text("Logs / Diagnostics").setPlainText("Import project first.")
            return
        rows = self.manager.db.execute("SELECT level, message, created_at FROM logs WHERE project_id=? ORDER BY id DESC LIMIT 100", (self.current_project_id,)).fetchall()
        self._active_text("Logs / Diagnostics").setPlainText(
            "\n".join([f"[{r[2]}] {r[0]}: {r[1]}" for r in rows]) or "No log records yet."
        )

    def _show_settings(self):
        self._active_text("Settings").setPlainText(
            f"Workspace: {self.manager.workspace}\n"
            f"Database: {self.manager.db.db_path}\n"
            "Mode support:\n- Automatic-first\n- Guided semi-automatic\n- Expert (manual review via catalog screens)"
        )

    def _show_about(self):
        self._active_text("About / Help").setPlainText(
            "CasCalc Reverse Mapper\n"
            "Package-specific reverse engineering assistant for CasCalc.zip.\n"
            "Use Project Import first, then review XML/DLL/Interface/Variable screens,\n"
            "run probing and sensitivity, generate lookup exports, then export reports."
        )

    def _one_click_semi_auto(self):
        if not self.current_project_id:
            self._active_text("Welcome / Home").setPlainText(
                "Önce Project Import ekranından CasCalc.zip/folder içe aktarın, sonra One-Click çalıştırın."
            )
            return
        self.progress.setValue(35)
        result = self.manager.run_one_click_semi_auto(self.current_project_id)
        self.progress.setValue(100)
        self.status.showMessage("One-click semi-auto workflow completed.")
        self._active_text("Welcome / Home").setPlainText(json.dumps(result, indent=2))


def main():
    app = QApplication(sys.argv)
    w = StudioWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
