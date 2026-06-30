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
from kmds_modeling import get_package_info
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

    def test_model_advisor_classification_buckets(self):
        config = {
            "data": {
                "working_dir": str(self.working_dir),
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
        advisor = ModelAdvisor(str(config_path))

        df_mild = pd.DataFrame({
            "record_id": list(range(20)),
            "loan_status_r": [0] * 16 + [1] * 4,
        })
        profile_mild = advisor.profile_data(df_mild, target="loan_status_r")
        rec_mild = advisor.get_recommendation(profile_mild, "TABULAR_CLASSIFICATION")
        self.assertEqual(rec_mild["bucket"], 1)
        self.assertIn("Stratified", rec_mild["strategy"])

        df_moderate = pd.DataFrame({
            "record_id": list(range(50)),
            "loan_status_r": [0] * 46 + [1] * 4,
        })
        profile_moderate = advisor.profile_data(df_moderate, target="loan_status_r")
        rec_moderate = advisor.get_recommendation(profile_moderate, "TABULAR_CLASSIFICATION")
        self.assertEqual(rec_moderate["bucket"], 2)
        self.assertIn("Cost-Sensitive", rec_moderate["strategy"])

        df_extreme = pd.DataFrame({
            "record_id": list(range(101)),
            "loan_status_r": [0] * 100 + [1],
        })
        profile_extreme = advisor.profile_data(df_extreme, target="loan_status_r")
        rec_extreme = advisor.get_recommendation(profile_extreme, "TABULAR_CLASSIFICATION")
        self.assertEqual(rec_extreme["bucket"], 3)
        self.assertIn("Anomaly", rec_extreme["strategy"])

    def test_model_advisor_out_of_scope_for_high_cardinality(self):
        config = {
            "data": {
                "working_dir": str(self.working_dir),
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
        advisor = ModelAdvisor(str(config_path))

        df = pd.DataFrame({
            "record_id": list(range(25)),
            "loan_status_r": list(range(25)),
        })
        profile = advisor.profile_data(df, target="loan_status_r")
        rec = advisor.get_recommendation(profile, "TABULAR_CLASSIFICATION")
        self.assertEqual(rec["status"], "OUT_OF_SCOPE")

    def test_model_advisor_graph_and_clustering_references(self):
        config = {
            "data": {
                "working_dir": str(self.working_dir),
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
        advisor = ModelAdvisor(str(config_path))

        df = pd.DataFrame({
            "record_id": list(range(10)),
            "loan_status_r": [0, 1] * 5,
        })
        profile = advisor.profile_data(df, target="loan_status_r")

        graph_rec = advisor.get_recommendation(profile, "GRAPH_NODE_CLASSIFICATION")
        self.assertEqual(graph_rec["status"], "SUCCESS")
        self.assertIn("graph_modeling", graph_rec["reference"])

        clustering_rec = advisor.get_recommendation(profile, "CLUSTERING")
        self.assertEqual(clustering_rec["status"], "SUCCESS")
        self.assertIn("clustering_recommendations", clustering_rec["reference"])

    def test_model_advisor_storage_path_uses_modeling_contracts(self):
        config = {
            "data": {
                "working_dir": str(self.working_dir),
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
        advisor = ModelAdvisor(str(config_path))

        path = advisor.recommendation_storage_path()
        self.assertTrue(path.endswith("documents/modeling_contracts"))

    def test_get_package_info_returns_metadata(self):
        info = get_package_info()
        self.assertIsInstance(info, dict)
        self.assertEqual(info.get("package_name"), "kmds-modeling")
        self.assertIn("version", info)
        self.assertIn("entry_points", info)
        self.assertIn("cli_commands", info)
        self.assertIn("provided_packages", info)


if __name__ == "__main__":
    unittest.main()
