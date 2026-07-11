import pandas as pd
from typing import Optional, List, Dict

class DesignAdvisor:
    """
    KMDS Design Governance Engine.
    Maps data profiles to architectural blueprints.

    Current scope:
    - Advisory-only module; runtime integration is separate.
    - Supports advisory guidance for Classification, Regression, Survival Analysis, Graph-based Analysis, and Clustering.
    - Classification and Regression are currently supported in runtime evaluation.
    - Graph, Clustering, and Survival Analysis remain advisory-only paths for future runtime support.
    - Recommendations are documented in the workspace `documents/modeling_contracts/` path.
    """
    def __init__(self):
        self.intents = {
            "TABULAR_CLASSIFICATION": "Standard classification (e.g., Is this loan good or bad?).",
            "TABULAR_REGRESSION": "Standard regression (e.g., What is the expected loss amount?).",
            "SURVIVAL_ANALYSIS": "Time-to-event survival analysis using Kaplan-Meier curves or Cox models.",
            "GRAPH_NODE_CLASSIFICATION": "Predicting a category for an entity based on its connections.",
            "GRAPH_NODE_REGRESSION": "Predicting a value for an entity based on its connections.",
            "GRAPH_DISCOVERY": "Unsupervised discovery of links or communities.",
            "CLUSTERING": "Unsupervised grouping of similar rows."
        }
        self.pillars = list(self.intents.keys())

    def profile_data(self, df: pd.DataFrame, target: Optional[str] = None, entities: List[str] = None) -> Dict:
        """Extracts objective metrics required for rule branching."""
        stats = {
            "row_count": len(df),
            "feature_count": len(df.columns),
            "entity_count": len(entities) if entities else 0
        }
        if target and target in df.columns:
            unique_count = df[target].nunique()
            stats["target_cardinality"] = unique_count
            if unique_count <= 20: 
                counts = df[target].value_counts(normalize=True)
                stats["minority_ratio"] = counts.min()
        return stats

    def get_recommendation(self, profile: Dict, user_intent: str, priority: str = "MAX_ACCURACY"):
        """
        Implements the Decision Tree:
        Scenario 1: Clear Pillar mapping.
        Scenario 2: Ambiguous (Multiple Pillars match).
        Scenario 3: Out of Scope.
        """
        if user_intent not in self.pillars:
            return "OUT_OF_SCOPE", "[kmds-modeling System Notice]: Requested workflow is out of scope."

        # Scenario 2 Check: Multiple entities but tabular intent (Ambiguity)
        if "TABULAR" in user_intent and profile.get("entity_count", 0) > 1:
            return "AMBIGUOUS", {
                "TABULAR": self.intents[user_intent],
                "GRAPH": f"Recommended due to multiple entities: {self.intents['GRAPH_NODE_CLASSIFICATION' if 'CLASSIFICATION' in user_intent else 'GRAPH_NODE_REGRESSION']}"
            }

        # Logic gates for Pillar A: Tabular Classification
        if user_intent == "TABULAR_CLASSIFICATION":
            if profile.get("target_cardinality", 0) > 20:
                return "OUT_OF_SCOPE", f"Target cardinality ({profile['target_cardinality']}) is too high for classification."

            ratio = profile.get("minority_ratio", 1.0)
            if ratio < 0.01:
                return "SUCCESS", {
                    "pillar": "A", 
                    "bucket": 3, 
                    "strategy": "Anomaly Detection",
                    "guidance": "Treat as Anomaly Detection. Use Isolation Forest or One-Class SVM. Avoid resampling."
                }
            elif ratio < 0.10:
                return "SUCCESS", {
                    "pillar": "A", 
                    "bucket": 2, 
                    "strategy": "Cost-Sensitive Learning",
                    "guidance": "Use cost-sensitive learning (e.g., class_weight='balanced'). Do not resample rows."
                }
            else:
                return "SUCCESS", {
                    "pillar": "A", 
                    "bucket": 1, 
                    "strategy": "Stratified Baseline",
                    "guidance": "Standard stratified cross-validation. No special imbalance handling required."
                }

        return "AMBIGUOUS", {"error": "Pillar implementation in progress."}