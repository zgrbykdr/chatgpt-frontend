from dataclasses import dataclass
from uuid import uuid4

import pandas as pd

from fmu_reverse_engineering.analysis.influence import InfluenceEngine
from fmu_reverse_engineering.core.config import AppConfig
from fmu_reverse_engineering.data.cleaner import DataCleaner
from fmu_reverse_engineering.data.feature_engineering import FeatureEngineeringEngine
from fmu_reverse_engineering.evaluation.ranking import WeightedRanker
from fmu_reverse_engineering.experiments.designer import DefaultExperimentDesigner
from fmu_reverse_engineering.fmu.inspector import FMUInspector
from fmu_reverse_engineering.models.orchestration import ModelSearchEngine
from fmu_reverse_engineering.models import simple_models  # noqa: F401
from fmu_reverse_engineering.reporting.summary_builder import SummaryBuilder
from fmu_reverse_engineering.runner.fmu_runner import FMURunner


@dataclass
class PipelineOrchestrator:
    config: AppConfig

    def run(self, fmu_path: str, output_dir: str) -> dict:
        run_id = str(uuid4())
        inspector = FMUInspector()
        metadata = inspector.inspect(fmu_path)
        manifest = inspector.export_manifest(metadata, output_dir)

        plan = DefaultExperimentDesigner().build_plan()
        raw_df = FMURunner().run(plan)
        clean_df = DataCleaner().clean(raw_df)
        feature_df = FeatureEngineeringEngine().transform(clean_df)

        influence = InfluenceEngine().compute_matrix(feature_df)

        model_results = []
        if isinstance(feature_df, pd.DataFrame) and not feature_df.empty and feature_df.shape[1] >= 2:
            target = feature_df.columns[-1]
            x = feature_df.drop(columns=[target])
            y = feature_df[target]
            candidates = ModelSearchEngine(enabled_models=["constant", "linear"]).run(x, y, target=target)
            ranked = WeightedRanker().rank(candidates)
            model_results = [m.model_dump() for m in ranked]

        summary = {
            "run_id": run_id,
            "mode": self.config.workflow.mode.value,
            "manifest": str(manifest),
            "influence_matrix_shape": list(influence.shape),
            "models": model_results,
        }

        SummaryBuilder().build(run_id=run_id, output_dir=output_dir, payload=summary)
        return summary
