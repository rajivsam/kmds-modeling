# KMDS Modeling Repository Context

## Purpose
This repo provides a KMDS modeling runtime package that evaluates candidate models, exports champion artifacts, and resolves KMDS workspace paths.

## Package discovery
- The installable package is `kmds-modeling`.
- Users should import the public API from `kmds_modeling`.
- For metadata discovery, use `importlib.metadata` or `importlib.metadata.version`.

## CLI workflows
- `kmds-modeling evaluate --config /path/to/model_config.yaml`
- `kmds-modeling export --config /path/to/model_config.yaml`

## Relevant source files
- `src/kmds_modeling/__init__.py`
- `src/kmds_modeling/cli.py`
- `src/kmds_modeling/core/runner.py`
- `src/kmds_modeling/core/path_coordinator.py`

## Instructions for Copilot
- Keep runtime logic generic and workspace-agnostic.
- Do not bundle workspace `documents/` artifacts into the installed package.
- Surface package metadata for clients using runtime discovery.
