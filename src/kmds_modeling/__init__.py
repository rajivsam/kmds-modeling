"""kmds_modeling package."""

from .core.runner import ExperimentRunner
from .core.base import BaseFeatureTransformer, BaseModelCandidate
from .core.model_spec import (
    ModelGuidanceSpec,
    build_model_spec,
    get_available_guidance_templates,
    get_spec_questions,
    get_supported_task_types,
    get_strategy_options,
)
from .package_info import get_package_info, get_package_version

__version__ = get_package_version()

__all__ = [
    "ExperimentRunner",
    "BaseFeatureTransformer",
    "BaseModelCandidate",
    "ModelGuidanceSpec",
    "build_model_spec",
    "get_available_guidance_templates",
    "get_spec_questions",
    "get_supported_task_types",
    "get_strategy_options",
    "get_package_info",
    "get_package_version",
    "__version__",
]
