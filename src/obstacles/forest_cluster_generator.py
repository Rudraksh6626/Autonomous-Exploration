from typing import List

import numpy as np

from .obstacle_generator import ObstacleGenerator
from .obstacle_models import Obstacle
from .obstacle_utils import valid_position


class ForestClusterGenerator(ObstacleGenerator):

    def __init__(
        self,
        cluster_count: int = 5,
        trees_per_cluster: int = 25,
        cluster_radius: float = 8.0,
        tree_radius: float = 0.4,
        tree_height: float = 4.0,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.cluster_count = cluster_count
        self.trees_per_cluster = trees_per_cluster
        self.cluster_radius = cluster_radius
        self.tree_radius = tree_radius
        self.tree_height = tree_height

    def generate(
        self,
        heightmap: np.ndarray,
        slope_map: np.ndarray,
        spawn: tuple[float, float],
        goal: tuple[float, float]
    ) -> List[Obstacle]:

        rows, cols = heightmap.shape
        obstacles: List[Obstacle] = []

        for _ in range(self.cluster_count):

            center_x = np.random.uniform(0, cols)
            center_y = np.random.uniform(0, rows)

            attempts = 0

            while (
                len(obstacles) <
                (_ + 1) * self.trees_per_cluster
                and attempts < self.trees_per_cluster * 20
            ):

                attempts += 1

                x = np.random.normal(
                    center_x,
                    self.cluster_radius
                )

                y = np.random.normal(
                    center_y,
                    self.cluster_radius
                )

                if not valid_position(
                    x,
                    y,
                    slope_map,
                    obstacles,
                    self.min_spacing,
                    spawn,
                    goal,
                    max_slope=self.max_slope
                ):
                    continue

                z = float(heightmap[int(y), int(x)])

                obstacles.append(
                    Obstacle(
                        x=x,
                        y=y,
                        z=z,
                        radius=self.tree_radius,
                        height=self.tree_height,
                        obstacle_type="tree"
                    )
                )

        return obstacles