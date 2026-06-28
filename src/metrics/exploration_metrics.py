"""
exploration_metrics.py

Core exploration metric computations.

This module contains pure functions that compute robot exploration
performance metrics. These functions are intentionally independent
from ROS/Gazebo and only require simple Python data structures.

Author: Autonomous Exploration Project
"""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple

from .metrics_schema import ExplorationMetrics

Point = Tuple[float, float]


# ==========================================================
# Distance Metrics
# ==========================================================

def euclidean_distance(p1: Point, p2: Point) -> float:
    """
    Compute Euclidean distance between two points.
    """

    return math.hypot(
        p2[0] - p1[0],
        p2[1] - p1[1],
    )


def compute_distance_traveled(
    trajectory: Sequence[Point],
) -> float:
    """
    Total robot travel distance.
    """

    if len(trajectory) < 2:
        return 0.0

    distance = 0.0

    for i in range(1, len(trajectory)):
        distance += euclidean_distance(
            trajectory[i - 1],
            trajectory[i],
        )

    return distance


# ==========================================================
# Coverage
# ==========================================================

def compute_coverage(
    explored_cells: int,
    total_cells: int,
) -> float:
    """
    Coverage percentage.
    """

    if total_cells <= 0:
        return 0.0

    return (
        explored_cells / total_cells
    ) * 100.0


# ==========================================================
# Exploration Time
# ==========================================================

def compute_exploration_time(
    start_time: float,
    end_time: float,
) -> float:
    """
    Total exploration duration.
    """

    return max(
        0.0,
        end_time - start_time,
    )


# ==========================================================
# Frontier Metrics
# ==========================================================

def compute_frontier_count(
    frontiers: Iterable,
) -> int:
    """
    Current frontier count.
    """

    return len(list(frontiers))


def compute_frontier_discovery_rate(
    discovered_frontiers: int,
    exploration_time: float,
) -> float:
    """
    Frontiers discovered per second.
    """

    if exploration_time <= 0:
        return 0.0

    return (
        discovered_frontiers
        / exploration_time
    )


# ==========================================================
# Path Efficiency
# ==========================================================

def compute_path_efficiency(
    trajectory: Sequence[Point],
) -> float:
    """
    Straight-line distance divided by actual distance.

    Value:

    1.0 = perfectly efficient

    Near 0 = highly inefficient
    """

    if len(trajectory) < 2:
        return 1.0

    straight = euclidean_distance(
        trajectory[0],
        trajectory[-1],
    )

    traveled = compute_distance_traveled(
        trajectory
    )

    if traveled <= 0:
        return 1.0

    efficiency = straight / traveled

    efficiency = max(0.0, efficiency)

    efficiency = min(1.0, efficiency)

    return efficiency


# ==========================================================
# Speed
# ==========================================================

def compute_average_speed(
    trajectory: Sequence[Point],
    exploration_time: float,
) -> float:
    """
    Average robot speed.
    """

    if exploration_time <= 0:
        return 0.0

    return (
        compute_distance_traveled(
            trajectory
        )
        / exploration_time
    )


# ==========================================================
# Coverage Rate
# ==========================================================

def compute_coverage_rate(
    coverage_percentage: float,
    exploration_time: float,
) -> float:
    """
    Coverage percentage per second.
    """

    if exploration_time <= 0:
        return 0.0

    return (
        coverage_percentage
        / exploration_time
    )


# ==========================================================
# Idle Time
# ==========================================================

def compute_idle_distance(
    trajectory: Sequence[Point],
    threshold: float = 0.01,
) -> float:
    """
    Distance moved below threshold.
    """

    idle = 0.0

    for i in range(1, len(trajectory)):

        d = euclidean_distance(
            trajectory[i - 1],
            trajectory[i],
        )

        if d < threshold:
            idle += d

    return idle


# ==========================================================
# Exploration Score
# ==========================================================

def compute_exploration_score(
    coverage: float,
    efficiency: float,
) -> float:
    """
    Simple normalized score.
    """

    coverage_score = coverage / 100.0

    return (
        0.7 * coverage_score
        + 0.3 * efficiency
    )


# ==========================================================
# Complete Metric Pipeline
# ==========================================================

def compute_all_metrics(
    trajectory: Sequence[Point],
    explored_cells: int,
    total_cells: int,
    frontiers: Iterable,
    discovered_frontiers: int,
    start_time: float,
    end_time: float,
) -> ExplorationMetrics:
    """
    Compute every exploration metric.
    """

    coverage = compute_coverage(
        explored_cells,
        total_cells,
    )

    exploration_time = compute_exploration_time(
        start_time,
        end_time,
    )

    distance = compute_distance_traveled(
        trajectory,
    )

    frontier_count = compute_frontier_count(
        frontiers,
    )

    frontier_rate = compute_frontier_discovery_rate(
        discovered_frontiers,
        exploration_time,
    )

    path_efficiency = compute_path_efficiency(
        trajectory,
    )

    metrics = ExplorationMetrics()

    metrics.coverage_percentage = coverage

    metrics.exploration_time = exploration_time

    metrics.distance_traveled = distance

    metrics.frontier_count = frontier_count

    metrics.frontier_discovery_rate = frontier_rate

    metrics.path_efficiency = path_efficiency

    metrics.explored_cells = explored_cells

    metrics.total_cells = total_cells

    metrics.start_time = start_time

    metrics.end_time = end_time

    metrics.metadata["average_speed"] = compute_average_speed(
        trajectory,
        exploration_time,
    )

    metrics.metadata["coverage_rate"] = compute_coverage_rate(
        coverage,
        exploration_time,
    )

    metrics.metadata["idle_distance"] = compute_idle_distance(
        trajectory,
    )

    metrics.metadata["exploration_score"] = compute_exploration_score(
        coverage,
        path_efficiency,
    )

    return metrics