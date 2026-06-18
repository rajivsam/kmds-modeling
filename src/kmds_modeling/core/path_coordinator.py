import os
from typing import Any, Dict


class PathCoordinator:
    """Resolves KMDS modeling package paths from the workspace working directory."""

    def __init__(self, working_dir: str, config: Dict[str, Any]):
        self.working_dir = os.path.abspath(working_dir)
        self.config = config or {}

    def _remove_anchor_prefix(self, config_value: str, anchor: str) -> str:
        if config_value.startswith(anchor + os.sep):
            return config_value.replace(anchor + os.sep, "", 1)
        return config_value

    @property
    def model_ready_data_file(self) -> str:
        return self.config.get("model_ready_data_file", "model_ready_numeric_data.csv")

    @property
    def featurization_output_dir(self) -> str:
        return self.config.get("featurization_output_dir", "featurization")

    @property
    def modeling_output_dir(self) -> str:
        return self.config.get("modeling_output_dir", "models")

    def _resolve_data_dir(self, config_value: str) -> str:
        if os.path.isabs(config_value):
            return config_value
        config_value = self._remove_anchor_prefix(config_value, "data")
        return os.path.join(self.working_dir, "data", config_value)

    def _resolve_workspace_dir(self, config_value: str) -> str:
        if os.path.isabs(config_value):
            return config_value
        return os.path.join(self.working_dir, config_value)

    @property
    def featurization_output_path(self) -> str:
        return self._resolve_data_dir(self.featurization_output_dir)

    @property
    def modeling_output_path(self) -> str:
        return self._resolve_workspace_dir(self.modeling_output_dir)

    @property
    def workspace_documents_path(self) -> str:
        return os.path.join(self.working_dir, "documents")

    @property
    def modeling_recommendations_path(self) -> str:
        return os.path.join(self.workspace_documents_path, "modeling_recommendations")

    @property
    def model_ready_dataset_path(self) -> str:
        return os.path.join(self.featurization_output_path, self.model_ready_data_file)

    @property
    def model_weights_path(self) -> str:
        return os.path.join(self.modeling_output_path, "model_weights.pkl")

    @property
    def feature_pipeline_path(self) -> str:
        return os.path.join(self.modeling_output_path, "feature_pipeline.pkl")

    @property
    def calibrator_path(self) -> str:
        return os.path.join(self.modeling_output_path, "calibrator.pkl")

    @property
    def metadata_path(self) -> str:
        return os.path.join(self.modeling_output_path, "metadata.json")

    @property
    def active_scores_path(self) -> str:
        return os.path.join(self.modeling_output_path, "active_set_scores.csv")
