from abc import ABC
from abc import abstractmethod
from typing import List
import numpy as np

from .obstacle_models import Obstacle


class ObstacleGenerator(ABC):

    def __init__(
        self,
        min_spacing: float = 2.0,
        max_slope: float = 0.4
    ):
        self.min_spacing = min_spacing
        self.max_slope = max_slope

    @abstractmethod
    def generate(
        self,
        heightmap: np.ndarray,
        slope_map: np.ndarray,
        spawn: tuple[float, float],
        goal: tuple[float, float]
    ) -> List[Obstacle]:
        ...