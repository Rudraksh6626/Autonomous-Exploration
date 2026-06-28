"""
metrics_schema.py

Central dataclasses used by the metrics subsystem.

These classes define a consistent schema for exploration,
mapping and experiment reports.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional


# ============================================================
# Exploration Metrics
# ============================================================

@dataclass
class ExplorationMetrics:
    """
    Metrics describing the robot exploration performance.
    """

    coverage_percentage: float = 0.0
    exploration_time: float = 0.0
    distance_traveled: float = 0.0

    frontier_count: int = 0
    frontier_discovery_rate: float = 0.0

    path_efficiency: float = 0.0

    explored_cells: int = 0
    total_cells: int = 0

    start_time: Optional[float] = None
    end_time: Optional[float] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# Mapping Metrics
# ============================================================

@dataclass
class MappingMetrics:
    """
    Metrics describing occupancy-grid quality.
    """

    total_cells: int = 0

    explored_cells: int = 0

    unknown_cells: int = 0

    occupied_cells: int = 0

    free_cells: int = 0

    obstacle_density: float = 0.0

    map_completeness: float = 0.0

    exploration_completeness: float = 0.0

    map_entropy: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# Experiment Metrics
# ============================================================

@dataclass
class ExperimentMetrics:
    """
    Complete metrics generated from one experiment.
    """

    experiment_name: str = ""

    algorithm: str = ""

    seed: Optional[int] = None

    world_name: str = ""

    exploration: ExplorationMetrics = field(
        default_factory=ExplorationMetrics
    )

    mapping: MappingMetrics = field(
        default_factory=MappingMetrics
    )

    additional_metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "experiment_name": self.experiment_name,
            "algorithm": self.algorithm,
            "seed": self.seed,
            "world_name": self.world_name,
            "exploration": self.exploration.to_dict(),
            "mapping": self.mapping.to_dict(),
            "additional_metrics": self.additional_metrics,
        }


# ============================================================
# Summary Statistics
# ============================================================

@dataclass
class MetricSummary:
    """
    Statistical summary of one metric across experiments.
    """

    mean: float = 0.0

    median: float = 0.0

    minimum: float = 0.0

    maximum: float = 0.0

    std_dev: float = 0.0

    variance: float = 0.0

    count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# Overall Experiment Report
# ============================================================

@dataclass
class ExperimentReport:
    """
    Final report containing all experiment runs
    together with statistical summaries.
    """

    runs: List[ExperimentMetrics] = field(default_factory=list)

    summaries: Dict[str, MetricSummary] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {
            "runs": [
                run.to_dict()
                for run in self.runs
            ],
            "summaries": {
                key: value.to_dict()
                for key, value in self.summaries.items()
            },
            "metadata": self.metadata,
        }