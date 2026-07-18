# KMDS Modeling Architecture

## Overview
`kmds-modeling` is shaped as a small runtime package focused on modeling workflow orchestration. It is intentionally separated into:
- an installable package under `src/kmds_modeling/`
- workspace-facing contract documentation under `documents/`
- CLI and discovery entry points for runtime execution

## Key runtime layers

### 1. Package entrypoints
- `src/kmds_modeling/__init__.py` exposes the public API.
- `src/kmds_modeling/cli.py` exposes `kmds-modeling evaluate` and `kmds-modeling export`.
- `src/kmds_modeling/package_info.py` supports runtime metadata discovery.

### 2. Runtime orchestration
- `src/kmds_modeling/core/runner.py` implements `ExperimentRunner`.
- It loads `model_config.yaml`, resolves workspace paths via `PathCoordinator`, and dispatches by task type.
- It supports evaluation and champion export as separate flows.

### 3. Workspace path coordination
- `src/kmds_modeling/core/path_coordinator.py` translates `data.working_dir` into concrete paths for:
  - feature-engineered data files
  - modeling output directories
  - `documents/modeling_contracts/`

### 4. Task runners
- `src/kmds_modeling/core/task_classification.py` handles tabular classification evaluation.
- `src/kmds_modeling/core/task_regression.py` handles tabular regression evaluation.
- Additional task modules exist as future extension points:
  - `task_graph.py`
  - `task_clustering.py`
  - `task_survival.py`

### 5. Modeling advisory and contract guidance
- `documents/advisor.py` and `documents/design_governance_feature.md` describe governance and guidance logic.
- `documents/modeling_contracts/` contains task-specific guidance artifacts.
- This advisory layer is intentionally kept separate from runtime package code.

## Data and config flow
1. User provides `model_config.yaml` with `project`, `data`, `experiment_settings`, and `candidates`.
2. `ExperimentRunner` resolves the working directory and loads the featurized dataset.
3. The selected task runner evaluates candidates and builds a leaderboard.
4. On export, the champion candidate is retrained and serialized along with pipeline metadata.

## Extension points
- Add new task runners by implementing a new module under `src/kmds_modeling/core/` and updating task dispatch logic.
- Keep workspace-specific artifacts and sample workflows outside `src/` in `documents/`, `notebooks/`, or `examples/`.

## Packaging
- `pyproject.toml` defines the installable package as `kmds-modeling`.
- The package is built from `src/` and exposes a console script entry point.
- `documents/` artifacts are not included in the installable package.
