import os
import json
from typing import Dict

import pandas as pd

from .task_base import BaseTaskRunner


class SurvivalTaskRunner(BaseTaskRunner):
    def run_evaluation(self) -> pd.DataFrame:
        raise NotImplementedError(
            "Survival analysis runtime evaluation is not implemented in kmds-modeling yet. "
            "Use a package like lifelines to fit Kaplan-Meier curves and derive survival metrics."
        )

    def export_champion(self):
        raise NotImplementedError(
            "Survival analysis export is not implemented in kmds-modeling at this time. "
            "A future implementation should serialize survival function estimates and Kaplan-Meier plots or tables."
        )
