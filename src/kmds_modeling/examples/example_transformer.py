import pandas as pd
from pandas import Series
from ..core.base import BaseFeatureTransformer


class ExampleTransformer(BaseFeatureTransformer):
    """A minimal sample transformer that preserves the input index."""

    def fit(self, X: pd.DataFrame, y: Series = None):
        self.feature_names_ = list(X.columns)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        transformed = X.copy()
        transformed.index = X.index
        return transformed
