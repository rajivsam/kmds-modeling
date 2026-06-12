#!/usr/bin/env python3
"""Validate kmds-modeling path coordinator and output directories."""

import argparse
from pathlib import Path

from kmds_modeling.core.notebook_utils import build_notebook_resolver, get_modeling_artifact_paths


def main():
    parser = argparse.ArgumentParser(description="Validate kmds-modeling workspace paths and outputs.")
    parser.add_argument(
        "--working-dir",
        default=".",
        help="KMDS workspace working directory containing modeling_config.yaml",
    )
    parser.add_argument(
        "--config",
        default="model_config.yaml",
        help="Modeling configuration file relative to working directory.",
    )
    args = parser.parse_args()

    working_dir = Path(args.working_dir).resolve()
    config_path = working_dir / args.config

    print(f"Working directory: {working_dir}")
    print(f"Config file: {config_path}")

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    resolver = build_notebook_resolver(str(working_dir), config_name=args.config)
    paths = get_modeling_artifact_paths(resolver)

    print("\nResolved artifact paths:")
    for name, path in paths.items():
        print(f"- {name}: {path}")

    print("\nExistence checks:")
    for name, path in paths.items():
        exists = Path(path).exists()
        print(f"- {name}: {'FOUND' if exists else 'MISSING'}")

    print("\nThe modeling output directory should be under working_dir/models by default.")
    print(f"modeling_output_path: {resolver.modeling_output_path}")
    assert resolver.modeling_output_path.endswith("models"), "modeling_output_path should end with 'models'"

    print("\nValidation complete.")


if __name__ == "__main__":
    main()
