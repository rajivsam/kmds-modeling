# 📖 User Guide: kmds-modeling

## 📑 Overview
`kmds-modeling` is a lightweight runtime package for KMDS modeling workflows. It bridges feature-engineered KMDS artifacts and production-ready champion model exports through a config-driven evaluation and export pipeline.

## 🚀 The 10-Step Operational Recipe
1. **Install**: `pip install kmds-modeling`
2. **Prepare**: Author a `model_config.yaml` for your KMDS workspace.
3. **Place data**: Ensure `data/` and `documents/` paths exist under your workspace.
4. **Resolve workspace**: Set `project.task_type`, `project.target_variable`, and `data.working_dir` in `model_config.yaml`.
5. **Validate candidates**: Define model candidates with `class_path` and `hyperparameters`.
6. **Run evaluation**: `kmds-modeling evaluate --config /path/to/model_config.yaml`
7. **Review leaderboard**: Inspect model scores and candidate ranking.
8. **Select champion**: Set `production_target.champion_candidate_name`.
9. **Run export**: `kmds-modeling export --config /path/to/model_config.yaml`
10. **Consume artifacts**: Use `output/mlops_bundle/model_weights.pkl`, `feature_pipeline.pkl`, and `metadata.json`.

## 🔎 Core Components

### `ExperimentRunner`
This class is the runtime entrypoint for model evaluation and champion export.

- Loads YAML config from `--config`
- Resolves workspace paths with `PathCoordinator`
- Reads `model_ready_dataset_path` from featurized data
- Splits data into `X` and `y`
- Dispatches to task-specific runners based on `project.task_type`

### `PathCoordinator`
Resolves all important KMDS paths relative to `data.working_dir`:
- `data/model_ready_numeric_data.csv`
- `data/featurization/`
- `workspace/documents/modeling_contracts/`
- `output/models/`

It keeps path resolution generic and avoids hardcoded workspace layouts.

### Task Runners
`kmds-modeling` currently implements:
- `TABULAR_CLASSIFICATION` via `ClassificationTaskRunner`
- `TABULAR_REGRESSION` via `RegressionTaskRunner`

Placeholder runners exist for:
- `GRAPH_NODE_CLASSIFICATION`
- `GRAPH_NODE_REGRESSION`
- `GRAPH_DISCOVERY`
- `CLUSTERING`

### Task Comparison
| Feature | TABULAR_CLASSIFICATION | TABULAR_REGRESSION |
|---|---|---|
| Candidate interface | `predict_proba(X)` required | `predict(X)` required |
| Cross-validation type | `StratifiedKFold` | `KFold` |
| Primary leaderboard metrics | `mean_roc_auc`, `mean_f1` | `mean_r2`, `mean_mae` |
| Export behavior | retrain champion and serialize class-prob model | retrain champion and serialize regression model |
| Typical use case | binary or multiclass target scoring | numeric continuous target prediction |

## 🧠 Supported Workflow

### Model evaluation
The CLI command `kmds-modeling evaluate`:
- loads the configured dataset
- performs cross-validation
- evaluates each candidate
- returns a leaderboard of metrics

For classification, candidates must implement `predict_proba(X)`.
For regression, candidates must implement `predict(X)`.

### Champion export
The CLI command `kmds-modeling export`:
- retrains the champion candidate on the full dataset
- serializes `model_weights.pkl`
- serializes `feature_pipeline.pkl`
- writes `metadata.json`

## 🧾 Configuration Reference

Use `model_config.yaml` to define runtime behavior.

### Required sections
- `project`
  - `name`
  - `experiment_version`
  - `target_variable`
  - `task_type`
- `data`
  - `working_dir`
  - `index_column` (optional)
  - `model_ready_data_file`
  - `featurization_output_dir`
  - `modeling_output_dir`
- `experiment_settings`
  - `cross_validation.splits`
  - `cross_validation.random_state`
  - `validation_fraction` (optional)
  - `primary_metric`
- `candidates`
  - list of candidate definitions with `name`, `class_path`, `hyperparameters`
- `production_target`
  - `champion_candidate_name`
  - `export_directory`

### Example structure
```yaml
data:
  working_dir: "../dd_parser_cleaner_migration/sba_migration"
  index_column: "record_id"
  model_ready_data_file: "model_ready_numeric_data.csv"
  featurization_output_dir: "featurization"
  modeling_output_dir: "models"

project:
  name: "sba_modeling_experiment"
  experiment_version: "0.1.0"
  task_type: "TABULAR_CLASSIFICATION"
  target_variable: "loan_status_r"

experiment_settings:
  cross_validation:
    splits: 5
    random_state: 42
  validation_fraction: 0.2
  primary_metric: "roc_auc"

candidates:
  - name: "gradient_boosting"
    class_path: "kmds_modeling.sba.candidates.GradientBoostingCandidate"
    hyperparameters:
      n_estimators: 100
      learning_rate: 0.1
      max_depth: 3
  - name: "random_forest"
    class_path: "kmds_modeling.sba.candidates.RandomForestCandidate"
    hyperparameters:
      n_estimators: 100
      max_depth: 8

production_target:
  champion_candidate_name: "gradient_boosting"
  export_directory: "output/mlops_bundle"
```

## 🛠️ Package API

Import the package from Python:
```python
from kmds_modeling import ExperimentRunner

runner = ExperimentRunner("/path/to/model_config.yaml")
results = runner.run_evaluation()
```

The package also exposes metadata via `get_package_info()`.

## 🧪 Running Tests

Run tests with `pytest`:
```bash
pytest tests/test_task_runners.py
```

## 📁 Project Structure
- `src/kmds_modeling/` — installable package code
- `src/kmds_modeling/cli.py` — command-line entrypoint
- `src/kmds_modeling/core/runner.py` — evaluation orchestration
- `src/kmds_modeling/core/path_coordinator.py` — workspace path resolver
- `src/kmds_modeling/core/task_classification.py` — classification workflow
- `src/kmds_modeling/core/task_regression.py` — regression workflow
- `documents/modeling_contracts/` — KMDS modeling contract guidance
- `model_config.yaml` — example runtime config
- `tests/test_task_runners.py` — runtime validation tests

## 💡 Notes
- Keep model candidate classes importable through the Python path.
- Ensure `data.working_dir` is correct relative to the configuration file.
- The export path is relative to the current workspace unless an absolute path is provided.

---
*Next Session: Add workspace examples and extend the CLI with `validate` and `list-candidates` commands.*