import json
import os
from typing import Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

from .task_base import BaseTaskRunner


class ClassificationTaskRunner(BaseTaskRunner):
    def _build_cv(self):
        cv_cfg = self.config["experiment_settings"]["cross_validation"]
        return StratifiedKFold(
            n_splits=cv_cfg["splits"],
            shuffle=True,
            random_state=cv_cfg["random_state"],
        )

    def _extract_positive_probs(self, raw_preds: np.ndarray) -> np.ndarray:
        if raw_preds.ndim == 1:
            return raw_preds
        if raw_preds.shape[1] == 2:
            return raw_preds[:, 1]
        return raw_preds[:, -1]

    def run_evaluation(self) -> pd.DataFrame:
        cv = self._build_cv()
        leaderboard = []

        for model_cfg in self.config["candidates"]:
            candidate_class = self._get_candidate_class(model_cfg["class_path"])
            fold_auc, fold_f1 = [], []

            for train_idx, val_idx in cv.split(self.X, self.y):
                X_train, X_val = self.X.iloc[train_idx], self.X.iloc[val_idx]
                y_train, y_val = self.y.iloc[train_idx], self.y.iloc[val_idx]

                X_tr_fe, X_val_fe = self._apply_transformers(X_train, X_val, y_train)

                model = self._instantiate_candidate(candidate_class, model_cfg["hyperparameters"])
                model.fit(X_tr_fe, y_train)

                preds = model.predict_proba(X_val_fe)
                probability = self._extract_positive_probs(preds)

                fold_auc.append(roc_auc_score(y_val, probability))
                fold_f1.append(f1_score(y_val, (probability >= 0.5).astype(int)))

            leaderboard.append(
                {
                    "candidate_name": model_cfg["name"],
                    "mean_roc_auc": float(np.mean(fold_auc)),
                    "mean_f1": float(np.mean(fold_f1)),
                }
            )

        return pd.DataFrame(leaderboard)

    def export_champion(self):
        prod_cfg = self.config["production_target"]
        champ_name = prod_cfg["champion_candidate_name"]
        model_cfg = next(c for c in self.config["candidates"] if c["name"] == champ_name)

        X_final = self.X.copy()
        for trans in self.custom_transformers:
            X_final = trans.fit_transform(X_final, self.y)

        candidate_class = self._get_candidate_class(model_cfg["class_path"])
        model = candidate_class(model_cfg["hyperparameters"])
        model.fit(X_final, self.y)

        out_dir = prod_cfg["export_directory"]
        os.makedirs(out_dir, exist_ok=True)

        joblib.dump(model, os.path.join(out_dir, "model_weights.pkl"))
        joblib.dump(self.custom_transformers, os.path.join(out_dir, "feature_pipeline.pkl"))

        metadata = {
            "model_name": self.config["project"]["name"],
            "version": self.config["project"]["experiment_version"],
            "features": list(X_final.columns),
            "target": self.config["project"]["target_variable"],
            "metrics": {"primary_metric": self.config["experiment_settings"]["primary_metric"]},
        }
        with open(os.path.join(out_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=4)
