# KMDS Modeling Recommendations

## Purpose
This document captures the current recommended approach for the KMDS modeling package given the agreed constraints:
- Keep governance as a separate advisory module
- Support only `TABULAR_CLASSIFICATION` in this iteration
- Create a dedicated recommendations folder for future modeling guidance

## Recommended Architecture

1. Keep `documents/advisor.py` as the governance/advisory module.
2. Store runtime modeling recommendations inside the KMDS workspace at `working_dir/documents/modeling_recommendations` rather than inside the package source tree.
   - It should remain separate from `src/kmds_modeling` runtime logic.
   - This supports the desired split between advisory guidance and production modeling execution.

2. In this iteration, the package runtime should enforce a strict scope check for task intent.
   - Accept only `TABULAR_CLASSIFICATION`.
   - If the config or advisory metadata requests any other intent, fail fast with a clear out-of-scope notice.

3. Maintain classification-only evaluation semantics in `ExperimentRunner`.
   - Continue using `predict_proba(...)[ :, 1]` and classification metrics like ROC AUC and F1.
   - Preserve index and leakage prevention behavior exactly as implemented today.

## Current Advisory Workflow

The recommended governance flow is:
1. User provides structured metadata and sample dataset information.
2. `documents/advisor.py` profiles the dataset and returns a recommendation.
3. The package runtime consults the advisory module only to validate scope.
4. If the advisory response is successful for `TABULAR_CLASSIFICATION`, proceed with model evaluation.

### Valid advisory outputs for this iteration
- `SUCCESS` for `TABULAR_CLASSIFICATION` with imbalance bucket guidance.
- `OUT_OF_SCOPE` for any other task intent.
- `AMBIGUOUS` if multiple entity mappings indicate a graph-aware task, which is not supported now.

## Recommended Runtime Behavior

- Do not serialize governance recommendations into exported artifacts at this time.
- Use governance only as a pre-flight check before evaluation.
- Keep the engine simple and limited to the current classification use case.

## Next Iteration

The next modeling iteration should target clustering support.
Recommended preparation steps:
- Keep the advisory module extensible for `CLUSTERING`.
- Design the runtime contract so that new task intents can be added later without changing the core model execution engine dramatically.
- Keep the classification path isolated so it remains stable while clustering is developed separately.
