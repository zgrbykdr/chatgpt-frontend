from dataclasses import dataclass

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from fmu_reverse_engineering.domain.schemas.model_schema import ModelCandidateSchema, ModelScore

from .registry import model_registry


@dataclass
class ModelSearchEngine:
    enabled_models: list[str]

    def run(self, x: pd.DataFrame, y: pd.Series, target: str) -> list[ModelCandidateSchema]:
        candidates: list[ModelCandidateSchema] = []
        for name in self.enabled_models:
            model = model_registry.create(name)
            model.fit(x, y)
            pred = model.predict(x)
            score = ModelScore(
                rmse=float(mean_squared_error(y, pred) ** 0.5),
                mae=float(mean_absolute_error(y, pred)),
                r2=float(r2_score(y, pred)),
                complexity=model.complexity(),
            )
            candidates.append(
                ModelCandidateSchema(name=name, family=model.family, target=target, score=score)
            )
        return candidates
