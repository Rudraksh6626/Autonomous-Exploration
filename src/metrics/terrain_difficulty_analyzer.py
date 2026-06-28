from dataclasses import dataclass

import numpy as np


@dataclass
class TerrainDifficultyResult:

    average_slope: float
    maximum_slope: float
    surface_roughness: float
    obstacle_density: float
    traversability_score: float

    difficulty_score: float
    category: str


class TerrainDifficultyAnalyzer:

    def __init__(
        self,
        max_traversable_slope: float = 30.0
    ):
        self.max_traversable_slope = max_traversable_slope

    def analyze(
        self,
        heightmap: np.ndarray,
        obstacle_layout: np.ndarray
    ) -> TerrainDifficultyResult:

        slopes = self._compute_slopes(heightmap)

        average_slope = float(np.mean(slopes))
        maximum_slope = float(np.max(slopes))

        surface_roughness = float(np.std(heightmap))

        obstacle_density = float(
            np.sum(obstacle_layout > 0)
            / obstacle_layout.size
        )

        traversability_score = self._compute_traversability(
            slopes,
            obstacle_layout
        )

        difficulty_score = self._compute_difficulty_score(
            average_slope,
            maximum_slope,
            surface_roughness,
            obstacle_density,
            traversability_score
        )

        category = self._difficulty_category(
            difficulty_score
        )

        return TerrainDifficultyResult(
            average_slope=average_slope,
            maximum_slope=maximum_slope,
            surface_roughness=surface_roughness,
            obstacle_density=obstacle_density,
            traversability_score=traversability_score,
            difficulty_score=difficulty_score,
            category=category
        )

    def _compute_slopes(
        self,
        heightmap: np.ndarray
    ) -> np.ndarray:

        gradient_y, gradient_x = np.gradient(
            heightmap
        )

        slope_radians = np.arctan(
            np.sqrt(
                gradient_x ** 2 +
                gradient_y ** 2
            )
        )

        return np.degrees(
            slope_radians
        )

    def _compute_traversability(
        self,
        slopes: np.ndarray,
        obstacle_layout: np.ndarray
    ) -> float:

        traversable = (
            (slopes < self.max_traversable_slope)
            &
            (obstacle_layout == 0)
        )

        return float(
            np.sum(traversable)
            / traversable.size
            * 100.0
        )

    def _compute_difficulty_score(
        self,
        avg_slope: float,
        max_slope: float,
        roughness: float,
        obstacle_density: float,
        traversability: float
    ) -> float:

        avg_slope_score = min(
            avg_slope / 45.0 * 100.0,
            100.0
        )

        max_slope_score = min(
            max_slope / 60.0 * 100.0,
            100.0
        )

        roughness_score = min(
            roughness * 20.0,
            100.0
        )

        obstacle_density_score = min(
            obstacle_density * 300.0,
            100.0
        )

        traversability_penalty = (
            100.0 - traversability
        )

        score = (
            0.25 * avg_slope_score +
            0.20 * max_slope_score +
            0.20 * roughness_score +
            0.15 * obstacle_density_score +
            0.20 * traversability_penalty
        )

        return float(
            np.clip(score, 0.0, 100.0)
        )

    def _difficulty_category(
        self,
        score: float
    ) -> str:

        if score <= 25:
            return "Easy"

        if score <= 50:
            return "Medium"

        if score <= 75:
            return "Hard"

        return "Extreme"