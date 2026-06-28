import numpy as np

from .obstacle_generator import ObstacleGenerator
from .obstacle_models import Obstacle
from .obstacle_utils import valid_position


class RockFieldGenerator(ObstacleGenerator):

    def __init__(
        self,
        rock_count: int = 100,
        radius_range=(0.4, 1.5),
        **kwargs
    ):
        super().__init__(**kwargs)

        self.rock_count = rock_count
        self.radius_range = radius_range

    def generate(
        self,
        heightmap,
        slope_map,
        spawn,
        goal
    ):

        rows, cols = heightmap.shape

        obstacles = []

        attempts = 0

        while (
            len(obstacles) < self.rock_count
            and attempts < self.rock_count * 50
        ):

            attempts += 1

            x = np.random.uniform(0, cols)
            y = np.random.uniform(0, rows)

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
                    radius=np.random.uniform(*self.radius_range),
                    height=1.0,
                    obstacle_type="rock"
                )
            )

        return obstacles