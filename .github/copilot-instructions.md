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

## Context engineering setup
- Use `PRODUCT.md`, `ARCHITECTURE.md`, and `CONTRIBUTING.md` to provide stable project context for AI workflows.
- Use `plan-template.md` as the standard implementation plan structure.
- Custom agents are defined in `.github/agents/plan.agent.md` and `.github/agents/implement.agent.md`.
- Prompt files are defined in `.github/prompts/plan.prompt.md` and `.github/prompts/implement.prompt.md`.

## Instructions for Copilot
- Keep runtime logic generic and workspace-agnostic.
- Do not bundle workspace `documents/` artifacts into the installed package.
- Surface package metadata for clients using runtime discovery.
