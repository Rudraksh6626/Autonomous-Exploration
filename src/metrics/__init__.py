"""
Metrics subsystem.

Provides tools for:

- Exploration metrics
- Mapping metrics
- Runtime metric collection
- Report generation
- Summary statistics
"""

from .exploration_metrics import (
    compute_all_metrics,
    compute_average_speed,
    compute_coverage,
    compute_coverage_rate,
    compute_distance_traveled,
    compute_exploration_score,
    compute_exploration_time,
    compute_frontier_count,
    compute_frontier_discovery_rate,
    compute_idle_distance,
    compute_path_efficiency,
    euclidean_distance,
)

from .mapping_metrics import (
    MappingMetricsCalculator,
)

from .metrics_collector import (
    MetricsCollector,
)

from .metrics_schema import (
    ExperimentMetrics,
    ExperimentReport,
    ExplorationMetrics,
    MappingMetrics,
    MetricSummary,
)

from .report_generator import (
    ReportGenerator,
)

from .summary_statistics import (
    SummaryStatistics,
)

from .terrain_difficulty_analyzer import (
    TerrainDifficultyAnalyzer,
)

__all__ = [

    # Exploration
    "compute_all_metrics",
    "compute_average_speed",
    "compute_coverage",
    "compute_coverage_rate",
    "compute_distance_traveled",
    "compute_exploration_score",
    "compute_exploration_time",
    "compute_frontier_count",
    "compute_frontier_discovery_rate",
    "compute_idle_distance",
    "compute_path_efficiency",
    "euclidean_distance",

    # Mapping
    "MappingMetricsCalculator",

    # Collector
    "MetricsCollector",

    # Reports
    "ReportGenerator",
    "SummaryStatistics",
    "TerrainDifficultyAnalyzer",

    # Schemas
    "ExperimentMetrics",
    "ExperimentReport",
    "ExplorationMetrics",
    "MappingMetrics",
    "MetricSummary",
]