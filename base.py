from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseFeatureTransformer(ABC):
    """Interface for ad-hoc dataset-level transformations."""
    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit internal parameters based on training data."""
        pass
        
    @abstractmethod
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transforms dataset features while maintaining the exact input index."""
        pass

    def fit_transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

class BaseModelCandidate(ABC):
    """Interface for uniform model orchestration."""
    def __init__(self, hyperparameters: dict):
        self.hyperparameters = hyperparameters
        
    @abstractmethod
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train the underlying model."""
        pass
        
    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return class probabilities. Must return a 2D array [prob_class_0, prob_class_1]."""
        pass