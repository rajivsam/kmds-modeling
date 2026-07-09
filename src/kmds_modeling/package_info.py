from importlib.metadata import PackageNotFoundError, version
from typing import Any, Dict, List

from .core.model_spec import get_supported_task_types

PACKAGE_NAME = "kmds-modeling"
CLI_COMMANDS = ["evaluate", "export"]
ENTRY_POINTS = {
    "kmds-modeling": "kmds_modeling.cli:cli",
}
PROVIDED_PACKAGES = ["kmds_modeling"]


def get_cli_command_names() -> List[str]:
    """Return the supported kmds-modeling CLI commands."""
    return list(CLI_COMMANDS)


def get_package_version() -> str:
    """Return the installed distribution version or fall back to the declared package version."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.2.1"


def get_package_info() -> Dict[str, Any]:
    """Return package discovery metadata for clients."""
    return {
        "package_name": PACKAGE_NAME,
        "version": get_package_version(),
        "entry_points": ENTRY_POINTS,
        "cli_commands": get_cli_command_names(),
        "provided_packages": PROVIDED_PACKAGES,
        "supported_models": get_supported_task_types(),
        "documentation_note": (
            "This package does not ship embedded documents in the installed distribution. "
            "Use the repository top-level documents/ folder for onboarding and implementation guidance."
        ),
    }
