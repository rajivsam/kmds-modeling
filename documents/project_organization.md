# KMDS Modeling Project Organization

## Purpose
This repository implements the `kmds-modeling` package for KMDS modeling and model selection. It is intended to consume outputs from `dd-parser-cleaner` and `kmds-featurization` and to serve as the modeling-phase component within the KMDS ecosystem.

## Directory Layout
- `main.py` — CLI entry point for evaluation and export commands.
- `src/kmds_modeling/` — package sources.
  - `src/kmds_modeling/core/base.py` — abstract interfaces for feature transformers and model candidates.
  - `src/kmds_modeling/core/runner.py` — `ExperimentRunner` implementation that loads config, applies transformers, runs cross-validation, and exports champion artifacts.
- `model_config.yaml` — example runtime config for the modeling pipeline.
- `documents/` — design and initialization documents.
- `pipeline_runner.py`, `evaluator.py` — placeholder scaffolds for future pipeline orchestration and metric handling.

## Design Principles
- Keep the package simple and aligned with KMDS lifecycle goals.
- Preserve `record_id` index and data provenance throughout transformation and model evaluation.
- Prevent leakage by fitting transformers only on training folds and applying them to validation folds.
- Use abstract candidate wrappers so the runner remains model-agnostic.
- Depend on upstream `dd-parser-cleaner` and `kmds-featurization` output rather than embedding lower-level data science code here.

## Expected Config Schema
The pipeline expects a config with these sections:
- `data`: input CSV path and index column name.
- `project`: target variable, project name, version.
- `experiment_settings`: cross-validation details and primary metric.
- `candidates`: candidate model definitions with `name`, `class_path`, and `hyperparameters`.
- `production_target`: champion candidate selection and export directory.

## Dependencies
- `kmds-featurization` (core dependency)
- `dd-parser-cleaner` (upstream data provenance dependency)
- `click` for CLI
- `pandas`, `numpy`, `scikit-learn`, `PyYAML`, `joblib`

## Next Implementation Steps
1. Implement candidate model wrappers that wrap specific downstream model types.
2. Implement feature transformer wrappers for featurization operations.
3. Add tests for `ExperimentRunner` cross-validation and index preservation.
4. Connect the pipeline to real featurization outputs and KMDS observation serialization.
