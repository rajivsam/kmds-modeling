# Google Code Assistant Template for KMDS Modeling

Use this file as the prompt input for Google Code Assistant when generating implementation code.

## Instructions

You are an expert machine learning platform engineer. Your task is to implement the core package structure and runtime engine for the `kmds-modeling` project, following the repository conventions and governance features.

### What to generate

- `src/kmds_modeling/core/base.py`
- `src/kmds_modeling/core/runner.py`
- `src/kmds_modeling/cli.py`
- Any additional support modules needed to satisfy core runtime behavior and package export.

### Required behavior

1. Preserve dataset index values across all feature transformation and evaluation steps.
2. Enforce training/validation leakage prevention in transformer workflows.
3. Support modular candidate classes via a wrapper API that can accept external model frameworks.
4. Use `model_config.yaml` for project metadata and runtime dispatch.
5. Support `TABULAR_CLASSIFICATION` and `TABULAR_REGRESSION` as runtime task types.

### Example goals

- Evaluation loop with cross-validation that evaluates multiple candidate classes.
- Export of champion model artifacts and feature pipeline metadata.
- CLI with `evaluate` and `export` commands.

### Deliverables

- Implementation files under `src/kmds_modeling/`
- Any docs needed to support a Google-driven implementation workflow
- A clear note if any required runtime paths are not yet implemented in the current package

## Notes

- The package is intended to be installed from `src/`.
- The workspace currently includes a `documents/` folder for governance and modeling recommendations.
- The runtime architecture should keep graph and clustering paths isolated until they are fully implemented.

---

Save this file as-is and use it to prompt Google Code Assistant for code generation.
