# Assistant Instructions for OKF / Google Code Assistant

This file is intended to be copied directly into Google Code Assistant or a similar implementation agent.

## Objective

Implement the core `kmds-modeling` package runtime and CLI. Follow the existing repository structure and keep the current tabular modeling workflow intact, while isolating graph and clustering runtime paths for future work.

## Tasks

1. Implement abstract interfaces in `src/kmds_modeling/core/base.py`.
2. Implement `ExperimentRunner` in `src/kmds_modeling/core/runner.py`.
3. Implement CLI entry points in `src/kmds_modeling/cli.py`.
4. Preserve `record_id` indices across feature transform operations.
5. Avoid train/validation leakage in transformers.
6. Make `project.task_type`, `user_intent`, `entities`, and `strategy` available in the config contract.

## Expected Output

- Working package under `src/kmds_modeling/`
- CLI commands: `evaluate` and `export`
- Runtime support for `TABULAR_CLASSIFICATION` and `TABULAR_REGRESSION`
- Document guidance for the OKF / Google workflow in this `documents/okf/` directory

## Notes

- Do not alter the existing documents outside the OKF support folder unless necessary.
- Keep the OKF docs separate from package runtime documentation.
- Provide any caveats in a follow-up note if path support is incomplete.
