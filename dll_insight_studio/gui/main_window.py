from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dll_insight_studio.models.entities import ProjectConfig
from dll_insight_studio.services.application_context import ApplicationContext


SCREENS = [
    "Welcome / Home",
    "Project Setup",
    "File Identification",
    "Metadata Explorer",
    "String Intelligence Review",
    "Function Analysis",
    "Variable Mapping",
    "Model Pattern Detection",
    "Guided Decisions",
    "Runtime Validation Wizard",
    "Report Preview / Export",
    "Settings",
    "Logs / Diagnostics",
    "About / Help",
]


class AnalysisWorker(QObject):
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, ctx: ApplicationContext, dll_path: Path, manual_labels: dict[str, str], fn_overrides: dict[str, str]):
        super().__init__()
        self.ctx = ctx
        self.dll_path = dll_path
        self.manual_labels = manual_labels
        self.fn_overrides = fn_overrides

    def run(self) -> None:
        try:
            result = self.ctx.pipeline.run(self.dll_path, self.manual_labels, self.fn_overrides)
            self.finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


@dataclass
class SessionState:
    project_id: int | None = None
    project_dir: Path | None = None
    dll_path: Path | None = None
    exe_path: Path | None = None
    db: Any | None = None
    repo: Any | None = None
    analysis: dict[str, Any] | None = None
    manual_labels: dict[str, str] = None
    function_overrides: dict[str, str] = None

    def __post_init__(self) -> None:
        self.manual_labels = self.manual_labels or {}
        self.function_overrides = self.function_overrides or {}


