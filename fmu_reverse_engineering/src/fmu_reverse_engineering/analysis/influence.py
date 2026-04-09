import pandas as pd


class InfluenceEngine:
    def compute_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        return df.corr(numeric_only=True).fillna(0.0)
