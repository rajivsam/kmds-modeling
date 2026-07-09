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


class TestModelSpec(unittest.TestCase):
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

    def test_build_model_spec_with_sba_requirements(self):
        df = pd.DataFrame({
            "record_id": list(range(10)),
            "feature_1": list(range(10)),
            "loan_status_r": [0, 1] * 5,
        })
        self._write_csv("model_ready_numeric_data.csv", df)

        requirements = {
            "data": {
                "working_dir": str(self.working_dir),
                "index_column": "record_id",
                "model_ready_data_file": "model_ready_numeric_data.csv",
                "featurization_output_dir": "featurization",
                "modeling_output_dir": "models",
            },
            "project": {
                "name": "sba_modeling_experiment",
                "experiment_version": "0.1.0",
                "target_variable": "loan_status_r",
                "task_type": "TABULAR_CLASSIFICATION",
                "strategy": "MAX_ACCURACY",
                "user_intent": "Imbalanced SBA loan status classification",
            },
            "experiment_settings": {
                "cross_validation": {"splits": 5, "random_state": 42},
                "primary_metric": "roc_auc",
            },
            "candidates": [
                {
                    "name": "gradient_boosting",
                    "class_path": "kmds_modeling.examples.example_candidate.ExampleCandidate",
                    "hyperparameters": {"strategy": "prior"},
                },
                {
                    "name": "random_forest",
                    "class_path": "kmds_modeling.examples.example_candidate.ExampleCandidate",
                    "hyperparameters": {"strategy": "prior"},
                },
            ],
            "production_target": {
                "champion_candidate_name": "random_forest",
                "export_directory": "output/mlops_bundle",
            },
        }

        spec = build_model_spec(
            requirements=requirements,
            guidance_templates=["tabular_classification"],
            domain_requirements="sba",
        )

        self.assertEqual(spec.config["project"]["task_type"], "TABULAR_CLASSIFICATION")
        self.assertEqual(spec.config["data"]["working_dir"], str(self.working_dir))
        self.assertIn("fit(X_train, y_train)", spec.task_contract["candidate_interface"])
        self.assertEqual(spec.config["data"]["model_ready_data_file"], "model_ready_numeric_data.csv")
        self.assertIn("documents/sba_modeling_requirements.md", spec.reference_docs)
        self.assertEqual(spec.config["production_target"]["champion_candidate_name"], "random_forest")
        self.assertIsInstance(spec.clarification_questions, list)

        output_path = self.working_dir / "model_config_built.yaml"
        spec.to_yaml(str(output_path))
        self.assertTrue(output_path.exists())

    def test_available_guidance_templates(self):
        from kmds_modeling import get_available_guidance_templates

        templates = get_available_guidance_templates()
        self.assertIn("tabular_classification", templates)
        self.assertIn("sba", templates)
