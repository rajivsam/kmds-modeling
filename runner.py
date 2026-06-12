import yaml
import importlib
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, f1_score

class ExperimentRunner:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.custom_transformers = []
        self._load_data()

    def _load_data(self):
        data_cfg = self.config["data"]
        df = pd.read_csv(data_cfg["input_csv"])
        df.set_index(data_cfg["index_column"], inplace=True)
        
        target = self.config["project"]["target_variable"]
        self.y = df[target]
        self.X = df.drop(columns=[target])

    def register_transformer(self, transformer):
        """Allows the data scientist to inject custom feature transformation pipelines."""
        self.custom_transformers.append(transformer)

    def _apply_transformers(self, X_train: pd.DataFrame, X_val: pd.DataFrame, y_train: pd.Series):
        X_tr_fe = X_train.copy()
        X_val_fe = X_val.copy()
        for trans in self.custom_transformers:
            X_tr_fe = trans.fit_transform(X_tr_fe, y_train)
            X_val_fe = trans.transform(X_val_fe)
        return X_tr_fe, X_val_fe

    def _get_candidate_class(self, class_path: str):
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def run_evaluation(self) -> pd.DataFrame:
        cv_cfg = self.config["experiment_settings"]["cross_validation"]
        skf = StratifiedKFold(n_splits=cv_cfg["splits"], shuffle=True, random_state=cv_cfg["random_state"])
        
        leaderboard = []

        for model_cfg in self.config["candidates"]:
            candidate_class = self._get_candidate_class(model_cfg["class_path"])
            fold_auc, fold_f1 = [], []

            for train_idx, val_idx in skf.split(self.X, self.y):
                X_train, X_val = self.X.iloc[train_idx], self.X.iloc[val_idx]
                y_train, y_val = self.y.iloc[train_idx], self.y.iloc[val_idx]

                X_tr_fe, X_val_fe = self._apply_transformers(X_train, X_val, y_train)

                model = candidate_class(model_cfg["hyperparameters"])
                model.fit(X_tr_fe, y_train)
                
                preds = model.predict_proba(X_val_fe)[:, 1]
                fold_auc.append(roc_auc_score(y_val, preds))
                fold_f1.append(f1_score(y_val, (preds >= 0.5).astype(int)))

            leaderboard.append({
                "candidate_name": model_cfg["name"],
                "mean_roc_auc": np.mean(fold_auc),
                "mean_f1": np.mean(fold_f1)
            })

        return pd.DataFrame(leaderboard)

    def export_champion(self):
        prod_cfg = self.config["production_target"]
        champ_name = prod_cfg["champion_candidate_name"]
        model_cfg = next(c for c in self.config["candidates"] if c["name"] == champ_name)
        
        # Process complete dataset
        X_final = self.X.copy()
        for trans in self.custom_transformers:
            X_final = trans.fit_transform(X_final, self.y)
            
        candidate_class = self._get_candidate_class(model_cfg["class_path"])
        model = candidate_class(model_cfg["hyperparameters"])
        model.fit(X_final, self.y)

        out_dir = prod_cfg["export_directory"]
        os.makedirs(out_dir, exist_ok=True)

        # Serialize MLOps Bundle
        joblib.dump(model, os.path.join(out_dir, "model_weights.pkl"))
        joblib.dump(self.custom_transformers, os.path.join(out_dir, "feature_pipeline.pkl"))

        metadata = {
            "model_name": self.config["project"]["name"],
            "version": self.config["project"]["experiment_version"],
            "features": list(X_final.columns),
            "target": self.config["project"]["target_variable"],
            "metrics": {"primary_metric": self.config["experiment_settings"]["primary_metric"]}
        }
        with open(os.path.join(out_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=4)