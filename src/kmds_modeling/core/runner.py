import os
import json
import importlib
from typing import Type

import joblib
import numpy as np
import pandas as pd
import yaml

from .path_coordinator import PathCoordinator
from .task_classification import ClassificationTaskRunner
from .task_clustering import ClusteringTaskRunner
from .task_graph import GraphTaskRunner
from .task_regression import RegressionTaskRunner
from .task_survival import SurvivalTaskRunner


class ExperimentRunner:
    def __init__(self, config_path: str):
        self.config_path = os.path.abspath(config_path)
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.custom_transformers = []
        self.task_type = self.config.get("project", {}).get("task_type")
        self.durations = None
        self.event_observed = None
        self._load_data()

    def _load_data(self):
        data_cfg = self.config["data"]
        working_dir = data_cfg.get("working_dir") or os.path.dirname(self.config_path)
        self.path_coordinator = PathCoordinator(working_dir=working_dir, config=self.config)

        df = pd.read_csv(self.path_coordinator.model_ready_dataset_path)

        index_column = data_cfg.get("index_column")
        if index_column:
            if index_column in df.columns:
                df.set_index(index_column, inplace=True)
            else:
                df.index.name = index_column

        if self.task_type == "SURVIVAL_ANALYSIS":
            project_cfg = self.config["project"]
            duration_col = project_cfg.get("duration_variable")
            event_col = project_cfg.get("event_variable")
            if not duration_col or not event_col:
                raise ValueError(
                    "project.duration_variable and project.event_variable must be set for SURVIVAL_ANALYSIS."
                )
            self.durations = df[duration_col]
            self.event_observed = df[event_col]
            self.y = self.event_observed
            self.X = df.drop(columns=[duration_col, event_col])
        else:
            target = self.config["project"]["target_variable"]
            self.y = df[target]
            self.X = df.drop(columns=[target])

    def register_transformer(self, transformer):
        self.custom_transformers.append(transformer)

    def _apply_transformers(self, X_train: pd.DataFrame, X_val: pd.DataFrame, y_train: pd.Series):
        X_tr_fe = X_train.copy()
        X_val_fe = X_val.copy()
        for trans in self.custom_transformers:
            X_tr_fe = trans.fit_transform(X_tr_fe, y_train)
            X_val_fe = trans.transform(X_val_fe)
        return X_tr_fe, X_val_fe

    def _get_task_runner(self, task_type: str):
        task_map = {
            "TABULAR_CLASSIFICATION": ClassificationTaskRunner,
            "TABULAR_REGRESSION": RegressionTaskRunner,
            "SURVIVAL_ANALYSIS": SurvivalTaskRunner,
            "GRAPH_NODE_CLASSIFICATION": GraphTaskRunner,
            "GRAPH_NODE_REGRESSION": GraphTaskRunner,
            "GRAPH_DISCOVERY": GraphTaskRunner,
            "CLUSTERING": ClusteringTaskRunner,
        }
        task_class = task_map.get(task_type)
        if task_class is None:
            raise ValueError(
                f"Unsupported task type: {task_type}. Supported tasks are: {', '.join(task_map)}."
            )
        return task_class(
            config=self.config,
            path_coordinator=self.path_coordinator,
            X=self.X,
            y=self.y,
            durations=self.durations,
            event_observed=self.event_observed,
        )

    def _validate_task_type(self):
        task_type = self.config.get("project", {}).get("task_type")
        if not task_type:
            raise ValueError("project.task_type must be set in model_config.yaml.")
        return task_type

    def run_evaluation(self) -> pd.DataFrame:
        task_type = self._validate_task_type()
        runner = self._get_task_runner(task_type)
        runner.custom_transformers = self.custom_transformers
        return runner.run_evaluation()

    def export_champion(self):
        task_type = self._validate_task_type()
        runner = self._get_task_runner(task_type)
        runner.custom_transformers = self.custom_transformers
        return runner.export_champion()
