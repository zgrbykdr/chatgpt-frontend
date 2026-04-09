from pydantic import BaseModel


class DatasetSchema(BaseModel):
    path: str
    rows: int
    columns: list[str]
