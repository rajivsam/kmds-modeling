# Client Discovery of Package Services

This document describes the runtime discovery and spec-building workflow for `kmds-modeling` package clients.

## Goal

Provide a package-level API that allows clients to:

1. discover package services and available CLI commands,
2. build a validated `model_config.yaml` from a minimal modeling spec,
3. receive embedded task guidance based on existing KMDS modeling contracts,
4. iterate with the data scientist on guidance and spec choices.

## Desired Developer Workflow

### Step 1: Discover the package

The client calls `get_package_info()` to learn:

- package name
- version
- CLI entry points
- provided package modules
- documentation note

This is the discovery phase. It confirms the package can run modeling evaluation and export.

### Step 2: Build a model spec

The client calls `build_model_spec()` with a minimal runtime spec plus guidance hints.

Required inputs include:

- `data.working_dir`
- `project.name`
- `project.experiment_version`
- `project.target_variable`
- `project.task_type`
- `project.strategy`
- `project.user_intent`
- `candidates` list with `name`, `class_path`, `hyperparameters`
- `production_target.champion_candidate_name`
- `production_target.export_directory`

The data file and featurization paths can be derived from notebook utilities or defaulted by the package. This keeps the interactive requirements focused on the task, target, strategy, and candidate choices.

Optional guidance inputs include:

- `guidance_templates` such as `tabular_classification`
- `domain_requirements` such as `sba`

The API returns:

- generated config payload for `model_config.yaml`
- task contract requirements
- guidance summary and details
- reference document links
- clarification questions for the data scientist

### Step 3: Review and iterate

The client reviews the returned guidance and can:

- accept the guidance and finalize the spec,
- provide an updated spec to refine the configuration,
- ask for explicit handling of domain-specific requirements.

This lets an orchestrator or agent complete one iteration with a closed loop.

### Step 4: Execute the model pipeline

After the spec is accepted, the client writes `model_config.yaml` and runs:

- `kmds-modeling evaluate --config /path/to/model_config.yaml`
- `kmds-modeling export --config /path/to/model_config.yaml`

### Interactive requirement collection

This package supports an interactive question workflow for the remaining runtime requirements.

The client can call `get_spec_questions(requirements)` to receive a list of missing fields, with task-type options and task-specific strategy choices:

- If `project.task_type` is missing, the API returns supported task types.
- Once a task type is selected, the API returns the strategy options tied to that task.
- Remaining questions gather `project.target_variable`, `project.user_intent`, `project.name`, `candidates`, and production export details.

This lets the user provide answers incrementally and keeps the initial payload minimal.

## API Contract

### `get_package_info()`

Returns discovery metadata only. Example:

```python
from kmds_modeling import get_package_info
info = get_package_info()
```

### `build_model_spec(requirements, guidance_templates=None, domain_requirements=None)`

Builds a runnable model configuration and embeds task guidance.

Returns a `ModelGuidanceSpec` object with:

- `config`
- `task_contract`
- `guidance`
- `reference_docs`
- `clarification_questions`

Example:

```python
from kmds_modeling import build_model_spec
spec = build_model_spec(
    requirements={...},
    guidance_templates=["tabular_classification"],
    domain_requirements="sba",
)
spec.to_yaml("model_config.yaml")
print(spec.summary())
```

### `get_available_guidance_templates()`

Returns the names of supported guidance templates.

## Guidance Folding

The new API merges runtime contract and document-based guidance.

Supported guidance templates include:

- `tabular_classification`
- `sba`

The API also resolves reference documents such as:

- `documents/modeling_contracts/tabular_classification_recommendations.md`
- `documents/sba_modeling_requirements.md`

## Test Case

A unit test validates that the API can:

- generate a spec from a minimal SBA-style requirements payload,
- include the classification task contract,
- attach the SBA guidance references,
- write a `model_config.yaml` file successfully.

## User-facing flow

1. call `get_package_info()`
2. call `build_model_spec()` with a spec attachment or notebook payload
3. review returned guidance
4. accept guidance or update spec
5. write the final config
6. run evaluation and export
