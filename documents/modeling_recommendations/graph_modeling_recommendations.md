# Graph Modeling Recommendations

## Recommended Framework
- Use graph-based analysis only when the dataset includes explicit entity relationships or multiple ID-like fields.
- Map entities and relationships first, then choose the graph task type:
  - `GRAPH_NODE_CLASSIFICATION`
  - `GRAPH_NODE_REGRESSION`
  - `GRAPH_DISCOVERY`

### Node Classification
- Use GraphSAGE, GCN, or a relational GNN when predicting a label for entities.
- Handle imbalance through loss reweighting rather than resampling.

### Node Regression
- Use RGCN or HAN for relational regression tasks.
- Preserve entity topology and avoid graph structure resampling.

### Graph Discovery
- Use representation learning and community detection.
- Focus on topology exploration rather than direct target prediction.
