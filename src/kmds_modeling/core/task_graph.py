from typing import Dict

from .task_base import BaseTaskRunner


class GraphTaskRunner(BaseTaskRunner):
    def run_evaluation(self):
        raise NotImplementedError(
            "Graph-based analysis is currently a supported advisory path, but runtime evaluation is not implemented in kmds-modeling yet. "
            "Future work should map dd-parser-cleaner metadata into PyG/DGL node and edge objects using the workspace PathCoordinator layout."
        )

    def export_champion(self):
        raise NotImplementedError(
            "Graph-based model export is not implemented in kmds-modeling at this time. "
            "The future implementation should freeze a graph data object and GNN weights from a PyG/DGL pipeline."
        )
