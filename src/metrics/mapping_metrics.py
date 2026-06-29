"""
mapping_metrics.py

Mapping quality metrics for occupancy-grid based exploration.

These metrics evaluate the generated map independently from
robot exploration metrics.
"""

from __future__ import annotations

import math

import numpy as np

from .metrics_schema import MappingMetrics


class MappingMetricsCalculator:
    """
    Computes mapping quality metrics from occupancy grids.

    Grid convention:

        -1 = Unknown
         0 = Free
       100 = Occupied
    """

    UNKNOWN = -1
    FREE = 0
    OCCUPIED = 100

    def __init__(self, occupancy_grid: np.ndarray):

        self.grid = np.asarray(occupancy_grid)

    # --------------------------------------------------
    # Cell Counts
    # --------------------------------------------------

    def total_cells(self) -> int:
        return int(self.grid.size)

    def explored_cells(self) -> int:
        return int(np.sum(self.grid != self.UNKNOWN))

    def unknown_cells(self) -> int:
        return int(np.sum(self.grid == self.UNKNOWN))

    def occupied_cells(self) -> int:
        return int(np.sum(self.grid == self.OCCUPIED))

    def free_cells(self) -> int:
        return int(np.sum(self.grid == self.FREE))

    # --------------------------------------------------
    # Coverage
    # --------------------------------------------------

    def map_completeness(self) -> float:

        total = self.total_cells()

        if total == 0:
            return 0.0

        return (
            self.explored_cells() / total
        ) * 100.0

    def exploration_completeness(self) -> float:
        return self.map_completeness()

    # --------------------------------------------------
    # Obstacle Density
    # --------------------------------------------------

    def obstacle_density(self) -> float:

        explored = self.explored_cells()

        if explored == 0:
            return 0.0

        return (
            self.occupied_cells() / explored
        ) * 100.0

    # --------------------------------------------------
    # Entropy
    # --------------------------------------------------

    def map_entropy(self) -> float:

        explored = self.explored_cells()

        if explored == 0:
            return 0.0

        p_free = self.free_cells() / explored
        p_occ = self.occupied_cells() / explored

        entropy = 0.0

        for p in (p_free, p_occ):
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    # --------------------------------------------------
    # Time
    # --------------------------------------------------

    @staticmethod
    def map_completion_time(
        start_time: float,
        end_time: float,
    ) -> float:

        return max(
            0.0,
            end_time - start_time,
        )

    # --------------------------------------------------
    # Build Dataclass
    # --------------------------------------------------

    def compute_metrics(self) -> MappingMetrics:

        metrics = MappingMetrics()

        metrics.total_cells = self.total_cells()

        metrics.explored_cells = self.explored_cells()

        metrics.unknown_cells = self.unknown_cells()

        metrics.occupied_cells = self.occupied_cells()

        metrics.free_cells = self.free_cells()

        metrics.map_completeness = self.map_completeness()

        metrics.exploration_completeness = (
            self.exploration_completeness()
        )

        metrics.obstacle_density = (
            self.obstacle_density()
        )

        metrics.map_entropy = self.map_entropy()

        return metrics