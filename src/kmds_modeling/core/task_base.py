import importlib
import os
from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd


class BaseTaskRunner(ABC):
    def __init__(self, config: Dict, path_coordinator, X: pd.DataFrame, y: pd.Series):
        self.config = config
        self.path_coordinator = path_coordinator
        self.X = X
        self.y = y
        self.custom_transformers = []

    def register_transformer(self, transformer):
        self.custom_transformers.append(transformer)

    def _apply_transformers(self, X_train: pd.DataFrame, X_val: pd.DataFrame, y_train: pd.Series):
        X_tr_fe = X_train.copy()
        X_val_fe = X_val.copy()
        for trans in self.custom_transformers:
            X_tr_fe = trans.fit_transform(X_tr_fe, y_train)
            X_val_fe = trans.transform(X_val_fe)
        return X_tr_fe, X_val_fe

    def _get_candidate_class(self, class_path: str):
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def _instantiate_candidate(self, candidate_class, hyperparameters: Dict):
        if not hyperparameters:
            return candidate_class()
        try:
            return candidate_class(**hyperparameters)
        except TypeError:
            return candidate_class(hyperparameters)

    @abstractmethod
    def run_evaluation(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def export_champion(self):
        pass
