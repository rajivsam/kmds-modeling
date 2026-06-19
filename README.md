# KMDS Modeling

`kmds-modeling` is a lightweight supporting package for KMDS modeling workflows. It provides the runtime plumbing, evaluation orchestration, artifact export utilities, and modeling contract documentation needed to bridge KMDS feature outputs and production-ready model assets.

## Overview
- Supports KMDS workspace modeling without embedding domain-specific business logic.
- Provides a generic `ExperimentRunner` engine for cross-validation, transformer orchestration, and candidate model evaluation.
- Includes a CLI for standard evaluation and production export flows.
- Keeps workspace-specific examples and artifacts outside the installable package.

## Key Features
- Config-driven modeling pipeline via YAML configuration files (e.g. `model_config.yaml`)
- Safe cross-validation with fold-specific transformer fitting
- Uniform candidate wrapper support for any model implementation
- Export of serialized model weights, feature pipeline, and metadata
- Path coordination for KMDS workspace layout handling
- Task contract documentation under `documents/modeling_contracts/`

## Installation
```bash
pip install kmds-modeling
```

## CLI
The package exposes a command-line interface for model evaluation and export.

```bash
kmds-modeling evaluate --config /path/to/modeling_config.yaml
kmds-modeling export --config /path/to/modeling_config.yaml
```

## Configuration
The package expects a YAML configuration file that defines:
- `project` settings such as name, version, task type, and target variable
- `data` settings including working directory, index column, and featurization paths
- `experiment_settings` for cross-validation and metrics
- `candidates` listing candidate models and their hyperparameters
- `production_target` for champion export paths

The `PathCoordinator` resolves workspace-relative paths, including `documents/modeling_contracts/`, and ensures the package operates on KMDS-generated modeling artifacts.

## Recommended Workflow
1. Generate feature-engineered data with KMDS upstream tools such as `kmds-featurization`.
2. Author a `modeling_config.yaml` with the correct workspace layout and candidate definitions.
3. Run `kmds-modeling evaluate` to compare candidate models and generate a leaderboard.
4. Select the champion candidate and run `kmds-modeling export` to produce model artifacts.

## Project Structure
- `src/kmds_modeling/` — installable package source
- `src/kmds_modeling/cli.py` — CLI entrypoint
- `src/kmds_modeling/core/runner.py` — evaluation and export orchestration
- `src/kmds_modeling/core/path_coordinator.py` — workspace path resolution
- `src/kmds_modeling/core/notebook_utils.py` — notebook-friendly utilities
- `documents/modeling_contracts/` — task contract documentation for KMDS modeling

## Contribution Notes
- Keep core modeling logic generic and focused on KMDS pipeline support.
- Add workspace-specific examples or experimental workflows outside the installable source tree.
- Avoid coupling the package to any single KMDS project domain.
