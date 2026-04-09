from pydantic import BaseModel, Field

from .variable_schema import VariableSchema


class FMUSchema(BaseModel):
    fmu_path: str
    fmi_version: str
    fmu_type: str
    variables: list[VariableSchema] = Field(default_factory=list)
    dependencies: dict[str, list[str]] = Field(default_factory=dict)
