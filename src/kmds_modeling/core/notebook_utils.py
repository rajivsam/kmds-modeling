import os
from typing import Dict

import pandas as pd
import yaml

from .path_coordinator import PathCoordinator


def resolve_notebook_workspace_root(working_dir: str, config_name: str = "modeling_config.yaml") -> str:
    working_dir = os.path.abspath(working_dir)
    if not os.path.isdir(working_dir):
        raise FileNotFoundError(f"Notebook directory does not exist: {working_dir}")

    return working_dir


def load_workspace_config(working_dir: str, config_name: str = "modeling_config.yaml") -> Dict:
    workspace_root = resolve_notebook_workspace_root(working_dir, config_name=config_name)
    config_path = os.path.join(workspace_root, config_name)
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Modeling config not found at: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_notebook_resolver(working_dir: str, config_name: str = "modeling_config.yaml") -> PathCoordinator:
    config = load_workspace_config(working_dir, config_name=config_name)
    return PathCoordinator(working_dir=working_dir, config=config)


def get_modeling_artifact_paths(resolver: PathCoordinator) -> Dict[str, str]:
    return {
        "model_ready_dataset_path": resolver.model_ready_dataset_path,
        "model_weights_path": resolver.model_weights_path,
        "feature_pipeline_path": resolver.feature_pipeline_path,
        "calibrator_path": resolver.calibrator_path,
        "metadata_path": resolver.metadata_path,
        "active_scores_path": resolver.active_scores_path,
    }


def load_model_ready_dataset(resolver: PathCoordinator, **read_csv_kwargs) -> pd.DataFrame:
    path = resolver.model_ready_dataset_path
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Model-ready dataset not found at: {path}")
    return pd.read_csv(path, **read_csv_kwargs)
