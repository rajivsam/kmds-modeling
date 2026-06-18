import os
import yaml
import pandas as pd
from typing import Any, Dict, List, Optional

from .path_coordinator import PathCoordinator


class ModelAdvisor:
    """Independent KMDS modeling advisor service."""

    SUPPORTED_TASKS = [
        "TABULAR_CLASSIFICATION",
        "TABULAR_REGRESSION",
        "GRAPH_NODE_CLASSIFICATION",
        "GRAPH_NODE_REGRESSION",
        "GRAPH_DISCOVERY",
        "CLUSTERING",
    ]

    DEFAULT_INTENTS = {
        "TABULAR_CLASSIFICATION": "Standard classification (e.g., Is this loan good or bad?).",
        "TABULAR_REGRESSION": "Standard regression (e.g., What is the expected loss amount?).",
        "GRAPH_NODE_CLASSIFICATION": "Predicting a category for an entity based on its connections.",
        "GRAPH_NODE_REGRESSION": "Predicting a value for an entity based on its connections.",
        "GRAPH_DISCOVERY": "Unsupervised discovery of links or communities.",
        "CLUSTERING": "Unsupervised grouping of similar rows.",
    }

    INTRO_TEXT = (
        "I can give you modeling suggestions for the following tasks: Classification, Regression, "
        "Graph-based Analysis, and Clustering. If you are not sure if your use case is a fit for "
        "graph-based analysis, I can give you a simple heuristic. These are good starting points, "
        "and you are of course free to supplement them with independent research."
    )

    def __init__(self, config_path: str):
        self.config_path = os.path.abspath(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f) or {}

        self.data_cfg = self.config.get("data", {})
        self.working_dir = self.data_cfg.get("working_dir")
        if not self.working_dir:
            raise ValueError(
                "working_dir must be set in the data section of model_config.yaml before running the model advisor."
            )

        self.path_coordinator = PathCoordinator(working_dir=self.working_dir, config=self.config)
        if not os.path.isdir(self.path_coordinator.working_dir):
            raise FileNotFoundError(
                f"working_dir does not exist: {self.path_coordinator.working_dir}"
            )

    def intro(self) -> str:
        return self.INTRO_TEXT

    def available_tasks(self) -> List[str]:
        return list(self.SUPPORTED_TASKS)

    def get_recommendation(self, profile: Dict[str, Any], user_intent: str, priority: str = "MAX_ACCURACY"):
        if user_intent not in self.SUPPORTED_TASKS:
            return {
                "status": "OUT_OF_SCOPE",
                "message": "[kmds-modeling System Notice]: Requested workflow is out of scope.",
            }

        if user_intent == "TABULAR_CLASSIFICATION":
            return self._classification_recommendation(profile)
        if user_intent == "TABULAR_REGRESSION":
            return self._regression_recommendation(profile, priority)
        if user_intent.startswith("GRAPH_"):
            return self._graph_recommendation(profile, user_intent, priority)
        if user_intent == "CLUSTERING":
            return self._clustering_recommendation(profile)

        return {
            "status": "AMBIGUOUS",
            "message": "The requested task is recognized but not yet fully supported.",
        }

    def profile_data(
        self,
        df: pd.DataFrame,
        target: Optional[str] = None,
        entities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        stats = {
            "row_count": len(df),
            "feature_count": len(df.columns),
            "entity_count": len(entities) if entities else 0,
            "id_like_columns": self._count_id_like_columns(df.columns),
        }
        if target and target in df.columns:
            unique_count = df[target].nunique()
            stats["target_cardinality"] = unique_count
            if unique_count <= 20:
                counts = df[target].value_counts(normalize=True)
                stats["minority_ratio"] = counts.min()
        return stats

    def graph_suitability_hint(
        self,
        profile: Dict[str, Any],
        entities: Optional[List[str]] = None,
    ) -> str:
        if profile.get("entity_count", 0) > 1:
            return (
                "Graph-based analysis is likely appropriate because multiple entity relationships are present."
            )

        if profile.get("id_like_columns", 0) >= 2:
            return (
                "A graph-based analysis may be helpful when the dataset contains multiple ID-like fields. "
                "Consider whether your workflow is modeling relationships between entities."
            )

        return (
            "Graph-based analysis is probably not the primary fit for this dataset. "
            "If your problem is still relationship-driven, provide explicit entity mappings."
        )

    def recommendation_storage_path(self) -> str:
        return self.path_coordinator.modeling_recommendations_path

    def _classification_recommendation(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        if profile.get("target_cardinality", 0) > 20:
            return {
                "status": "OUT_OF_SCOPE",
                "message": f"Target cardinality ({profile['target_cardinality']}) is too high for classification.",
            }

        ratio = profile.get("minority_ratio", 1.0)
        if ratio < 0.01:
            return {
                "status": "SUCCESS",
                "pillar": "A",
                "bucket": 3,
                "strategy": "Anomaly Detection",
                "guidance": (
                    "Treat this as an anomaly detection scenario. Use Isolation Forest or One-Class SVM. "
                    "Avoid resampling."
                ),
                "reference": self._document_reference("tabular_classification"),
            }
        if ratio < 0.10:
            return {
                "status": "SUCCESS",
                "pillar": "A",
                "bucket": 2,
                "strategy": "Cost-Sensitive Learning",
                "guidance": (
                    "Use cost-sensitive learning (for example, class_weight='balanced'). "
                    "Do not resample rows."
                ),
                "reference": self._document_reference("tabular_classification"),
            }

        return {
            "status": "SUCCESS",
            "pillar": "A",
            "bucket": 1,
            "strategy": "Stratified Baseline",
            "guidance": (
                "Use stratified cross-validation. No special imbalance handling is required."
            ),
            "reference": self._document_reference("tabular_classification"),
        }

    def _regression_recommendation(self, profile: Dict[str, Any], priority: str) -> Dict[str, Any]:
        if priority == "HIGH_INTERPRETABILITY":
            guidance = (
                "Use additive or kernelized methods such as GAMs, Gaussian Processes, or kernel regression. "
                "Prefer visualizable partial dependence curves."
            )
        else:
            guidance = (
                "Use high-capacity, non-linear models such as XGBoost or Random Forest. "
                "Avoid simple linear models in this branch."
            )

        return {
            "status": "SUCCESS",
            "pillar": "B",
            "strategy": "Regression",
            "guidance": guidance,
            "reference": self._document_reference("tabular_regression"),
        }

    def _graph_recommendation(
        self,
        profile: Dict[str, Any],
        user_intent: str,
        priority: str,
    ) -> Dict[str, Any]:
        if user_intent == "GRAPH_DISCOVERY":
            guidance = (
                "Use unsupervised graph representation learning or community detection. "
                "Focus on topology discovery rather than target prediction."
            )
        elif user_intent == "GRAPH_NODE_CLASSIFICATION":
            guidance = (
                "Use a graph neural network architecture such as GraphSAGE or GCN for node classification. "
                "Apply loss reweighting instead of resampling for class imbalance."
            )
        else:
            guidance = (
                "Use a relational GNN architecture such as RGCN or HAN for graph node regression. "
                "Preserve the entity topology and avoid resampling the graph."
            )

        return {
            "status": "SUCCESS",
            "pillar": "C",
            "strategy": "Graph-Based Analysis",
            "guidance": guidance,
            "heuristic": self.graph_suitability_hint(profile),
            "reference": self._document_reference("graph_modeling"),
        }

    def _clustering_recommendation(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "pillar": "D",
            "strategy": "Clustering",
            "guidance": (
                "Use robust clustering that respects operational heterogeneity. "
                "Prefer spectral clustering with gap selection or HDBSCAN fallback when appropriate."
            ),
            "reference": self._document_reference("clustering"),
        }

    def _document_reference(self, topic: str) -> str:
        target_file = {
            "tabular_classification": "tabular_classification_recommendations.md",
            "tabular_regression": "tabular_regression_recommendations.md",
            "graph_modeling": "graph_modeling_recommendations.md",
            "clustering": "clustering_recommendations.md",
        }.get(topic, "modeling_recommendations.md")
        return os.path.join(self.path_coordinator.modeling_recommendations_path, target_file)

    @staticmethod
    def _count_id_like_columns(columns: List[str]) -> int:
        return sum(
            1
            for value in columns
            if value.lower().endswith("_id") or value.lower().startswith("id_")
        )
