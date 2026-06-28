from typing import List

import numpy as np

from .obstacle_generator import ObstacleGenerator
from .obstacle_models import Obstacle


class NarrowPassageGenerator(ObstacleGenerator):

    def __init__(
        self,
        wall_length: float = 30.0,
        gap_width: float = 3.0,
        obstacle_spacing: float = 1.0,
        wall_radius: float = 0.5,
        wall_height: float = 2.0,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.wall_length = wall_length
        self.gap_width = gap_width
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

        offsets = [
            -self.gap_width / 2,
            self.gap_width / 2
        ]

        for offset in offsets:

            for t in np.arange(
                -self.wall_length / 2,
                self.wall_length / 2,
                self.obstacle_spacing
            ):

                x = center_x + offset
                y = center_y + t

                if (
                    x < 0 or y < 0
                    or x >= cols
                    or y >= rows
                ):
                    continue

                z = float(heightmap[int(y), int(x)])

                obstacles.append(
                    Obstacle(
                        x=x,
                        y=y,
                        z=z,
                        radius=self.wall_radius,
                        height=self.wall_height,
                        obstacle_type="passage_wall"
                    )
                )

        return obstacles