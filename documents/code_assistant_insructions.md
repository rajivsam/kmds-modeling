## Part 2: Code Assistant Instruction Markdown
(Save this exact section as ASSISTANT_INSTRUCTIONS.md and feed it directly into Google Code Assistant to generate the code)

# Instructions for Implementing the kmds-modeling Framework
You are an expert ML platform engineer. Your task is to implement the core python modules for a framework called `kmds-modeling`. The target directory structure has already been initialized. Implement the code files based on the specifications below.

## Core Engineering Requirements

1. **Index Preservation**: Every transformer and pipeline operation must strictly preserve the `record_id` string/numeric index from the input dataset.
2. **Leakage Prevention**: Feature transformations must be fit strictly on training folds and applied to validation folds.
3. **Model Agnosticism**: The engine must accept any model framework (Scikit-Learn, LightGBM, XGBoost) by interacting only through an abstract wrapper interface.

---

### Task 1: Implement Abstract Base Classes

Create `src/modeling/core/base.py`. This file must define the interfaces that data scientists will inherit from in their workspaces.

```python
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseFeatureTransformer(ABC):
    """Interface for ad-hoc dataset-level transformations."""
    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit internal parameters based on training data."""
        pass
        
    @abstractmethod
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transforms dataset features while maintaining the exact input index."""
        pass

    def fit_transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

class BaseModelCandidate(ABC):
    """Interface for uniform model orchestration."""
    def __init__(self, hyperparameters: dict):
        self.hyperparameters = hyperparameters
        
    @abstractmethod
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train the underlying model."""
        pass
        
    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return class probabilities. Must return a 2D array [prob_class_0, prob_class_1]."""
        pass
```
---### Task 2: Implement the Configuration and Data EngineCreate `src/modeling/core/runner.py`. This class orchestrates reading configs, parsing user-defined classes dynamically, executing cross-validation, and compiling build bundles.
```python
import yaml
import importlib
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, f1_score, precision_score

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
```
---### Task 3: Implement the Command Line Interface Entry pointCreate `

main.py

` at the root of the project to expose execution verbs.

```python
import click
from modeling.core.runner import ExperimentRunner

@click.group()
def cli():
    """KMDS Modeling CLI Framework Utility Engine."""
    pass

@cli.command()
@click.option('--config', required=True, type=click.Path(exists=True), help='Path to modeling_config.yaml')
def evaluate(config):
    """Runs cross-validation evaluations on all registered candidates."""
    runner = ExperimentRunner(config)
    click.echo("Starting candidate model evaluation loop...")
    df = runner.run_evaluation()
    click.echo("\n--- EXPERIMENT RESULTS LEADERBOARD ---")
    click.echo(df.to_string(index=False))

@cli.command()
@click.option('--config', required=True, type=click.Path(exists=True), help='Path to modeling_config.yaml')
def export(config):
    """Freezes training datasets and builds MLOps deployment assets."""
    runner = ExperimentRunner(config)
    click.echo("Building final production pipeline bundles...")
    runner.export_champion()

if __name__ == '__main__':
    cli()
```

------------------------------
## Next Step Verification
Once Google Code Assistant generates these three files inside your workspace, you are ready to start writing code as a data scientist.
Would you like to build an example workspace project configuration showing how a data scientist would subclass BaseFeatureTransformer to confirm that the package works as intended?
