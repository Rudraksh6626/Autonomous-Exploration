import matplotlib.pyplot as plt
import numpy as np

from .obstacle_models import Obstacle


class ObstacleVisualizer:

    @staticmethod
    def plot(
        heightmap: np.ndarray,
        obstacles: list[Obstacle]
    ) -> None:

        plt.figure(figsize=(10, 10))

        plt.imshow(
            heightmap,
            origin="lower"
        )

        for obstacle in obstacles:

            plt.scatter(
                obstacle.x,
                obstacle.y,
                s=20
            )

        plt.title(
            "Terrain and Obstacles"
        )

        plt.tight_layout()
        plt.show()