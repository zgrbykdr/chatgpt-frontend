from abc import ABC, abstractmethod

from fmu_reverse_engineering.domain.schemas.model_schema import ModelCandidateSchema


class ModelRanker(ABC):
    @abstractmethod
    def rank(self, candidates: list[ModelCandidateSchema]) -> list[ModelCandidateSchema]:
        raise NotImplementedError
