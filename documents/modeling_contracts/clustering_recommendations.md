# Clustering Recommendations

## Purpose
This document explains how to build a KMDS-compatible `CLUSTERING` task package. It provides the KMDS task contract, data and output contracts, and an implementation template for clustering-based model design.

## KMDS Task Contract
- `project.task_type`: `CLUSTERING`
- `project.user_intent`: explicit clustering intent
- `data.working_dir`: KMDS workspace root directory
- `data.index_column`: optional row identity column to preserve provenance
- `data.featurization_output_dir`: directory containing feature data
- `production_target.export_directory`: artifact export location
- Clustering does not require `project.target_variable`

## When to Use Clustering
- The problem is exploratory or unsupervised.
- There is no reliable target label.
- The objective is to segment data into homogeneous sub-populations or derive structural features.
- Clustering is used as a preprocessing step for downstream supervised models or operational segmentation.

## Data Requirements
- Input should be cleaned KMDS featurization output.
- Preserve row identity through `data.index_column` or DataFrame index.
- Avoid clustering raw text or unencoded categorical features unless they are properly encoded.
- If the dataset includes multiple sub-populations, avoid pooling them without explicit segmentation logic.

## Clustering Implementation Contract
### Clusterer Interface
- If the clusterer is used directly as a candidate-like object, implement:
  - `fit(X)`
  - `transform(X)` -> DataFrame or array of cluster assignments
  - optionally `fit_predict(X)`
- Preserve the input index in output cluster labels.
- Export cluster assignments and cluster metadata for downstream use.

### Feature Transformer Interface
- Clustering pipelines that generate features must also follow the transformer contract:
  - `fit_transform(X, y=None)`
  - `transform(X)`
- Fit on training data only if clustering is part of a supervised downstream workflow.
- Export the full pipeline as `feature_pipeline.pkl` when clustering results feed subsequent models.

## Output Contract
- If clustering is a standalone task, export:
  - cluster labels per row
  - cluster membership strengths or distances
  - cluster summary metadata
- If clustering feeds a supervised model, export derived cluster features for the downstream pipeline.
- Preserve provenance and row IDs in all outputs.

## Runtime Status
- `src/kmds_modeling/core/task_clustering.py` currently raises `NotImplementedError` for runtime evaluation and export.
- This document is advisory-only until clustering runtime is implemented.

## Implementation Template
### Example `model_config.yaml`
```yaml
data:
  working_dir: .
  index_column: row_id
  featurization_output_dir: featurization
  modeling_output_dir: models
  model_ready_data_file: model_ready_numeric_data.csv

project:
  name: customer_segmentation
  task_type: CLUSTERING
  experiment_version: v1
  user_intent: "Segment customers into operational cohorts"

experiment_settings:
  primary_metric: silhouette_score
  cross_validation:
    splits: 5
    random_state: 42

candidates:
  - name: spectral_clustering
    class_path: my_clustering_models.SpectralClusteringWrapper
    hyperparameters:
      n_clusters: 5
      affinity: nearest_neighbors

production_target:
  champion_candidate_name: spectral_clustering
  export_directory: ./models
```

### Clusterer Skeleton
```python
from kmds_modeling.core.base import BaseFeatureTransformer

class SpectralClusteringWrapper:
    def __init__(self, n_clusters: int = 5, affinity: str = "nearest_neighbors"):
        self.n_clusters = n_clusters
        self.affinity = affinity
        self.model = None

    def fit(self, X):
        self.model = ...
        return self

    def transform(self, X):
        labels = self.model.fit_predict(X)
        return labels
```

### Transformer Skeleton
```python
from kmds_modeling.core.base import BaseFeatureTransformer

class ClusterFeatureTransformer(BaseFeatureTransformer):
    def fit(self, X, y=None):
        self.cols_ = X.select_dtypes(include=["number"]).columns
        return self

    def transform(self, X):
        return X[self.cols_].copy()
```

## Notes
- This document is the KMDS clustering guideline for agents and implementers.
- Use it to design a clustering package that preserves provenance, outputs cluster metadata, and aligns with future KMDS runtime expectations.
