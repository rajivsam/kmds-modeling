import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import pandas as pd
from kmds_modeling import build_model_spec
from kmds_modeling.core.runner import ExperimentRunner


class TestSurvivalTask(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.working_dir = Path(self.temp_dir.name)
        (self.working_dir / "data" / "featurization").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_csv(self, filename: str, df: pd.DataFrame):
        path = self.working_dir / "data" / "featurization" / filename
        df.to_csv(path, index=False)
        return path

    def _write_config(self, config: dict):
        config_path = self.working_dir / "model_config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            import yaml

            yaml.safe_dump(config, f)
        return config_path

    def test_survival_runner_not_implemented(self):
        df = pd.DataFrame({
            "record_id": list(range(10)),
            "feature_1": list(range(10)),
            "time_to_event": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            "event_occurred": [1, 0, 1, 1, 0, 1, 1, 0, 1, 0],
        })
        self._write_csv("model_ready_numeric_data.csv", df)

        config = {
            "data": {
                "working_dir": str(self.working_dir),
                "index_column": "record_id",
                "model_ready_data_file": "model_ready_numeric_data.csv",
                "featurization_output_dir": "featurization",
                "modeling_output_dir": "models",
            },
            "project": {
                "name": "survival_experiment",
                "experiment_version": "0.1.0",
                "task_type": "SURVIVAL_ANALYSIS",
                "duration_variable": "time_to_event",
                "event_variable": "event_occurred",
            },
            "experiment_settings": {
                "cross_validation": {"splits": 2, "random_state": 42},
                "primary_metric": "concordance_index",
            },
            "candidates": [],
            "production_target": {
                "champion_candidate_name": "dummy_survival",
                "export_directory": "output/mlops_bundle",
            },
        }

        config_path = self._write_config(config)
        runner = ExperimentRunner(str(config_path))

        with self.assertRaises(NotImplementedError):
            runner.run_evaluation()

        with self.assertRaises(NotImplementedError):
            runner.export_champion()

    def test_build_survival_model_spec(self):
        requirements = {
            "project": {
                "name": "survival_experiment",
                "experiment_version": "0.1.0",
                "task_type": "SURVIVAL_ANALYSIS",
                "strategy": "MAX_SURVIVAL_INSIGHT",
                "user_intent": "Model time-to-event outcomes with survival curves.",
                "duration_variable": "time_to_event",
                "event_variable": "event_occurred",
            },
            "data": {
                "working_dir": str(self.working_dir),
            },
            "candidates": [],
            "production_target": {},
        }

        spec = build_model_spec(requirements=requirements, guidance_templates=["survival_analysis"])
        self.assertEqual(spec.config["project"]["task_type"], "SURVIVAL_ANALYSIS")
        self.assertIn("documents/modeling_contracts/survival_recommendations.md", spec.reference_docs)
        self.assertIn("lifelines", " ".join(spec.guidance["details"]))


if __name__ == "__main__":
    unittest.main()
