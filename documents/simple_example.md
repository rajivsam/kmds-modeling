# Simple KMDS Modeling Example

This example is intentionally tiny: it illustrates how the framework is supposed to be used, not how to solve a real modeling problem.

## What it shows
- `ExperimentRunner` reads config and loads input data
- `ExampleTransformer` is a minimal transformer that preserves the input index
- `ExampleCandidate` is a minimal candidate wrapper using `DummyClassifier`
- The runner can evaluate candidates and export a champion

## Example usage
1. Put your input CSV in `data/model_ready_numeric_data.csv`.
2. Use `model_config.yaml` to point to the file and the target variable.
3. Register `ExampleTransformer` and use `ExampleCandidate` in your workspace.

## Minimal intended pattern
- `BaseFeatureTransformer` defines `fit`, `transform`, and `fit_transform`
- `BaseModelCandidate` defines `fit` and `predict_proba`
- `ExperimentRunner` applies transformers on training folds only and then evaluates model candidates

## Simple illustration
This example is small because the goal is to show framework shape:
- no feature engineering details
- no production model tuning
- no KMDS observation serialization yet

Use this pattern as a starter, then replace `ExampleTransformer` and `ExampleCandidate` with KMDS-specific implementations.
