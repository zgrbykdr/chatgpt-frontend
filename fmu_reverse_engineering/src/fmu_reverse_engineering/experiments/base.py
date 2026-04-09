from abc import ABC, abstractmethod

from fmu_reverse_engineering.domain.schemas.experiment_schema import ExperimentPlanSchema


class ExperimentDesigner(ABC):
    @abstractmethod
    def build_plan(self) -> ExperimentPlanSchema:
        raise NotImplementedError
