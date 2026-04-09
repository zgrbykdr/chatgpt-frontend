from dataclasses import dataclass

import pandas as pd


@dataclass
class RegimeDetector:
    def detect(self, df: pd.DataFrame, target: str) -> dict:
        return {"target": target, "regimes": 1, "strategy": "global"}
