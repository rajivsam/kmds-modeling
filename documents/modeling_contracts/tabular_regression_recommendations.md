# Tabular Regression Recommendations

## Purpose
This document explains how to implement a KMDS-compatible `TABULAR_REGRESSION` task package. It describes the config contract, runtime expectations, candidate and transformer interfaces, and export template.

## KMDS Task Contract
- `project.task_type`: `TABULAR_REGRESSION`
- `project.target_variable`: numeric target column name
- `project.strategy`: `MAX_ACCURACY` or `HIGH_INTERPRETABILITY`
- `project.user_intent`: descriptive modeling intent
- `data.working_dir`: KMDS workspace root directory
- `data.index_column`: optional row identity column to preserve provenance
- `data.featurization_output_dir`: directory containing featurized dataset
- `production_target.export_directory`: artifact export location

## Data Requirements
- Input should be the cleaned, featurized dataset produced by the KMDS featurization upstream flow.
- Preserve the source record index via `data.index_column` or DataFrame index.
- The target must be numeric and continuous.
- Use derived numerical features; avoid raw text or unencoded categorical columns.

## Model and Transformer Contracts
### Feature Transformers
- Transformers must implement `fit_transform(X_train, y_train)` and `transform(X_val)`.
- Transformers are only fit on training splits and applied to validation and export data.
- Transformers must preserve DataFrame indices.
- Export the transformer list as `feature_pipeline.pkl` alongside the champion model.

### Regression Candidates
- Candidates must implement:
  - `fit(X_train, y_train)`
  - `predict(X)` -> `np.ndarray`
- Candidate classes are instantiated via `class_path` and `hyperparameters`.
- If hyperparameters are empty, instantiation may use the no-arg constructor.

## Evaluation Contract
- Use `RegressionTaskRunner` in `src/kmds_modeling/core/task_regression.py`.
- Use `KFold` cross-validation.
- Evaluation metrics:
  - `mean_r2`
  - `mean_mae`
- The runner computes fold-level scores and returns a leaderboard DataFrame.

## Strategy Branching
- `HIGH_INTERPRETABILITY`
  - Use additive or kernel-based models such as GAMs or Gaussian Processes.
  - Emphasize explainability and partial dependence diagnostics.
- `MAX_ACCURACY`
  - Use high-capacity models such as XGBoost, Random Forest, or TabPFN.
  - Avoid simple linear models in this branch.

## Export Contract
- `ExperimentRunner.export_champion()` writes:
  - `model_weights.pkl`
  - `feature_pipeline.pkl`
  - `metadata.json`
- Required metadata fields:
  - `model_name`
  - `version`
  - `features`
  - `target`
  - `metrics.primary_metric`

## Implementation Template
### Example `model_config.yaml`
```yaml
data:
  working_dir: .
  index_column: loan_id
  featurization_output_dir: featurization
  modeling_output_dir: models
  model_ready_data_file: model_ready_numeric_data.csv

project:
  name: loss_amount_prediction
  task_type: TABULAR_REGRESSION
  target_variable: expected_loss
  experiment_version: v1
  strategy: HIGH_INTERPRETABILITY
  user_intent: "Loss amount estimation"

experiment_settings:
  primary_metric: mae
  cross_validation:
    splits: 5
    random_state: 42

candidates:
  - name: gam_regressor
    class_path: pygam.GAM
    hyperparameters:
      n_splines: 20
      max_iter: 100

production_target:
  champion_candidate_name: gam_regressor
  export_directory: ./models
```

### Candidate Skeleton
```python
from kmds_modeling.core.base import BaseModelCandidate
from sklearn.ensemble import RandomForestRegressor

class MyRegressorCandidate(BaseModelCandidate):
    def __init__(self, hyperparameters: dict):
        super().__init__(hyperparameters)
        self.model = RandomForestRegressor(**self.hyperparameters)

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict(self, X):
        return self.model.predict(X)
```

### Transformer Skeleton
```python
from kmds_modeling.core.base import BaseFeatureTransformer

class MyFeatureTransformer(BaseFeatureTransformer):
    def fit(self, X, y=None):
        self.columns_ = X.select_dtypes(include=["number"]).columns
        return self

    def transform(self, X):
        out = X[self.columns_].copy()
        return out
```

## Notes
- This document is the authoritative KMDS regression guideline for agents and implementers.
- Use the package's runtime contract exactly as defined in `src/kmds_modeling/core/task_regression.py` and `src/kmds_modeling/core/task_base.py`.
