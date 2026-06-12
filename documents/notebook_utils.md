# Notebook Utilities Design for `kmds-modeling`

## Purpose
The notebook utilities provide a lightweight launcher for the modeling package from a notebook or script in the KMDS workspace.

## Design Goals
- Follow the same pattern as `kmds-featurization` notebook utilities.
- Build a `PathCoordinator` from a workspace root.
- Expose artifact paths for modeling outputs.
- Load the model-ready dataset through the package coordinator.

## Interface
### `resolve_notebook_workspace_root(working_dir: str, config_name: str = "modeling_config.yaml") -> str`
- Accepts a workspace root or notebook directory.
- Returns the same root path.
- Raises if the directory does not exist.

### `load_workspace_config(working_dir: str, config_name: str = "modeling_config.yaml") -> Dict`
- Loads `modeling_config.yaml` from the workspace root.
- Returns a dict with config values.
- Raises if the config file is missing.

### `build_notebook_resolver(working_dir: str, config_name: str = "modeling_config.yaml") -> PathCoordinator`
- Loads workspace config.
- Instantiates a `PathCoordinator`.

### `get_modeling_artifact_paths(resolver: PathCoordinator) -> Dict[str, str]`
Returns absolute paths for:
- `model_ready_dataset_path`
- `model_weights_path`
- `feature_pipeline_path`
- `calibrator_path`
- `metadata_path`
- `active_scores_path`

### `load_model_ready_dataset(resolver: PathCoordinator, **read_csv_kwargs) -> pd.DataFrame`
- Loads the model-ready dataset from the path coordinator.
- Raises a `FileNotFoundError` if the dataset is missing.

## Example usage
```python
from kmds_modeling.core.notebook_utils import build_notebook_resolver, load_model_ready_dataset

resolver = build_notebook_resolver("/path/to/kmds_working")
df = load_model_ready_dataset(resolver)
```

## Validation
- The implementation is present in `src/kmds_modeling/core/notebook_utils.py`.
- It is already imported by `src/kmds_modeling/core/__init__.py`.

## Notes
- This design decouples notebook entry points from package internals.
- The notebook utils know only about `working_dir` and `modeling_config.yaml`.
- Path resolution and artifact definitions are delegated to the coordinator.