class MainWindow(QMainWindow):
    def __init__(self, context: ApplicationContext):
        super().__init__()
        self.ctx = context
        self.state = SessionState()
        self.setWindowTitle("DLL Insight Studio")
        self.resize(1440, 860)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(root)

        self.nav = QListWidget()
        self.nav.addItems(SCREENS)
        self.nav.setMaximumWidth(250)
        self.nav.currentRowChanged.connect(self._on_screen_change)
        root.addWidget(self.nav)

        center_wrap = QWidget()
        center_layout = QVBoxLayout(center_wrap)
        self.stack = QStackedWidget()
        center_layout.addWidget(self.stack)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        center_layout.addWidget(self.progress)
        root.addWidget(center_wrap)

        self.help_panel = QTextEdit()
        self.help_panel.setReadOnly(True)
        self.help_panel.setMaximumWidth(340)
        root.addWidget(self.help_panel)
        root.setSizes([200, 900, 280])

        self.statusBar().showMessage("Ready")

        self._init_screens()
        self.nav.setCurrentRow(0)

    def _init_screens(self) -> None:
        self.welcome = QWidget()
        l = QVBoxLayout(self.welcome)
        l.addWidget(QLabel("<h1>DLL Insight Studio</h1><p>Guided DLL model understanding for beginner, intermediate, and expert analysts.</p>"))
        self.recent_label = QLabel("Recent projects are shown after you create/open a project.")
        l.addWidget(self.recent_label)
        btn_new = QPushButton("New Project")
        btn_new.clicked.connect(lambda: self.nav.setCurrentRow(1))
        btn_open = QPushButton("Open Existing Project DB")
        btn_open.clicked.connect(self._open_existing_project)
        l.addWidget(btn_new)
        l.addWidget(btn_open)
        l.addStretch(1)
        self.stack.addWidget(self.welcome)

        self.setup = QWidget()
        fl = QFormLayout(self.setup)
        self.project_name = QLineEdit("dll_project")
        self.dll_input = QLineEdit()
        self.exe_input = QLineEdit()
        self.related_input = QLineEdit()
        self.mode_combo = QComboBox(); self.mode_combo.addItems(["Automatic", "Guided", "Expert"])
        self.depth_combo = QComboBox(); self.depth_combo.addItems(["Quick", "Standard", "Deep"])
        for field, handler in [(self.dll_input, self._pick_dll), (self.exe_input, self._pick_exe), (self.related_input, self._pick_related)]:
            row = QHBoxLayout(); row.addWidget(field); b = QPushButton("Browse"); b.clicked.connect(handler); row.addWidget(b)
            c = QWidget(); c.setLayout(row)
            fl.addRow(field.placeholderText() or "", c)
        self.dll_input.setPlaceholderText("Select DLL file")
        self.exe_input.setPlaceholderText("Optional EXE")
        self.related_input.setPlaceholderText("Optional related folder")
        fl.addRow("Project Name", self.project_name)
        fl.addRow("DLL", self._wrap_browse(self.dll_input, self._pick_dll))
        fl.addRow("Host EXE (optional)", self._wrap_browse(self.exe_input, self._pick_exe))
        fl.addRow("Related Files Folder (optional)", self._wrap_browse(self.related_input, self._pick_related))
        fl.addRow("Workflow Mode", self.mode_combo)
        fl.addRow("Analysis Depth", self.depth_combo)
        run_btn = QPushButton("Create Project and Run Analysis")
        run_btn.clicked.connect(self._create_and_analyze)
        fl.addRow(run_btn)
        self.stack.addWidget(self.setup)

        self.identity_view = QPlainTextEdit(); self.identity_view.setReadOnly(True); self.stack.addWidget(self.identity_view)
        self.metadata_table = QTableWidget(0, 3); self.metadata_table.setHorizontalHeaderLabels(["Section", "Name", "Details"]); self.stack.addWidget(self.metadata_table)
        self.strings_table = QTableWidget(0, 3); self.strings_table.setHorizontalHeaderLabels(["String", "Category", "Confidence"]); self.stack.addWidget(self.strings_table)
        self.functions_table = QTableWidget(0, 5); self.functions_table.setHorizontalHeaderLabels(["Function", "Role", "Secondary", "Confidence", "Explanation"]); self.stack.addWidget(self.functions_table)
        self.variables_table = QTableWidget(0, 4); self.variables_table.setHorizontalHeaderLabels(["Variable", "Category", "Region", "Confidence"]); self.stack.addWidget(self.variables_table)
        self.pattern_table = QTableWidget(0, 3); self.pattern_table.setHorizontalHeaderLabels(["Pattern", "Confidence", "Evidence"]); self.stack.addWidget(self.pattern_table)

        self.guided = QWidget(); gl = QVBoxLayout(self.guided)
        self.guided_text = QTextEdit(); self.guided_text.setReadOnly(True)
        self.guidance_scope = QComboBox(); self.guidance_scope.addItems(["String Label Decision", "Function Role Decision"])
        self.guidance_scope.currentTextChanged.connect(self._refresh_guided_targets)
        self.guidance_target = QComboBox()
        self.guidance_choice = QComboBox(); self.guidance_choice.addItems(["Input", "Output", "Parameter", "State", "Config", "Ignore", "I am not sure", "Unsure"])
        save_decision = QPushButton("Record Decision")
        save_decision.clicked.connect(self._record_guided_decision)
        rerun_btn = QPushButton("Re-run Analysis with Decisions")
        rerun_btn.clicked.connect(self._rerun_after_guidance)
        gl.addWidget(QLabel("Guided Decision Wizard"))
        gl.addWidget(QLabel("1) Choose decision type  2) Choose target item  3) Choose label/role  4) Click Record Decision"))
        gl.addWidget(self.guided_text)
        gl.addWidget(self.guidance_scope)
        gl.addWidget(self.guidance_target)
        gl.addWidget(self.guidance_choice)
        gl.addWidget(save_decision)
        gl.addWidget(rerun_btn)
        self.stack.addWidget(self.guided)

        self.runtime = QWidget(); rl = QVBoxLayout(self.runtime)
        self.runtime_text = QTextEdit(); self.runtime_text.setReadOnly(False)
        capture_btn = QPushButton("Save Runtime Observation")
        capture_btn.clicked.connect(self._save_runtime_observation)
        rl.addWidget(QLabel("Runtime Validation Assistant")); rl.addWidget(self.runtime_text); rl.addWidget(capture_btn)
        self.stack.addWidget(self.runtime)

        self.report = QWidget(); rpl = QVBoxLayout(self.report)
        self.report_preview = QTextEdit(); self.report_preview.setReadOnly(True)
        e1 = QPushButton("Export HTML"); e1.clicked.connect(lambda: self._export_report("html"))
        e2 = QPushButton("Export PDF"); e2.clicked.connect(lambda: self._export_report("pdf"))
        e3 = QPushButton("Export JSON"); e3.clicked.connect(lambda: self._export_report("json"))
        e4 = QPushButton("Export Dymola Lookup CSV"); e4.clicked.connect(self._export_dymola_lookup)
        rpl.addWidget(self.report_preview); rpl.addWidget(e1); rpl.addWidget(e2); rpl.addWidget(e3); rpl.addWidget(e4)
        self.stack.addWidget(self.report)

        self.settings = QTextEdit("Workspace, analysis, and report settings are stored per project and can be changed before rerun.")
        self.stack.addWidget(self.settings)
        self.logs = QPlainTextEdit(); self.logs.setReadOnly(True); self.stack.addWidget(self.logs)
        self.about = QTextEdit("DLL Insight Studio supports automatic, guided, and expert workflows with transparent confidence and evidence.")
        self.about.setReadOnly(True)
        self.stack.addWidget(self.about)

    def _wrap_browse(self, field: QLineEdit, handler: Any) -> QWidget:
        row = QHBoxLayout()
        row.addWidget(field)
        btn = QPushButton("Browse")
        btn.clicked.connect(handler)
        row.addWidget(btn)
        widget = QWidget(); widget.setLayout(row)
        return widget

    def _on_screen_change(self, idx: int) -> None:
        self.stack.setCurrentIndex(idx)
        hints = {
            0: "Start a new project or reopen an existing SQLite-backed project.",
            1: "Select DLL, optional EXE/folder, then choose mode and depth.",
            2: "Review architecture, native/.NET identity, and protection suspicion.",
            3: "Browse exports/imports/resources/strings/numeric clues in one place.",
            4: "Relabel string categories if needed to improve downstream confidence.",
            5: "Inspect ranked function roles with evidence explanations.",
            6: "Review inferred inputs/outputs/states/parameters and synthetic mappings.",
            7: "Inspect ranked model pattern candidates and uncertainty notes.",
            8: "Follow plain-English guided decision points with safe fallback options.",
            9: "Record runtime observations or stay static-only when EXE is unavailable.",
            10: "Preview and export executive/technical reports in HTML/PDF/JSON.",
            11: "Tune workspace, analysis, and output behavior.",
            12: "Review app/analysis logs and copy diagnostics for troubleshooting.",
            13: "Application help and product overview.",
        }
        self.help_panel.setPlainText(hints.get(idx, ""))

    def _pick_dll(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select DLL", "", "DLL Files (*.dll);;All Files (*)")
        if path:
            self.dll_input.setText(path)

    def _pick_exe(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select EXE", "", "Executable (*.exe);;All Files (*)")
        if path:
            self.exe_input.setText(path)

    def _pick_related(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Related Files Folder")
        if path:
            self.related_input.setText(path)

    def _create_and_analyze(self) -> None:
        dll = Path(self.dll_input.text().strip()) if self.dll_input.text().strip() else None
        if not dll or not dll.exists() or dll.suffix.lower() != ".dll":
            QMessageBox.warning(self, "Validation", "Please select a valid DLL file.")
            return
        try:
            config = ProjectConfig(
                name=self.project_name.text().strip() or "dll_project",
                dll_path=dll,
                exe_path=Path(self.exe_input.text().strip()) if self.exe_input.text().strip() else None,
                related_dir=Path(self.related_input.text().strip()) if self.related_input.text().strip() else None,
                mode=self.mode_combo.currentText(),
                depth=self.depth_combo.currentText(),
            )
            project_id, db, repo, project_dir = self.ctx.project_manager.create_project(config)
            self.state.project_id = project_id
            self.state.db = db
            self.state.repo = repo
            self.state.project_dir = project_dir
            self.state.dll_path = project_dir / dll.name
            self.state.exe_path = Path(self.exe_input.text().strip()) if self.exe_input.text().strip() else None
            self.statusBar().showMessage("Project created. Running analysis in background...")
            self.progress.setRange(0, 0)
            self._run_worker()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Project Creation Failed", str(exc))

    def _run_worker(self) -> None:
        self.thread = QThread(self)
        self.worker = AnalysisWorker(self.ctx, self.state.dll_path, self.state.manual_labels, self.state.function_overrides)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._analysis_done)
        self.worker.failed.connect(self._analysis_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.start()

    def _analysis_done(self, result: dict[str, Any]) -> None:
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.state.analysis = result
        self._persist_results()
        self._populate_views()
        self.statusBar().showMessage("Analysis complete")
        self.nav.setCurrentRow(2)

    def _analysis_failed(self, message: str) -> None:
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.statusBar().showMessage("Analysis failed")
        QMessageBox.critical(self, "Analysis Error", f"Analysis failed: {message}")

    def _persist_results(self) -> None:
        a = self.state.analysis
        self.state.repo.save_metadata(self.state.project_id, a["metadata"]["exports"], a["metadata"]["imports"])
        self.state.repo.save_strings(self.state.project_id, a["strings"])
        self.state.repo.save_functions(self.state.project_id, a["functions"])
        self.state.repo.save_variables(self.state.project_id, a["variables"])
        self.state.repo.save_patterns(self.state.project_id, a["patterns"])

    def _populate_views(self) -> None:
        a = self.state.analysis
        self.identity_view.setPlainText(json.dumps(a["identity"], indent=2))

        self._fill_table(self.metadata_table, [("Export", e["name"], str(e.get("ordinal", ""))) for e in a["metadata"]["exports"]] +
                         [("Import", i["name"], i["library"]) for i in a["metadata"]["imports"][:200]] +
                         [("Resource", r, "") for r in a["metadata"]["resources"][:100]])

        self._fill_table(self.strings_table, [(s["value"], s["category"], str(s["confidence"])) for s in a["strings"][:1000]])
        self._fill_table(self.functions_table, [(f["name"], f["role"]["primary"], f["role"]["secondary"], str(f["role"]["confidence"]), f["role"]["explanation"]) for f in a["functions"][:500]])
        self._fill_table(self.variables_table, [(v["name"], v["category"], v.get("region", ""), str(v.get("confidence", 0))) for v in a["variables"][:800]])
        self._fill_table(self.pattern_table, [(p["pattern"], str(p["confidence"]), p["evidence"]) for p in a["patterns"]])

        guide = self.ctx.guidance.decision_text("important_terms")
        self.guided_text.setPlainText(f"Why we ask: {guide['why']}\n\nWhat to look for: {guide['look_for']}\n\nSafe option: {guide['safe']}")
        readiness = self.ctx.runtime.readiness_message(self.state.exe_path)
        self.runtime_text.setPlainText(readiness + "\n\nRecord observations here for baseline and changed runs.")
        self.report_preview.setPlainText(self._executive_preview())
        self._resolve_dependencies_with_user()
        self._refresh_guided_targets()

        logs = self.state.repo.load_dashboard_data(self.state.project_id)
        self.logs.setPlainText(json.dumps(logs.get("analysis_logs", []) + logs.get("app_logs", []), indent=2))

    def _fill_table(self, table: QTableWidget, rows: list[tuple[str, ...]]) -> None:
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                table.setItem(r, c, QTableWidgetItem(value))
        table.resizeColumnsToContents()

    def _record_guided_decision(self) -> None:
        if not self.state.project_id:
            return
        choice = self.guidance_choice.currentText()
        scope = self.guidance_scope.currentText()
        target = self.guidance_target.currentText()
        if target.endswith("No uncertain target found"):
            QMessageBox.information(self, "Guided Decision", "There are currently no uncertain targets to label.")
            return
        prompt = f"{scope}: {target}"
        if target.startswith("STR::"):
            value = target.replace("STR::", "", 1)
            map_choice = {
                "Input": "Possible Inputs",
                "Output": "Possible Outputs",
                "Parameter": "Possible Parameters",
                "State": "Possible States",
                "Config": "Possible Config Terms",
                "Ignore": "Unknown but important",
                "Unsure": "Unknown but important",
                "I am not sure": "Unknown but important",
            }
            self.state.manual_labels[value] = map_choice.get(choice, "Unknown but important")
        elif target.startswith("FN::"):
            fn = target.replace("FN::", "", 1)
            map_role = {
                "Input": "Input",
                "Output": "Output",
                "Parameter": "Parameter",
                "State": "State Update",
                "Config": "Config",
                "Ignore": "Control/Coordinator",
                "Unsure": "Compute",
                "I am not sure": "Compute",
            }
            self.state.function_overrides[fn] = map_role.get(choice, "Compute")
        self.state.repo.add_guidance_decision(self.state.project_id, "guided_decision", prompt, choice, "Recorded from guided screen")
        QMessageBox.information(self, "Saved", "Decision saved. Click 'Re-run Analysis with Decisions' to apply immediately.")

    def _rerun_after_guidance(self) -> None:
        if not self.state.dll_path:
            return
        self.statusBar().showMessage("Re-running analysis with guided decisions...")
        self.progress.setRange(0, 0)
        self._run_worker()

    def _refresh_guided_targets(self) -> None:
        if not self.state.analysis:
            return
        self.guidance_target.clear()
        scope = self.guidance_scope.currentText()
        if scope == "String Label Decision":
            low_conf_strings = [s for s in self.state.analysis.get("strings", []) if s.get("confidence", 0) < 0.65][:80]
            for s in low_conf_strings:
                self.guidance_target.addItem(f"STR::{s['value']}")
        else:
            top_functions = self.state.analysis.get("functions", [])[:80]
            for fn in top_functions:
                self.guidance_target.addItem(f"FN::{fn['name']}")
        if self.guidance_target.count() == 0:
            self.guidance_target.addItem("STR::No uncertain target found")

    def _save_runtime_observation(self) -> None:
        if not self.state.project_id:
            return
        text = self.runtime_text.toPlainText().strip()
        self.state.repo.add_runtime_session(self.state.project_id, str(self.state.exe_path or ""), "run_note", text, "manual-observation")
        QMessageBox.information(self, "Saved", "Runtime observation recorded.")

    def _export_report(self, fmt: str) -> None:
        if not self.state.analysis or not self.state.project_dir:
            return
        payload = {
            "project_name": self.project_name.text().strip() or "dll_project",
            "identity": self.state.analysis["identity"],
            "metadata": self.state.analysis["metadata"],
            "functions": self.state.analysis["functions"],
            "variables": self.state.analysis["variables"],
            "patterns": self.state.analysis["patterns"],
            "reverse_engineering": self.state.analysis.get("reverse_engineering", {}),
            "recommendations": "Review unresolved uncertainties, confirm important terms, and run controlled runtime comparison when possible.",
        }
        out = self.state.project_dir / f"report.{fmt}"
        if fmt == "html":
            self.ctx.reports.export_html(payload, out)
            report_type = "HTML"
        elif fmt == "pdf":
            self.ctx.reports.export_pdf(payload, out)
            report_type = "PDF"
        else:
            self.ctx.reports.export_json(payload, out)
            report_type = "JSON"
        self.state.repo.add_report_history(self.state.project_id, report_type, str(out))
        QMessageBox.information(self, "Export Complete", f"Report exported to {out}")

    def _executive_preview(self) -> str:
        if not self.state.analysis:
            return "No analysis yet."
        top_functions = "\n".join(f"- {f['name']} ({f['role']['primary']}, {f['role']['confidence']})" for f in self.state.analysis["functions"][:5])
        top_patterns = "\n".join(f"- {p['pattern']} ({p['confidence']})" for p in self.state.analysis["patterns"][:5])
        return (
            f"Executive Summary\n\n"
            f"File type: {self.state.analysis['identity']['dll_type']}\n"
            f"Architecture: {self.state.analysis['identity']['architecture']}\n"
            f"Protection suspicion: {', '.join(self.state.analysis['identity']['protection_signals']) or 'No strong signs'}\n\n"
            f"Likely core functions:\n{top_functions}\n\n"
            f"Likely model pattern:\n{top_patterns}\n\n"
            f"Recommended next steps:\n- Review guided decisions\n- Confirm uncertain I/O terms\n- Use runtime wizard if host EXE is available"
        )

    def _resolve_dependencies_with_user(self) -> None:
        reverse = (self.state.analysis or {}).get("reverse_engineering", {})
        deps = reverse.get("dependencies", [])
        if not deps:
            return
        related_dir = Path(self.related_input.text().strip()) if self.related_input.text().strip() else None
        found_map: dict[str, str] = {}
        for dep in deps[:30]:
            lib = dep["library"]
            if dep.get("is_system"):
                continue
            if related_dir and (related_dir / lib).exists():
                found_map[lib] = str((related_dir / lib).resolve())
                continue
            answer = QMessageBox.question(
                self,
                "Dependency Path Needed",
                f"Dependency '{lib}' was detected. Do you want to select its file location now?",
            )
            if answer == QMessageBox.StandardButton.Yes:
                selected, _ = QFileDialog.getOpenFileName(self, f"Locate {lib}", "", "DLL Files (*.dll);;All Files (*)")
                if selected:
                    found_map[lib] = selected
        reverse["resolved_dependency_paths"] = found_map
        if self.state.project_id and found_map:
            self.state.repo.add_guidance_decision(
                self.state.project_id,
                "dependency_resolution",
                "Resolve dependent DLL paths",
                json.dumps(found_map),
                "User provided dependency paths",
            )

    def _export_dymola_lookup(self) -> None:
        if not self.state.analysis or not self.state.project_dir:
            return
        reverse = self.state.analysis.get("reverse_engineering", {})
        rows = reverse.get("dymola_lookup_rows", [])
        if not rows:
            QMessageBox.warning(self, "Export Dymola Lookup", "No lookup rows available yet. Run analysis first.")
            return
        output_path = self.state.project_dir / "dymola_lookup_table.csv"
        self.ctx.pipeline.reverse.export_dymola_lookup_csv(rows, output_path)
        if self.state.project_id:
            self.state.repo.add_report_history(self.state.project_id, "DYMOLA_LOOKUP_CSV", str(output_path))
        QMessageBox.information(self, "Export Complete", f"Dymola lookup table exported to {output_path}")

    def _open_existing_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open project database", "", "SQLite (*.db)")
        if not path:
            return
        try:
            db, repo = self.ctx.project_manager.open_project(Path(path))
            project = db.fetch_project(1)
            if not project:
                QMessageBox.warning(self, "Open Project", "No project row found in selected database.")
                return
            self.state.db = db
            self.state.repo = repo
            self.state.project_id = project["id"]
            self.state.project_dir = Path(project["workspace"])
            self.state.dll_path = Path(project["dll_path"])
            self.recent_label.setText(f"Loaded project: {project['name']} ({project['workspace']})")
            QMessageBox.information(self, "Project Loaded", "Project loaded. Re-run analysis from Project Setup if needed.")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Open Failed", str(exc))
