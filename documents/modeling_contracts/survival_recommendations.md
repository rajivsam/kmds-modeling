# KMDS Survival Analysis Recommendations

This document explains how to implement a KMDS-compatible `SURVIVAL_ANALYSIS` task package.

## Task Type
- `project.task_type`: `SURVIVAL_ANALYSIS`

## Required Project Fields
- `name`
- `experiment_version`
- `duration_variable`
- `event_variable`
- `task_type`
- `strategy`
- `user_intent`

## Required Data Fields
- `working_dir`
- `model_ready_data_file`
- `featurization_output_dir`
- `modeling_output_dir`

## Modeling Guidance
- Use Kaplan-Meier curves to model survival / time-to-event outcomes.
- A package like `lifelines` is recommended for fitting survival functions and generating survival plots.
- Provide `duration_variable` for event time or censoring time.
- Provide `event_variable` as a binary indicator of whether the event occurred.
- When using a candidate wrapper, support a `fit(X_train, durations, event_observed)` interface.
- Export survival function estimates and related metadata in the champion artifact bundle.

## Candidate Interface
- `fit(X_train, durations, event_observed)`
- `predict_survival_function(X) -> survival curves`

## Transformer Interface
- `fit(X_train, durations, event_observed)`
- `transform(X_val)`
- preserve DataFrame index

## Notes
- Survival analysis is censoring-aware and should not treat censored observations as negative events.
- Kaplan-Meier estimation is a strong first-choice baseline when the dataset is focused on event timing and censoring.
