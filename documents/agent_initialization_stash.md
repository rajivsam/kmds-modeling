# KMDS Modeling Agent Initialization Stash

## Initialize from stash and stand by for your task.

### Current repository state
- A `src/kmds_modeling` package is implemented with a `core.runner.ExperimentRunner`.
- `main.py` is the CLI entry point with `evaluate` and `export` commands.
- `ExperimentRunner` provides config-driven evaluation, cross-validation, and champion export logic.
- `documents/` contains design docs and this initialization stash.
- The module is intended for KMDS-specific modeling and depends on `dd-parser-cleaner` and `kmds-featurization` outputs.

### What to read first
1. `documents/kmds_project_structure.md`
2. `documents/kmds-modeling-high-level-design.md`
3. `documents/code_assistant_insructions.md`
4. `documents/project_organization.md`
5. `main.py`
6. `src/kmds_modeling/core/runner.py`

### Core task context
- Build a simple, consistent KMDS modeling package.
- Preserve `record_id` index through transformations.
- Enforce no leakage via fold-specific transformer training.
- Support any model through a uniform candidate wrapper interface.
- Depend on upstream KMDS tool outputs, not on raw data ingestion logic.

### What the agent should do next
- Confirm package import and runtime layout.
- Implement the minimal feature wrapper and candidate wrapper patterns.
- Add a working example config or sample data contract.
- Keep the implementation aligned with KMDS project design, not general-purpose ML.

### Trigger
When you see: `: Initialize from stash and stand by for your task` — use this file as the starting context and begin implementing the next coding task.
