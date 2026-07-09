import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from kmds_modeling import get_spec_questions, get_supported_task_types, get_strategy_options


class TestModelSpecInteractive(unittest.TestCase):
    def test_spec_questions_initial(self):
        requirements = {"data": {"working_dir": "."}, "project": {}, "candidates": [], "production_target": {}}
        questions = get_spec_questions(requirements)

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["field"], "project.task_type")
        self.assertEqual(questions[0]["options"], get_supported_task_types())

    def test_spec_questions_after_task_type(self):
        requirements = {"data": {"working_dir": "."}, "project": {"task_type": "TABULAR_CLASSIFICATION"}, "candidates": [], "production_target": {}}
        questions = get_spec_questions(requirements)

        self.assertTrue(any(q["field"] == "project.strategy" for q in questions))
        self.assertEqual(get_strategy_options("TABULAR_CLASSIFICATION"), ["MAX_ACCURACY", "HIGH_INTERPRETABILITY"])

    def test_spec_questions_with_complete_project(self):
        requirements = {
            "data": {"working_dir": "."},
            "project": {
                "task_type": "TABULAR_CLASSIFICATION",
                "strategy": "MAX_ACCURACY",
                "target_variable": "loan_status_r",
                "user_intent": "Imbalanced SBA loan status classification",
                "name": "sba_experiment",
            },
            "candidates": [
                {"name": "dummy", "class_path": "kmds_modeling.examples.example_candidate.ExampleCandidate", "hyperparameters": {"strategy": "prior"}}
            ],
            "production_target": {"champion_candidate_name": "dummy", "export_directory": "output/mlops_bundle"},
        }
        questions = get_spec_questions(requirements)

        self.assertEqual(questions, [])
