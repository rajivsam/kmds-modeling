# KMDS Copilot Initialization

## Purpose
This file summarizes the current state of the `kmds-modeling` repo for a Copilot-style implementation agent. It focuses on the design governance feature and the current runtime architecture, which now supports task-specific runner modules.

## Current Repo State
- The installable package lives under `src/kmds_modeling/`.
- `src/kmds_modeling/core/base.py` defines abstract interfaces:
  - `BaseFeatureTransformer`
  - `BaseModelCandidate`
- `src/kmds_modeling/core/runner.py` implements `ExperimentRunner` with task dispatching:
  - loads runtime config and resolves `working_dir` via `PathCoordinator`
  - branches by `project.task_type` into task-specific runners
  - supports classification and regression runtime workflows
  - uses `task_classification.py` and `task_regression.py` for current execution paths
  - `task_graph.py` and `task_clustering.py` exist for future runtime implementation
- `src/kmds_modeling/cli.py` exposes `evaluate` and `export` commands.

## Design Governance Feature
- The documentation for the governance feature is primarily in `documents/design_governance_feature.md`.
- A lightweight governance engine exists in `documents/advisor.py` as `DesignAdvisor`.
- `DesignAdvisor` currently expresses the advisory framework across all supported tasks, but the core runtime currently implements classification and regression evaluation only.
- It enforces an input contract of:
  1. fixed task intent literals,
  2. entity mapping awareness,
  3. a strategy toggle for priority,
  4. data profile validation via cardinality and minority ratio.

## Current Runtime Task Architecture
- `ExperimentRunner` now uses `project.task_type` in `model_config.yaml` to select a task runner.
- Supported runtime task modules:
  - `task_classification.py` for `TABULAR_CLASSIFICATION`
  - `task_regression.py` for `TABULAR_REGRESSION`
  - `task_graph.py` for graph-based analysis placeholders
  - `task_clustering.py` for clustering placeholders
- `task_graph.py` and `task_clustering.py` currently raise `NotImplementedError` for runtime evaluation and export.
- The graph path is intentionally isolated so it can later map `dd-parser-cleaner` metadata into PyG/DGL node/edge objects from the KMDS workspace layout.

## Validation Status
- Regression tests for the SBA classifier path passed successfully.

## Current Tabular Classification Logic
- `DesignAdvisor.get_recommendation()` for `TABULAR_CLASSIFICATION` does:
  - reject classification if target cardinality > 20
  - compute `minority_ratio`
  - bucket the dataset into:
    - Bucket 1: Mild imbalance (>= 10%) → stratified baseline
    - Bucket 2: Moderate imbalance (1%–10%) → cost-sensitive learning; no resampling
    - Bucket 3: Extreme imbalance (< 1%) → anomaly detection; no resampling
- The classification runtime now integrates the task runner path in `ExperimentRunner`.
- Candidate wrappers for classification must still provide `predict_proba`, but the runner now supports sklearn-style instantiation for both wrapper candidates and native sklearn models.

## What is Implemented Today
- A generic modeling engine for chained transformers and candidate evaluation
- A classification-focused evaluation loop
- A regression evaluation loop via a separate task module
- Runtime artifact export for champion model and feature pipeline
- Governance documentation and advisor logic separated from runtime

## What is Not Yet Implemented
- runtime governance enforcement in `src/kmds_modeling/`
- direct use of user intent / task literals in the package config beyond `project.task_type`
- graph and clustering runtime evaluation/export support
- explicit class-weight or anomaly-detection candidate wrappers for the classification runner

## Recommended Focus for Copilot
1. Keep `documents/advisor.py` as a separate advisory module.
2. Add a lightweight config contract for `project.task_type`, `user_intent`, `entities`, and `strategy`.
3. Preserve the current tabular implementation while keeping graph and clustering as isolated future paths.
4. Keep the existing no-leakage transformer contract and index preservation intact.

## Recommendations Documents
- `documents/modeling_recommendations/tabular_classification_recommendations.md`
- `documents/modeling_recommendations/tabular_regression_recommendations.md`
- `documents/modeling_recommendations/graph_modeling_recommendations.md`
- `documents/modeling_recommendations/clustering_recommendations.md`

## Key File Locations
- `documents/design_governance_feature.md` — governance concept and rule sets
- `documents/advisor.py` — current governance engine implementation
- `src/kmds_modeling/core/runner.py` — evaluation and export orchestration

## Workspace Recommendation Path
- Runtime recommendations should be written to `working_dir/documents/modeling_recommendations/` in the consuming KMDS workspace, not to the package repo `documents/` directory.
- The package should expose this path through `PathCoordinator` so the runtime can resolve it reliably from `model_config.yaml`.
- `src/kmds_modeling/core/base.py` — transformer / candidate interface
- `src/kmds_modeling/core/path_coordinator.py` — KMDS path resolution
- `src/kmds_modeling/cli.py` — CLI entry point
