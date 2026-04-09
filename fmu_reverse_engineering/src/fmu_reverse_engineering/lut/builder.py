from dataclasses import dataclass

import pandas as pd

from fmu_reverse_engineering.domain.schemas.lut_schema import LUTSchema


@dataclass
class LUTBuilder:
    interpolation: str = "linear"

    def build(self, df: pd.DataFrame, input_cols: list[str], output_col: str, storage_path: str) -> LUTSchema:
        shape = [max(2, min(25, df[c].nunique())) for c in input_cols]
        return LUTSchema(dimensions=input_cols, shape=shape, interpolation=self.interpolation, storage_path=storage_path)
