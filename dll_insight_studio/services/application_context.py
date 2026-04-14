from __future__ import annotations

from pathlib import Path

from dll_insight_studio.reports.report_generator import ReportGenerator
from dll_insight_studio.runtime.runtime_assistant import RuntimeValidationAssistant
from dll_insight_studio.services.analysis_pipeline import AnalysisPipeline
from dll_insight_studio.services.guidance_engine import UserGuidanceEngine
from dll_insight_studio.services.project_manager import ProjectManager
from dll_insight_studio.utilities.logging_utils import configure_logging


class ApplicationContext:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.workspace_root = base_dir / "workspace_projects"
        self.project_manager = ProjectManager(self.workspace_root)
        self.pipeline = AnalysisPipeline()
        self.guidance = UserGuidanceEngine()
        self.reports = ReportGenerator()
        self.runtime = RuntimeValidationAssistant()
        self.logger = configure_logging(self.workspace_root / "app.log")
