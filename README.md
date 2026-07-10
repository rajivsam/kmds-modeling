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

## Package discovery
Clients can discover runtime metadata using the package API or import installed package metadata.

```python
from kmds_modeling import get_package_info

info = get_package_info()
print(info)
```

The discovery payload includes standard fields used across KMDS packages:
- `package_name`
- `version`
- `entry_points`
- `cli_commands`
- `provided_packages`
- `documentation_note`

This package publishes the `kmds-modeling` console script entry point as:
- `kmds-modeling = "kmds_modeling.cli:cli"`

Clients can inspect the loaded entry points at runtime using the package metadata:

```python
from kmds_modeling import get_package_info

info = get_package_info()
print(info["entry_points"])
print(info["cli_commands"])
```

The package also exposes a spec discovery API for building a validated modeling configuration from minimal instructions.

```python
from kmds_modeling import get_spec_questions, build_model_spec

requirements = {
    "project": {"task_type": "TABULAR_CLASSIFICATION"},
    "data": {"working_dir": "."},
}

questions = get_spec_questions(requirements)
print(questions)

# After supplying answers to the spec questions,
# build the final model config and write it to YAML.
spec = build_model_spec(requirements)
spec.to_yaml("model_config.yaml")
```

When the client provides modeling instructions that answer the required spec questions, this package can build the model spec and run the evaluation/export workflow to produce model artifacts.

When installed, the package can also be resolved via `importlib.metadata`:

```python
from importlib.metadata import version

print(version("kmds-modeling"))
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

## Spec discovery and build
Clients can use the package's spec discovery API to ask what configuration items are still required and then build a complete `model_config.yaml`.

```python
from kmds_modeling import get_spec_questions, build_model_spec

requirements = {
    "project": {
        "task_type": "TABULAR_CLASSIFICATION",
        "target_variable": "label",
        "user_intent": "Predict the probability of the positive class for business interventions.",
    },
    "data": {
        "working_dir": ".",
    },
}

questions = get_spec_questions(requirements)
for question in questions:
    print(question["field"], question["question"])

# Supply the remaining answers and build the final model spec.
requirements.update({
    "project": {
        **requirements["project"],
        "name": "customer_churn_classifier",
        "strategy": "MAX_ACCURACY",
    },
    "candidates": [
        {
            "name": "random_forest",
            "class_path": "my_models.RandomForestCandidate",
            "hyperparameters": {"n_estimators": 100},
        }
    ],
    "production_target": {"champion_candidate_name": "random_forest"},
})

spec = build_model_spec(requirements)
spec.to_yaml("model_config.yaml")
```

When modeling instructions cover the returned spec questions, this package can build the model spec and then run the evaluation/export workflow to produce model artifacts.

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
