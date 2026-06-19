# Tabular Classification Recommendations

## Purpose
This document explains how to implement a KMDS-compatible `TABULAR_CLASSIFICATION` task package. It describes the config contract, runtime expectations, candidate and transformer interfaces, and export template.

## KMDS Task Contract
- `project.task_type`: `TABULAR_CLASSIFICATION`
- `project.target_variable`: categorical target column name
- `project.strategy`: `MAX_ACCURACY` or `HIGH_INTERPRETABILITY`
- `project.user_intent`: descriptive modeling intent
- `data.working_dir`: KMDS workspace root directory
- `data.index_column`: optional row identity column to preserve provenance
- `data.featurization_output_dir`: directory containing featurized dataset
- `production_target.export_directory`: artifact export location

## Data Requirements
- Input should be the cleaned, featurized dataset produced by the KMDS featurization upstream flow.
- Preserve the source record index via `data.index_column` or DataFrame index.
- The target must be categorical with `target_cardinality <= 20`.
- For tabular classification, do not derive graph features by flattening entity relationships; if multiple entity IDs exist, consider a graph task instead.

## Model and Transformer Contracts
### Feature Transformers
- Transformers must implement `fit_transform(X_train, y_train)` and `transform(X_val)`.
- Transformers are only fit on training splits and applied to validation and export data.
- Transformers must preserve DataFrame indices.
- Export the transformer list as `feature_pipeline.pkl` alongside the champion model.

### Classification Candidates
- Candidates must implement:
  - `fit(X_train, y_train)`
  - `predict_proba(X)` -> `np.ndarray`
- `predict_proba(X)` may return either:
  - 1D positive-class scores, or
  - 2D class probabilities with the positive class in the last column.
- Candidate classes are instantiated via `class_path` and `hyperparameters`.
- If hyperparameters are empty, instantiation may use the no-arg constructor.

## Evaluation Contract
- Use `ClassificationTaskRunner` in `src/kmds_modeling/core/task_classification.py`.
- Use stratified cross-validation via `StratifiedKFold`.
- Evaluation metrics:
  - `mean_roc_auc`
  - `mean_f1`
- The runner computes fold-level scores and returns a leaderboard DataFrame.

## Imbalance Strategy
KMDS classifies imbalance into three buckets:
- Bucket 1: Mild imbalance (`minority_ratio >= 0.10`)
  - Use stratified baselines; no special balancing.
- Bucket 2: Moderate imbalance (`0.01 <= minority_ratio < 0.10`)
  - Use cost-sensitive models or class weighting.
- Bucket 3: Extreme imbalance (`minority_ratio < 0.01`)
  - Use anomaly detection or specialized rare-event modeling.
- Do not perform synthetic oversampling in production-ready KMDS classification.

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
  name: sba_default_prediction
  task_type: TABULAR_CLASSIFICATION
  target_variable: loan_status_r
  experiment_version: v1
  strategy: MAX_ACCURACY
  user_intent: "Loan default prediction"

experiment_settings:
  primary_metric: roc_auc
  cross_validation:
    splits: 5
    random_state: 42

candidates:
  - name: xgb_classifier
    class_path: xgboost.sklearn.XGBClassifier
    hyperparameters:
      objective: binary:logistic
      eval_metric: auc
      use_label_encoder: false
      random_state: 42

production_target:
  champion_candidate_name: xgb_classifier
  export_directory: ./models
```

### Candidate Skeleton
```python
from kmds_modeling.core.base import BaseModelCandidate
import xgboost as xgb

class MyClassifierCandidate(BaseModelCandidate):
    def __init__(self, hyperparameters: dict):
        super().__init__(hyperparameters)
        self.model = xgb.XGBClassifier(**self.hyperparameters)

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict_proba(self, X):
        return self.model.predict_proba(X)
```

### Transformer Skeleton
```python
from kmds_modeling.core.base import BaseFeatureTransformer

class MyFeatureTransformer(BaseFeatureTransformer):
    def fit(self, X, y=None):
        self.columns_ = X.columns
        return self

    def transform(self, X):
        out = X[self.columns_].copy()
        return out
```

## Notes
- This document is the authoritative KMDS classification guideline for agents and implementers.
- Use the package's runtime contract exactly as defined in `src/kmds_modeling/core/task_classification.py` and `src/kmds_modeling/core/task_base.py`.
