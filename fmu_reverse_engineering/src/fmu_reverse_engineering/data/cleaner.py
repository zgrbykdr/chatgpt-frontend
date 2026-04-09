import pandas as pd


class DataCleaner:
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.replace([float("inf"), float("-inf")], pd.NA).dropna()
