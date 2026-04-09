from pydantic import BaseModel, Field


class ModelScore(BaseModel):
    rmse: float
    mae: float
    r2: float
    complexity: float = 0.0


class ModelCandidateSchema(BaseModel):
    name: str
    family: str
    target: str
    score: ModelScore
    metadata: dict = Field(default_factory=dict)
