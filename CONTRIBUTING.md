# Contributing to KMDS Modeling

## Get started
- Use the repository Python environment from the project root.
- Install dependencies into the active environment with `pip install -e .` if needed.
- Run tests with `pytest` from the repository root.

## Project conventions
- Keep installable package logic inside `src/kmds_modeling/`.
- Keep workspace-specific documentation, examples, and advisory artifacts under `documents/` or `notebooks/`.
- Do not add workspace documents into the package source tree.
- Preserve the existing path resolution contract in `PathCoordinator`.

## Code and docs
- Update `README.md`, `USER_GUIDE.md`, and `PRODUCT.md` when adding new runtime behavior.
- Add or revise architecture details in `ARCHITECTURE.md` for any structural changes.
- Keep `.github/copilot-instructions.md` aligned with new agent workflows and project context.
- Use `plan-template.md` and `.github/agents/*.agent.md` when introducing new feature planning or implementation workflows.

## Testing
- Add targeted tests in `tests/` for new runtime or candidate behavior.
- Keep tests small and focused.
- Run the full suite after substantial changes.

## Issue tracking and review
- This repository includes repository-level issue guidance. See `AGENTS.md` for issue tracker conventions.
- Use git branches for feature work and keep context-engineering files under version control.

## AI and context workflow
- This repo uses `.github/copilot-instructions.md` to provide AI agents with repository context.
- Keep context artifacts up to date when architectural assumptions or documentation change.
