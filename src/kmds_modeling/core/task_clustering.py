from typing import Dict

from .task_base import BaseTaskRunner


class ClusteringTaskRunner(BaseTaskRunner):
    def run_evaluation(self):
        raise NotImplementedError(
            "Clustering is currently a supported advisory path, but runtime clustering evaluation is not implemented yet."
        )

    def export_champion(self):
        raise NotImplementedError(
            "Clustering model export is not implemented in kmds-modeling at this time."
        )
