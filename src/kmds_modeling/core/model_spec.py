import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml


DEFAULT_EXPERIMENT_SETTINGS = {
    "cross_validation": {"splits": 5, "random_state": 42},
    "primary_metric": "roc_auc",
}

DEFAULT_PRODUCTION_TARGET = {
    "export_directory": "output/mlops_bundle",
}

TASK_CONTRACTS = {
    "TABULAR_CLASSIFICATION": {
        "task_type": "TABULAR_CLASSIFICATION",
        "required_project_fields": [
            "name",
            "experiment_version",
            "target_variable",
            "task_type",
            "strategy",
            "user_intent",
        ],
        "required_data_fields": [
            "working_dir",
            "model_ready_data_file",
            "featurization_output_dir",
            "modeling_output_dir",
        ],
        "candidate_interface": [
            "fit(X_train, y_train)",
            "predict_proba(X) -> np.ndarray",
        ],
        "transformer_interface": [
            "fit(X_train, y_train)",
            "transform(X_val)",
            "preserve DataFrame index",
        ],
    },
    "TABULAR_REGRESSION": {
        "task_type": "TABULAR_REGRESSION",
        "required_project_fields": [
            "name",
            "experiment_version",
            "target_variable",
            "task_type",
            "strategy",
            "user_intent",
        ],
        "required_data_fields": [
            "working_dir",
            "model_ready_data_file",
            "featurization_output_dir",
            "modeling_output_dir",
        ],
        "candidate_interface": [
            "fit(X_train, y_train)",
            "predict(X) -> np.ndarray",
        ],
        "transformer_interface": [
            "fit(X_train, y_train)",
            "transform(X_val)",
            "preserve DataFrame index",
        ],
    },
    "SURVIVAL_ANALYSIS": {
        "task_type": "SURVIVAL_ANALYSIS",
        "required_project_fields": [
            "name",
            "experiment_version",
            "duration_variable",
            "event_variable",
            "task_type",
            "strategy",
            "user_intent",
        ],
        "required_data_fields": [
            "working_dir",
            "model_ready_data_file",
            "featurization_output_dir",
            "modeling_output_dir",
        ],
        "candidate_interface": [
            "fit(X_train, durations, event_observed)",
            "predict_survival_function(X) -> survival curves",
        ],
        "transformer_interface": [
            "fit(X_train, durations, event_observed)",
            "transform(X_val)",
            "preserve DataFrame index",
        ],
    },
}

GUIDANCE_TEMPLATES = {
    "tabular_classification": {
        "summary": "Use stratified cross-validation, candidate wrappers with predict_proba, and serialize model_weights, feature_pipeline, and metadata.",
        "details": [
            "Use `project.task_type = TABULAR_CLASSIFICATION`.",
            "Candidates must implement `fit(X_train, y_train)` and `predict_proba(X)`.",
            "Return positive-class probabilities from the last column or a one-dimensional score array.",
            "Export the champion model using `model_weights.pkl`, `feature_pipeline.pkl`, and `metadata.json`.",
        ],
        "reference_doc": "documents/modeling_contracts/tabular_classification_recommendations.md",
    },
    "sba": {
        "summary": "For SBA modeling, derive geographic cluster distance features, calibrate probabilities, and tune a ROC threshold for export.",
        "details": [
            "Learn good/bad geographic cluster structure using training-set geography only.",
            "Prefer spectral clustering and fall back to HDBSCAN when spectral clustering is not viable.",
            "Derive only two distance features: `hdgc` and `hdbc`.",
            "Calibrate candidate probability outputs with isotonic regression.",
            "Use ROC-based threshold tuning and export both probability and binary decision outputs.",
        ],
        "reference_doc": "documents/sba_modeling_requirements.md",
    },
    "survival_analysis": {
        "summary": "Use Kaplan-Meier survival curves and a survival analysis library such as lifelines to model time-to-event outcomes.",
        "details": [
            "Use `project.task_type = SURVIVAL_ANALYSIS`.",
            "Provide `project.duration_variable` and `project.event_variable` for censoring-aware modeling.",
            "Fit Kaplan-Meier curves using a package like `lifelines` to estimate survival functions.",
            "Generate survival plots and export survival function estimates as part of the champion workflow.",
        ],
        "reference_doc": "documents/modeling_contracts/survival_recommendations.md",
    },
}

