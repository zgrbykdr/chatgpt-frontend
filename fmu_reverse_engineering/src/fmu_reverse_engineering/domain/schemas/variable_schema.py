from pydantic import BaseModel


class VariableSchema(BaseModel):
    name: str
    causality: str
    variability: str
    data_type: str
    unit: str | None = None
    min: float | None = None
    max: float | None = None
    nominal: float | None = None
    start: float | None = None
