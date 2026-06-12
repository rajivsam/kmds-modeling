# Path Coordinator Design for `kmds-modeling`

## Purpose
The `PathCoordinator` encapsulates the directory layout for the `kmds-modeling` package and resolves all runtime paths from a single `working_dir`.

## Design Principles
- Mirror KMDS package conventions used by `kmds-featurization`.
- Use workspace-relative paths only inside the coordinator.
- Keep package code dependent only on coordinator properties, not on raw path logic.
- Resolve output into `data/modeling` under the KMDS working directory.
- Resolve featurization inputs from `data/featurization` under the same working directory.

## Interface
### `PathCoordinator(working_dir: str, config: Dict[str, Any])`
- `working_dir` is the root of the KMDS workspace.
- `config` is loaded from `modeling_config.yaml`.

### Properties
- `working_dir` — absolute workspace root path
- `model_ready_data_file` — filename of model-ready CSV, default `model_ready_numeric_data.csv`
- `featurization_output_dir` — relative output directory for featurization data, default `featurization`
- `modeling_output_dir` — relative output directory for modeling artifacts, default `models`
- `featurization_output_path` — absolute path to `data/<featurization_output_dir>`
- `modeling_output_path` — absolute path under the working directory, default `<working_dir>/models`
- `model_ready_dataset_path` — absolute path to the model-ready dataset
- `model_weights_path` — absolute path for serialized model weights
- `feature_pipeline_path` — absolute path for serialized feature pipeline
- `calibrator_path` — absolute path for the probability calibrator
- `metadata_path` — absolute path for run metadata
- `active_scores_path` — absolute path for active-set scoring output

## Sample behavior
Given:
```yaml
working_dir: /home/rajiv/programming/dd_parser_cleaner_migration/sba_migration
modeling_output_dir: modeling
featurization_output_dir: featurization
model_ready_data_file: model_ready_numeric_data.csv
```
Then:
- `featurization_output_path` -> `/home/rajiv/programming/dd_parser_cleaner_migration/sba_migration/data/featurization`
- `model_ready_dataset_path` -> `/home/rajiv/programming/dd_parser_cleaner_migration/sba_migration/data/featurization/model_ready_numeric_data.csv`
- `modeling_output_path` -> `/home/rajiv/programming/dd_parser_cleaner_migration/sba_migration/models`
- `model_weights_path` -> `/home/rajiv/programming/dd_parser_cleaner_migration/sba_migration/models/model_weights.pkl`

## Validation
- The `PathCoordinator` is already implemented and imports successfully from `src/kmds_modeling/core/path_coordinator.py`.
- This mirrors the KMDS featurization coordinator design by providing workspace-rooted path resolution.

## Notes
- This interface keeps the modeling package independent of external notebook path logic.
- The `working_dir` is the canonical KMDS workspace root, not the notebook directory.
- All path computations happen inside the coordinator.
