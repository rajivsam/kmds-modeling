# KMDS Modeling Product

## What it is
`kmds-modeling` is a lightweight runtime package for KMDS modeling workflows. It bridges KMDS feature-engineered artifacts and production-ready model exports by providing a config-driven evaluation and export pipeline.

## Who it is for
- KMDS modeling engineers who need to validate candidate models against featurized datasets.
- Integration teams that need a consistent workflow for champion model export.
- Analysts who want a reusable runtime package that resolves KMDS workspace paths.

## What it solves
- Manual wiring between KMDS-generated data artifacts and model evaluation pipelines.
- Inconsistent path resolution across KMDS workspaces.
- Ad hoc export of champion model weights and metadata.
- Lack of a compact, package-based runtime for model scoring and artifact packaging.

## Core capabilities
- YAML-driven model config discovery and runtime orchestration.
- `ExperimentRunner` for evaluation, cross-validation, and export.
- `PathCoordinator` for resolving KMDS workspace data and document paths.
- Task-aware runner support for tabular classification and regression.
- Spec discovery APIs for building validated model configurations.
- Export of champion model artifacts, feature pipeline, and metadata.

## Outcome
Users get a reproducible modeling runtime that keeps KMDS-specific workspace contracts separate from installable package logic, while still allowing easy discovery and execution from Python or CLI.
