import pandas as pd
import numpy as np
from ..core.base import BaseModelCandidate


class ExampleSurvivalCandidate(BaseModelCandidate):
    """A minimal survival candidate that computes a Kaplan-Meier style survival function."""

    def __init__(self, hyperparameters: dict = None):
        super().__init__(hyperparameters or {})
        self.survival_df = None

    def fit(self, X_train: pd.DataFrame, durations: pd.Series, event_observed: pd.Series):
        data = pd.DataFrame(
            {
                "durations": durations,
                "event_observed": event_observed,
            }
        ).sort_values("durations")

        survival = 1.0
        survival_records = []
        unique_times = np.sort(data["durations"].unique())

        for time in unique_times:
            at_risk = (data["durations"] >= time).sum()
            events = ((data["durations"] == time) & (data["event_observed"] == 1)).sum()
            if at_risk > 0:
                survival *= 1.0 - (events / at_risk)
            survival_records.append({"timeline": time, "survival_probability": survival})

        self.survival_df = pd.DataFrame(survival_records).set_index("timeline")
        return self

    def predict_survival_function(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.survival_df is None:
            raise ValueError("The survival model must be fit before predicting a survival function.")

        repeated = pd.concat(
            [self.survival_df.assign(observation=i) for i in range(len(X))],
            keys=range(len(X)),
            names=["observation", "timeline"],
        )
        return repeated
