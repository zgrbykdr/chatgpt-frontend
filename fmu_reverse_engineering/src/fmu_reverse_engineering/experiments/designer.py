from dataclasses import dataclass

from fmu_reverse_engineering.domain.schemas.experiment_schema import ExperimentPlanSchema


@dataclass
class DefaultExperimentDesigner:
    strategy: str = "lhs"

    def build_plan(self) -> ExperimentPlanSchema:
        return ExperimentPlanSchema(strategy=self.strategy, points=[])