STRATEGY_OPTIONS = {
    "TABULAR_CLASSIFICATION": ["MAX_ACCURACY", "HIGH_INTERPRETABILITY"],
    "TABULAR_REGRESSION": ["MAX_ACCURACY", "HIGH_INTERPRETABILITY"],
    "SURVIVAL_ANALYSIS": ["MAX_SURVIVAL_INSIGHT", "HIGH_INTERPRETABILITY"],
}


def get_supported_task_types() -> List[str]:
    return list(TASK_CONTRACTS.keys())


def get_strategy_options(task_type: str) -> List[str]:
    return STRATEGY_OPTIONS.get(task_type, [])


def get_spec_questions(requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    questions: List[Dict[str, Any]] = []
    project_cfg = requirements.get("project", {})

    if not project_cfg.get("task_type"):
        questions.append(
            {
                "field": "project.task_type",
                "question": "Select the KMDS modeling task type.",
                "options": get_supported_task_types(),
                "note": "This determines the runtime task runner and supported strategy options.",
            }
        )
        return questions

    if not project_cfg.get("strategy"):
        questions.append(
            {
                "field": "project.strategy",
                "question": f"Choose the modeling strategy for {project_cfg['task_type']}",
                "options": get_strategy_options(project_cfg["task_type"]),
                "note": "Strategy options depend on the selected task type.",
            }
        )

    if project_cfg.get("task_type") == "SURVIVAL_ANALYSIS":
        if not project_cfg.get("duration_variable"):
            questions.append(
                {
                    "field": "project.duration_variable",
                    "question": "What is the duration/time-to-event variable column name?",
                    "note": "This field captures the survival time or censoring duration.",
                }
            )
        if not project_cfg.get("event_variable"):
            questions.append(
                {
                    "field": "project.event_variable",
                    "question": "What is the event-observed indicator column name?",
                    "note": "This boolean or binary field indicates whether the event of interest occurred.",
                }
            )
    elif not project_cfg.get("target_variable"):
        questions.append(
            {
                "field": "project.target_variable",
                "question": "What is the target variable column name?",
                "note": "This is the label the model will predict.",
            }
        )

    if not project_cfg.get("user_intent"):
        questions.append(
            {
                "field": "project.user_intent",
                "question": "Describe the modeling objective in one sentence.",
                "note": "This should capture the business or prediction intent.",
            }
        )

    if not project_cfg.get("name"):
        questions.append(
            {
                "field": "project.name",
                "question": "Provide a name for this modeling experiment.",
                "note": "This is used in metadata and export naming.",
            }
        )

    candidates = requirements.get("candidates")
    if not candidates:
        questions.append(
            {
                "field": "candidates",
                "question": "Provide one or more candidate model definitions with `name`, `class_path`, and `hyperparameters`.",
                "note": "Candidate classes can be custom wrappers or importable sklearn-like estimators.",
            }
        )

    production_target = requirements.get("production_target", {})
    if not production_target.get("champion_candidate_name"):
        questions.append(
            {
                "field": "production_target.champion_candidate_name",
                "question": "Which candidate should be exported as the production champion?",
                "note": "This should match one of the candidate names you provided.",
            }
        )

    if not production_target.get("export_directory"):
        questions.append(
            {
                "field": "production_target.export_directory",
                "question": "Where should the champion artifacts be exported?",
                "note": "This is the path to the ML-Ops artifact bundle.",
            }
        )

    return questions


@dataclass
class ModelGuidanceSpec:
    config: Dict[str, Any]
    task_contract: Dict[str, Any]
    guidance: Dict[str, Any]
    reference_docs: List[str] = field(default_factory=list)
    clarification_questions: List[str] = field(default_factory=list)

    def to_yaml(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f, sort_keys=False)

    def summary(self) -> Dict[str, Any]:
        return {
            "task_contract": self.task_contract,
            "guidance": self.guidance,
            "reference_docs": self.reference_docs,
            "clarification_questions": self.clarification_questions,
        }


def _build_default_config(requirements: Dict[str, Any]) -> Dict[str, Any]:
    config = {
        "data": {},
        "project": {},
        "experiment_settings": {},
        "candidates": [],
        "production_target": {},
    }
    for key in ["data", "project", "experiment_settings", "candidates", "production_target"]:
        if key in requirements and requirements[key] is not None:
            config[key] = requirements[key]
    if "config" in requirements and isinstance(requirements["config"], dict):
        config = {**config, **requirements["config"]}
    data_cfg = config.get("data", {})
    data_cfg.setdefault("model_ready_data_file", "model_ready_numeric_data.csv")
    data_cfg.setdefault("featurization_output_dir", "featurization")
    data_cfg.setdefault("modeling_output_dir", "models")
    config["data"] = data_cfg

    project_cfg = config.get("project", {})
    project_cfg.setdefault("experiment_version", project_cfg.get("experiment_version", "0.1.0"))
    config["project"] = project_cfg

    exp_cfg = config.get("experiment_settings", {})
    exp_cfg = {**DEFAULT_EXPERIMENT_SETTINGS, **exp_cfg}
    config["experiment_settings"] = exp_cfg

    production_cfg = config.get("production_target", {})
    production_cfg.setdefault("export_directory", DEFAULT_PRODUCTION_TARGET["export_directory"])
    config["production_target"] = production_cfg

    return config


def _build_clarification_questions(config: Dict[str, Any], task_contract: Dict[str, Any]) -> List[str]:
    questions: List[str] = []
    if not config["candidates"]:
        questions.append("Provide candidate model definitions with `class_path` and `hyperparameters`.")
    if not config["production_target"].get("champion_candidate_name"):
        questions.append("Select which candidate should be exported as the production champion.")
    if task_contract["task_type"] == "TABULAR_CLASSIFICATION":
        if config["experiment_settings"].get("primary_metric") is None:
            questions.append("Confirm the primary metric for classification evaluation (for example, roc_auc).")
    if task_contract["task_type"] == "SURVIVAL_ANALYSIS":
        if config["project"].get("duration_variable") is None:
            questions.append("Provide the duration/time-to-event variable for survival analysis.")
        if config["project"].get("event_variable") is None:
            questions.append("Provide the event-observed indicator variable for survival analysis.")
        if config["experiment_settings"].get("primary_metric") is None:
            questions.append("Confirm the primary survival metric (for example, concordance_index).")
    return questions


def _resolve_guidance_templates(
    task_type: str,
    templates: Optional[List[str]] = None,
    domain_requirements: Optional[str] = None,
) -> List[Dict[str, Any]]:
    resolved: List[Dict[str, Any]] = []
    if templates:
        for tmpl in templates:
            key = tmpl.lower()
            if key in GUIDANCE_TEMPLATES:
                resolved.append(GUIDANCE_TEMPLATES[key])
    if domain_requirements:
        key = domain_requirements.lower()
        if key in GUIDANCE_TEMPLATES and GUIDANCE_TEMPLATES[key] not in resolved:
            resolved.append(GUIDANCE_TEMPLATES[key])
        elif "sba" in key and GUIDANCE_TEMPLATES["sba"] not in resolved:
            resolved.append(GUIDANCE_TEMPLATES["sba"])
    if not resolved and task_type == "TABULAR_CLASSIFICATION":
        resolved.append(GUIDANCE_TEMPLATES["tabular_classification"])
    return resolved


def build_model_spec(
    requirements: Dict[str, Any],
    guidance_templates: Optional[List[str]] = None,
    domain_requirements: Optional[str] = None,
) -> ModelGuidanceSpec:
    config = _build_default_config(requirements)
    task_type = config["project"].get("task_type")
    if not task_type:
        raise ValueError("project.task_type is required to build a model spec.")
    task_contract = TASK_CONTRACTS.get(task_type)
    if task_contract is None:
        raise ValueError(f"Unsupported task_type: {task_type}")

    guidance_items = _resolve_guidance_templates(task_type, guidance_templates, domain_requirements)
    reference_docs = [item["reference_doc"] for item in guidance_items if "reference_doc" in item]
    guidance = {
        "task_summary": guidance_items[0]["summary"] if guidance_items else "No guidance available.",
        "details": [detail for item in guidance_items for detail in item.get("details", [])],
    }
    clarification_questions = _build_clarification_questions(config, task_contract)

    return ModelGuidanceSpec(
        config=config,
        task_contract=task_contract,
        guidance=guidance,
        reference_docs=reference_docs,
        clarification_questions=clarification_questions,
    )


def get_available_guidance_templates() -> List[str]:
    return list(GUIDANCE_TEMPLATES.keys())
