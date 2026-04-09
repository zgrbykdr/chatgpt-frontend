from pydantic import BaseModel, Field


class ExperimentPoint(BaseModel):
    values: dict[str, float]


class ExperimentPlanSchema(BaseModel):
    strategy: str
    points: list[ExperimentPoint] = Field(default_factory=list)
