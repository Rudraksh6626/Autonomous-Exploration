"""
summary_statistics.py

Computes statistical summaries across multiple exploration runs.
"""

from __future__ import annotations

from statistics import mean, median, stdev, variance
from typing import Dict, List

from .metrics_schema import (
    ExperimentMetrics,
    MetricSummary,
    ExperimentReport,
)


class SummaryStatistics:
    """
    Computes statistical summaries over multiple experiments.
    """

    def __init__(self, runs: List[ExperimentMetrics]):

        self.runs = runs

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _build_summary(values: List[float]) -> MetricSummary:
        """
        Create a MetricSummary object from a list of values.
        """

        if not values:
            return MetricSummary()

        if len(values) == 1:
            return MetricSummary(
                mean=values[0],
                median=values[0],
                minimum=values[0],
                maximum=values[0],
                std_dev=0.0,
                variance=0.0,
                count=1,
            )

        return MetricSummary(
            mean=mean(values),
            median=median(values),
            minimum=min(values),
            maximum=max(values),
            std_dev=stdev(values),
            variance=variance(values),
            count=len(values),
        )

    # ==========================================================
    # Exploration Metrics
    # ==========================================================

    def exploration_statistics(self) -> Dict[str, MetricSummary]:

        metrics = {}

        metrics["coverage_percentage"] = self._build_summary(
            [r.exploration.coverage_percentage for r in self.runs]
        )

        metrics["exploration_time"] = self._build_summary(
            [r.exploration.exploration_time for r in self.runs]
        )

        metrics["distance_traveled"] = self._build_summary(
            [r.exploration.distance_traveled for r in self.runs]
        )

        metrics["frontier_count"] = self._build_summary(
            [r.exploration.frontier_count for r in self.runs]
        )

        metrics["frontier_discovery_rate"] = self._build_summary(
            [r.exploration.frontier_discovery_rate for r in self.runs]
        )

        metrics["path_efficiency"] = self._build_summary(
            [r.exploration.path_efficiency for r in self.runs]
        )

        return metrics

    # ==========================================================
    # Mapping Metrics
    # ==========================================================

    def mapping_statistics(self) -> Dict[str, MetricSummary]:

        metrics = {}

        metrics["map_completeness"] = self._build_summary(
            [r.mapping.map_completeness for r in self.runs]
        )

        metrics["obstacle_density"] = self._build_summary(
            [r.mapping.obstacle_density for r in self.runs]
        )

        metrics["map_entropy"] = self._build_summary(
            [r.mapping.map_entropy for r in self.runs]
        )

        metrics["explored_cells"] = self._build_summary(
            [r.mapping.explored_cells for r in self.runs]
        )

        metrics["occupied_cells"] = self._build_summary(
            [r.mapping.occupied_cells for r in self.runs]
        )

        metrics["unknown_cells"] = self._build_summary(
            [r.mapping.unknown_cells for r in self.runs]
        )

        return metrics

    # ==========================================================
    # Combined Statistics
    # ==========================================================

    def compute(self) -> Dict[str, MetricSummary]:
        """
        Compute statistics for every metric.
        """

        summaries = {}

        summaries.update(
            self.exploration_statistics()
        )

        summaries.update(
            self.mapping_statistics()
        )

        return summaries

    # ==========================================================
    # Experiment Report
    # ==========================================================

    def generate_report(self) -> ExperimentReport:
        """
        Generate an ExperimentReport containing
        all runs and statistical summaries.
        """

        report = ExperimentReport()

        report.runs = self.runs

        report.summaries = self.compute()

        report.metadata["number_of_runs"] = len(self.runs)

        return report

    # ==========================================================
    # Console Output
    # ==========================================================

    def print_summary(self):

        summaries = self.compute()

        print("=" * 70)
        print("Experiment Summary")
        print("=" * 70)

        for metric, stats in summaries.items():

            print(f"\n{metric}")

            print(f"  Mean     : {stats.mean:.4f}")
            print(f"  Median   : {stats.median:.4f}")
            print(f"  Minimum  : {stats.minimum:.4f}")
            print(f"  Maximum  : {stats.maximum:.4f}")
            print(f"  Std Dev  : {stats.std_dev:.4f}")
            print(f"  Variance : {stats.variance:.4f}")
            print(f"  Count    : {stats.count}")