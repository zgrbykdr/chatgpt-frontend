from abc import ABC, abstractmethod

import pandas as pd


class SurrogateModel(ABC):
    name: str
    family: str

    @abstractmethod
    def fit(self, x: pd.DataFrame, y: pd.Series) -> None:
        raise NotImplementedError

    @abstractmethod
    def predict(self, x: pd.DataFrame) -> pd.Series:
        raise NotImplementedError

    @abstractmethod
    def complexity(self) -> float:
        raise NotImplementedError
