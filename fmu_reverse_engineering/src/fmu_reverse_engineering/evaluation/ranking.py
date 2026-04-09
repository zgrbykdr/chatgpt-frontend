from dataclasses import dataclass

from fmu_reverse_engineering.domain.schemas.model_schema import ModelCandidateSchema


@dataclass
class WeightedRanker:
    rmse_weight: float = 0.7
    complexity_weight: float = 0.3

    def rank(self, candidates: list[ModelCandidateSchema]) -> list[ModelCandidateSchema]:
        def key(c: ModelCandidateSchema) -> float:
            return self.rmse_weight * c.score.rmse + self.complexity_weight * c.score.complexity

        return sorted(candidates, key=key)
