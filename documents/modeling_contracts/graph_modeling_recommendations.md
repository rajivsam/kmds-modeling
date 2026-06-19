# Graph Modeling Recommendations

## Purpose
This document explains how to build a KMDS-compatible graph modeling package. It is intended for agents and implementers who need explicit contracts and implementation patterns for graph-based tasks.

## KMDS Task Contract
- `project.task_type`: one of
  - `GRAPH_NODE_CLASSIFICATION`
  - `GRAPH_NODE_REGRESSION`
  - `GRAPH_DISCOVERY`
- `project.user_intent`: explicit graph modeling intent
- `entities`: explicit entity mapping fields
- `data.working_dir`: KMDS workspace root directory
- `data.index_column`: optional row identity column for provenance
- `data.featurization_output_dir`: directory containing feature data
- `production_target.export_directory`: artifact export location

## When to Use Graph Modeling
- The dataset contains multiple entity identifiers or explicit relationships.
- The objective depends on entity connectivity rather than only row-level features.
- Flattening relationships into a single table would lose signal or create leakage.

## Graph Task Types
- `GRAPH_NODE_CLASSIFICATION`
  - Predict a discrete label for nodes.
  - Use when the target is a property of an entity connected in a graph.
- `GRAPH_NODE_REGRESSION`
  - Predict a numeric value for nodes.
  - Use when the target is a continuous property of an entity.
- `GRAPH_DISCOVERY`
  - Unsupervised discovery of links, communities, or latent structure.
  - Use when the objective is topology insight rather than direct target prediction.

## Data and Topology Requirements
- Consume entity metadata from `dd-parser-cleaner` or equivalent.
- Build explicit node and edge tables before modeling.
- Preserve the original relational schema and avoid collapsing the graph into a flat tabular table.
- If the dataset includes multiple ID-like columns with a supervised target, verify whether a graph path is required.

## Runtime Status
- `src/kmds_modeling/core/task_graph.py` currently raises `NotImplementedError` for runtime evaluation and export.
- This document is advisory-only until graph runtime is implemented.
- The implementation should remain isolated from the tabular classification/regression paths.

## Implementation Template
### Expected Candidate Interface
For graph classification:
```python
class GraphNodeClassifier(BaseModelCandidate):
    def __init__(self, hyperparameters: dict):
        super().__init__(hyperparameters)
        self.model = ...

    def fit(self, graph_data, y):
        self.model.fit(graph_data, y)
        return self

    def predict_proba(self, graph_data):
        return self.model.predict_proba(graph_data)
```

For graph regression:
```python
class GraphNodeRegressor(BaseModelCandidate):
    def __init__(self, hyperparameters: dict):
        super().__init__(hyperparameters)
        self.model = ...

    def fit(self, graph_data, y):
        self.model.fit(graph_data, y)
        return self

    def predict(self, graph_data):
        return self.model.predict(graph_data)
```
```

### Graph Data Object Template
- `node_features`: node-level feature matrix
- `edge_index` / `edge_list`: graph connectivity
- `node_labels`: target labels for supervised node tasks
- `entity_types`: optional heterogeneous entity metadata

### Example `model_config.yaml`
```yaml
data:
  working_dir: .
  featurization_output_dir: graph_features
  modeling_output_dir: models
  model_ready_data_file: graph_ready_data.csv

project:
  name: entity_graph_model
  task_type: GRAPH_NODE_CLASSIFICATION
  experiment_version: v1
  user_intent: "Predict borrower risk in relationship graph"

experiment_settings:
  primary_metric: roc_auc
  cross_validation:
    splits: 5
    random_state: 42

candidates:
  - name: heterogeneous_gnn
    class_path: my_graph_models.HeterogeneousGNNCandidate
    hyperparameters:
      hidden_dim: 128
      num_layers: 2
      dropout: 0.3

production_target:
  champion_candidate_name: heterogeneous_gnn
  export_directory: ./models
```

## Recommended Design Patterns
### Homogeneous Graphs
- Use GraphSAGE, GCN, or similar message-passing architectures.
- Keep node features and adjacency structure separate.

### Bipartite Graphs
- Use bipartite-aware GNNs or co-clustering for discovery.
- Preserve the two-mode structure rather than collapsing entities.

### Heterogeneous Graphs
- Use RGCN, HAN, or other heterogeneous graph models.
- Preserve entity and relation types.
- For imbalance, apply loss weighting rather than resampling graph structure.

## Governance and Compliance
- Document the chosen task type and why graph modeling is required.
- Explain why a tabular path is not sufficient.
- Include entity mapping and topology assumptions in the implementation notes.

## Notes
- This document is an advisory blueprint for graph package design.
- A future runtime implementation must serialize graph data objects and model weights.
