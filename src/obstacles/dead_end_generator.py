from typing import List

import numpy as np

from .obstacle_generator import ObstacleGenerator
from .obstacle_models import Obstacle


class DeadEndGenerator(ObstacleGenerator):

    def __init__(
        self,
        width: float = 15.0,
        depth: float = 15.0,
        obstacle_spacing: float = 1.0,
        wall_radius: float = 0.5,
        wall_height: float = 2.0,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.width = width
        self.depth = depth
        self.obstacle_spacing = obstacle_spacing
        self.wall_radius = wall_radius
        self.wall_height = wall_height

    def generate(
        self,
        heightmap: np.ndarray,
        slope_map: np.ndarray,
        spawn: tuple[float, float],
        goal: tuple[float, float]
    ) -> List[Obstacle]:

        rows, cols = heightmap.shape

        center_x = cols / 2
        center_y = rows / 2

        obstacles: List[Obstacle] = []

        for t in np.arange(
            0,
            self.depth,
            self.obstacle_spacing
        ):

            for side in (
                -self.width / 2,
                self.width / 2
            ):

                x = center_x + side
                y = center_y + t

                z = float(heightmap[int(y), int(x)])

                obstacles.append(
                    Obstacle(
                        x=x,
                        y=y,
                        z=z,
                        radius=self.wall_radius,
                        height=self.wall_height,
                        obstacle_type="dead_end"
                    )
                )

        for t in np.arange(
            -self.width / 2,
            self.width / 2,
            self.obstacle_spacing
        ):

            x = center_x + t
            y = center_y + self.depth

            z = float(heightmap[int(y), int(x)])

            obstacles.append(
                Obstacle(
                    x=x,
                    y=y,
                    z=z,
                    radius=self.wall_radius,
                    height=self.wall_height,
                    obstacle_type="dead_end"
                )
            )

        return obstacles