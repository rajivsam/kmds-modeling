import numpy as np
import pandas as pd
from pandas import Series
from sklearn.dummy import DummyClassifier
from ..core.base import BaseModelCandidate


class ExampleCandidate(BaseModelCandidate):
    """A minimal candidate that uses a dummy classifier."""

    def __init__(self, hyperparameters: dict):
        super().__init__(hyperparameters)
        strategy = hyperparameters.get("strategy", "prior")
        self.model = DummyClassifier(strategy=strategy)

    def fit(self, X_train: pd.DataFrame, y_train: Series):
        self.model.fit(X_train, y_train)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(X)
