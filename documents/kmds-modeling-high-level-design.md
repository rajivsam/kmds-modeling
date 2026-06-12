1. High-Level Concept

The kmds-modeling package is a configuration-driven, pipeline-enforcing modeling framework. It acts as an abstraction layer between feature engineering outputs and deployment payloads.

+----------------------------------------+

| Upstream: model_ready_numeric_data.csv |
+----------------------------------------+
                   │
                   ▼ (Maintains 'record_id' Index)
+----------------------------------------+

| 1. ExperimentRunner Engine             | <--- Driven by modeling_config.yaml
|    - Splits train/test safely          |
|    - Executes custom transformers      |
+----------------------------------------+
                   │
                   ▼ (Cross-Validation Loops)
+----------------------------------------+

| 2. Candidate Evaluator                 |
|    - Ranks custom model wrappers       |
|    - Outputs validation leaderboards   |
+----------------------------------------+
                   │
                   ▼ (Triggered via CLI / Export)
+----------------------------------------+

| 3. MLOps Build Artifacts               | ---> [model_weights.pkl]
|    - Frozen pipeline serialization     | ---> [feature_pipeline.pkl]
+----------------------------------------+ ---> [metadata.json]

2. Structural Separation of Concerns

**The Framework's Job (Your Package):** Handle the data loading plumbing, enforce cross-validation without data leakage, compute standardized evaluation metrics, wrap models uniformly, and output standard MLOps-compliant build artifacts.

**The Data Scientist's Job (The Workspace):** Declare parameters in `modeling_config.yaml`, implement specific ad-hoc features using framework base classes, and write custom candidate models.

3. Incremental Implementation Phases

To build this without getting overwhelmed, implement and test it in these four discrete steps:

**Phase 1: Configuration & Data Contract Validation**
Build the YAML configuration parser. Implement data loaders that ingest the `model_ready_numeric_data.csv` file, strictly enforcing that `record_id` is retained as the DataFrame index.

**Phase 2: Abstract Base Classes (ABCs) & Custom Pipelines**
Define the abstract interfaces for transformers and candidate models. Build the orchestration engine that applies these transformers strictly within training splits to prevent data leakage.

**Phase 3: Cross-Validation & Evaluation Engine**
Build the looping mechanism that trains candidate models across K-folds. Implement metric logging and return a structured pandas DataFrame leaderboard.

**Phase 4: Artifact Packaging & CLI Entry Point**
Write the serialization routine that exports final model weights, pipeline steps, and a JSON schema manifest. Expose the pipeline runner via a command-line interface command.