from dataclasses import dataclass

import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression

from .base import SurrogateModel
from .registry import model_registry


@dataclass
class ConstantModel(SurrogateModel):
    name: str = "constant"
    family: str = "simple"

    def __post_init__(self) -> None:
        self._model = DummyRegressor(strategy="mean")

    def fit(self, x: pd.DataFrame, y: pd.Series) -> None:
        self._model.fit(x, y)

    def predict(self, x: pd.DataFrame) -> pd.Series:
        return pd.Series(self._model.predict(x), index=x.index)

    def complexity(self) -> float:
        return 1.0


@dataclass
class LinearModel(SurrogateModel):
    name: str = "linear"
    family: str = "simple"

    def __post_init__(self) -> None:
        self._model = LinearRegression()

    def fit(self, x: pd.DataFrame, y: pd.Series) -> None:
        self._model.fit(x, y)

    def predict(self, x: pd.DataFrame) -> pd.Series:
        return pd.Series(self._model.predict(x), index=x.index)

    def complexity(self) -> float:
        return float(len(getattr(self._model, "coef_", [])) + 1)


model_registry.register("constant", ConstantModel)
model_registry.register("linear", LinearModel)
