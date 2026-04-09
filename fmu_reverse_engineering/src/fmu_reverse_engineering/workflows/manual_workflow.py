from dataclasses import dataclass

from fmu_reverse_engineering.core.config import AppConfig

from .pipeline import PipelineOrchestrator


@dataclass
class ManualWorkflow:
    config: AppConfig

    def execute(self, fmu_path: str, output_dir: str) -> dict:
        return PipelineOrchestrator(self.config).run(fmu_path=fmu_path, output_dir=output_dir)
