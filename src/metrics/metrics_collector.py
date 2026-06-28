"""
metrics_collector.py

Collects runtime exploration data and computes final
exploration/mapping metrics.

This class is intended to be updated continuously while the
simulation is running.
"""

from __future__ import annotations

import time
from typing import Any, List, Optional, Sequence, Tuple

import numpy as np

from .exploration_metrics import compute_all_metrics
from .mapping_metrics import MappingMetricsCalculator
from .metrics_schema import (
    ExperimentMetrics,
    ExplorationMetrics,
    MappingMetrics,
)

Point = Tuple[float, float]


class MetricsCollector:
    """
    Runtime metrics collector.

    Example
    -------
    collector = MetricsCollector()

    collector.start()

    collector.update_position(x, y)

    collector.update_frontier(frontiers)

    collector.update_map(occupancy_grid)

    ...

    metrics = collector.finish()
    """

    def __init__(self):

        self.reset()

    # ======================================================
    # Lifecycle
    # ======================================================

    def reset(self):

        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        self.robot_path: List[Point] = []

        self.timestamps: List[float] = []

        self.frontier_history: List[int] = []

        self.coverage_history: List[float] = []

        self.discovered_frontiers = 0

        self.current_frontiers = []

        self.occupancy_grid = None

        self.explored_cells = 0
        self.total_cells = 0

    def start(self):

        self.reset()

        self.start_time = time.time()

    def finish(
        self,
        experiment_name: str = "",
        algorithm: str = "",
        world_name: str = "",
        seed: Optional[int] = None,
    ) -> ExperimentMetrics:

        self.end_time = time.time()

        exploration = compute_all_metrics(
            trajectory=self.robot_path,
            explored_cells=self.explored_cells,
            total_cells=self.total_cells,
            frontiers=self.current_frontiers,
            discovered_frontiers=self.discovered_frontiers,
            start_time=self.start_time or 0.0,
            end_time=self.end_time,
        )

        if self.occupancy_grid is not None:

            mapping = MappingMetricsCalculator(
                self.occupancy_grid
            ).compute_metrics()

        else:

            mapping = MappingMetrics()

        return ExperimentMetrics(
            experiment_name=experiment_name,
            algorithm=algorithm,
            seed=seed,
            world_name=world_name,
            exploration=exploration,
            mapping=mapping,
        )

    # ======================================================
    # Robot
    # ======================================================

    def update_position(
        self,
        x: float,
        y: float,
    ):

        self.robot_path.append((x, y))

        self.timestamps.append(time.time())

    def update_pose(
        self,
        pose: Sequence[float],
    ):

        self.update_position(
            float(pose[0]),
            float(pose[1]),
        )

    # ======================================================
    # Frontiers
    # ======================================================

    def update_frontiers(
        self,
        frontiers,
    ):

        self.current_frontiers = list(frontiers)

        self.frontier_history.append(
            len(frontiers)
        )

        self.discovered_frontiers += len(frontiers)

    # ======================================================
    # Coverage
    # ======================================================

    def update_coverage(
        self,
        explored_cells: int,
        total_cells: int,
    ):

        self.explored_cells = explored_cells
        self.total_cells = total_cells

        if total_cells > 0:

            coverage = (
                explored_cells
                / total_cells
            ) * 100.0

        else:

            coverage = 0.0

        self.coverage_history.append(
            coverage
        )

    # ======================================================
    # Occupancy Grid
    # ======================================================

    def update_map(
        self,
        occupancy_grid,
    ):

        self.occupancy_grid = np.asarray(
            occupancy_grid
        )

        self.total_cells = int(
            self.occupancy_grid.size
        )

        self.explored_cells = int(
            np.sum(self.occupancy_grid != -1)
        )

    # ======================================================
    # Metadata
    # ======================================================

    def path(self):

        return self.robot_path

    def latest_position(self):

        if not self.robot_path:
            return None

        return self.robot_path[-1]

    def elapsed_time(self):

        if self.start_time is None:
            return 0.0

        return time.time() - self.start_time

    # ======================================================
    # Statistics
    # ======================================================

    def total_positions(self):

        return len(self.robot_path)

    def total_frontiers(self):

        return self.discovered_frontiers

    def average_frontiers(self):

        if not self.frontier_history:
            return 0.0

        return (
            sum(self.frontier_history)
            / len(self.frontier_history)
        )

    def maximum_frontiers(self):

        if not self.frontier_history:
            return 0

        return max(self.frontier_history)

    def average_coverage(self):

        if not self.coverage_history:
            return 0.0

        return (
            sum(self.coverage_history)
            / len(self.coverage_history)
        )