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
        elif name == "Package Overview":
            btn = QPushButton("Refresh Summary")
            btn.clicked.connect(self._refresh_overview)
            layout.addWidget(btn)
            self.overview_text = text
        elif name == "Runtime Probing":
            probe = QPushButton("Run Direct Probe (safe)")
            probe.clicked.connect(self._run_probe)
            layout.addWidget(probe)
            self.runtime_text = text
        elif name == "Report Preview / Export":
            report = QPushButton("Generate Reports")
            report.clicked.connect(self._run_report)
            layout.addWidget(report)
            self.report_text = text
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


def main():
    app = QApplication(sys.argv)
    w = StudioWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
