from fmu_reverse_engineering.domain.schemas.model_schema import ModelCandidateSchema, ModelScore
from fmu_reverse_engineering.evaluation.ranking import WeightedRanker


def test_weighted_ranker_orders_by_weighted_score() -> None:
    a = ModelCandidateSchema(name='a', family='simple', target='y', score=ModelScore(rmse=1.0, mae=1.0, r2=0.9, complexity=10))
    b = ModelCandidateSchema(name='b', family='simple', target='y', score=ModelScore(rmse=1.1, mae=1.0, r2=0.8, complexity=1))
    ranked = WeightedRanker().rank([a, b])
    assert ranked[0].name == 'b'
