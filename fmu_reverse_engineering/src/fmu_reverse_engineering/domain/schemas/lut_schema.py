from pydantic import BaseModel


class LUTSchema(BaseModel):
    dimensions: list[str]
    shape: list[int]
    interpolation: str
    storage_path: str
