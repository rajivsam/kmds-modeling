import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the package source directory is importable
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import pandas as pd
from kmds_modeling.core.runner import ExperimentRunner
from kmds_modeling.core.model_advisor import ModelAdvisor


class TestTaskRunners(unittest.TestCase):
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

    def test_classification_task_runner(self):
        df = pd.DataFrame({
            "record_id": list(range(10)),
            "feature_1": list(range(10)),
            "feature_2": [x * 2 for x in range(10)],
            "loan_status_r": [0, 1] * 5,
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
                "name": "classification_experiment",
                "experiment_version": "0.1.0",
                "target_variable": "loan_status_r",
                "task_type": "TABULAR_CLASSIFICATION",
            },
            "experiment_settings": {
                "cross_validation": {"splits": 5, "random_state": 42},
                "primary_metric": "roc_auc",
            },
            "candidates": [
                {
                    "name": "dummy_classifier",
                    "class_path": "kmds_modeling.examples.example_candidate.ExampleCandidate",
                    "hyperparameters": {"strategy": "prior"},
                }
            ],
            "production_target": {
                "champion_candidate_name": "dummy_classifier",
                "export_directory": "output/mlops_bundle",
            },
        }

        config_path = self._write_config(config)
        runner = ExperimentRunner(str(config_path))
        df_result = runner.run_evaluation()

        self.assertEqual(df_result.shape[0], 1)
        self.assertIn("mean_roc_auc", df_result.columns)
        self.assertIn("mean_f1", df_result.columns)
        self.assertAlmostEqual(df_result.loc[0, "mean_roc_auc"], 0.5, places=2)

    def test_regression_task_runner(self):
        df = pd.DataFrame({
            "record_id": list(range(10)),
            "feature_1": list(range(10)),
            "feature_2": [x * 2 for x in range(10)],
            "loan_status_r": [x + 2 * x for x in range(10)],
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
                "name": "regression_experiment",
                "experiment_version": "0.1.0",
                "target_variable": "loan_status_r",
                "task_type": "TABULAR_REGRESSION",
            },
            "experiment_settings": {
                "cross_validation": {"splits": 5, "random_state": 42},
                "primary_metric": "r2",
            },
            "candidates": [
                {
                    "name": "linear_regression",
                    "class_path": "sklearn.linear_model.LinearRegression",
                    "hyperparameters": {},
                }
            ],
            "production_target": {
                "champion_candidate_name": "linear_regression",
                "export_directory": "output/mlops_bundle",
            },
        }

        config_path = self._write_config(config)
        runner = ExperimentRunner(str(config_path))
        df_result = runner.run_evaluation()

        self.assertEqual(df_result.shape[0], 1)
        self.assertIn("mean_r2", df_result.columns)
        self.assertIn("mean_mae", df_result.columns)
        self.assertGreaterEqual(df_result.loc[0, "mean_r2"], 0.95)

    def test_model_advisor_requires_working_dir(self):
        config = {
            "data": {
                "index_column": "record_id",
            },
            "project": {
                "name": "advisor_experiment",
                "experiment_version": "0.1.0",
                "target_variable": "loan_status_r",
                "task_type": "TABULAR_CLASSIFICATION",
            },
        }
        config_path = self._write_config(config)

        with self.assertRaises(ValueError):
            ModelAdvisor(str(config_path))


if __name__ == "__main__":
    unittest.main()
