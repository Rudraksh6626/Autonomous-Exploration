"""
report_generator.py

Exports experiment metrics to JSON, CSV and summary reports.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from .metrics_schema import (
    ExperimentMetrics,
    ExperimentReport,
)


class ReportGenerator:
    """
    Generates experiment reports.
    """

    def __init__(self, output_directory="generated/reports"):

        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ======================================================
    # JSON
    # ======================================================

    def export_json(
        self,
        metrics: ExperimentMetrics,
        filename: str,
    ):

        path = self.output_directory / filename

        with open(path, "w", encoding="utf-8") as file:

            json.dump(
                metrics.to_dict(),
                file,
                indent=4,
            )

        return path

    # ======================================================
    # CSV
    # ======================================================

    def export_csv(
        self,
        metrics: ExperimentMetrics,
        filename: str,
    ):

        path = self.output_directory / filename

        exploration = metrics.exploration
        mapping = metrics.mapping

        rows = [

            ("Experiment", metrics.experiment_name),

            ("Algorithm", metrics.algorithm),

            ("World", metrics.world_name),

            ("Seed", metrics.seed),

            ("Coverage (%)", exploration.coverage_percentage),

            ("Exploration Time", exploration.exploration_time),

            ("Distance Travelled", exploration.distance_traveled),

            ("Frontier Count", exploration.frontier_count),

            (
                "Frontier Discovery Rate",
                exploration.frontier_discovery_rate,
            ),

            (
                "Path Efficiency",
                exploration.path_efficiency,
            ),

            ("Explored Cells", exploration.explored_cells),

            ("Total Cells", exploration.total_cells),

            ("Map Completeness", mapping.map_completeness),

            ("Obstacle Density", mapping.obstacle_density),

            ("Map Entropy", mapping.map_entropy),
        ]

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(["Metric", "Value"])

            writer.writerows(rows)

        return path

    # ======================================================
    # Experiment List JSON
    # ======================================================

    def export_experiment_report(
        self,
        report: ExperimentReport,
        filename="experiment_report.json",
    ):

        path = self.output_directory / filename

        with open(path, "w", encoding="utf-8") as file:

            json.dump(
                report.to_dict(),
                file,
                indent=4,
            )

        return path

    # ======================================================
    # Summary CSV
    # ======================================================

    def export_summary_csv(
        self,
        report: ExperimentReport,
        filename="summary.csv",
    ):

        path = self.output_directory / filename

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
                [
                    "Metric",
                    "Mean",
                    "Median",
                    "Minimum",
                    "Maximum",
                    "Std Dev",
                    "Variance",
                    "Count",
                ]
            )

            for name, summary in report.summaries.items():

                writer.writerow(
                    [
                        name,
                        summary.mean,
                        summary.median,
                        summary.minimum,
                        summary.maximum,
                        summary.std_dev,
                        summary.variance,
                        summary.count,
                    ]
                )

        return path

    # ======================================================
    # Batch Export
    # ======================================================

    def export_all_runs(
        self,
        runs: List[ExperimentMetrics],
    ):

        exported = []

        for i, run in enumerate(runs, start=1):

            json_name = f"run_{i:03d}.json"

            csv_name = f"run_{i:03d}.csv"

            self.export_json(run, json_name)

            self.export_csv(run, csv_name)

            exported.append(
                {
                    "json": json_name,
                    "csv": csv_name,
                }
            )

        return exported

    # ======================================================
    # Pretty Console Output
    # ======================================================

    @staticmethod
    def print_summary(metrics: ExperimentMetrics):

        e = metrics.exploration
        m = metrics.mapping

        print("=" * 60)
        print("Exploration Summary")
        print("=" * 60)

        print(f"Coverage              : {e.coverage_percentage:.2f}%")
        print(f"Time                  : {e.exploration_time:.2f}s")
        print(f"Distance              : {e.distance_traveled:.2f}m")
        print(f"Frontiers             : {e.frontier_count}")
        print(f"Discovery Rate        : {e.frontier_discovery_rate:.3f}")
        print(f"Path Efficiency       : {e.path_efficiency:.3f}")

        print()

        print("Mapping")

        print(f"Explored Cells        : {m.explored_cells}")
        print(f"Unknown Cells         : {m.unknown_cells}")
        print(f"Occupied Cells        : {m.occupied_cells}")
        print(f"Map Completeness      : {m.map_completeness:.2f}%")
        print(f"Obstacle Density      : {m.obstacle_density:.2f}%")
        print(f"Map Entropy           : {m.map_entropy:.3f}")

        print("=" * 60)