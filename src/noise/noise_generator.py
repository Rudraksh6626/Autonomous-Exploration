from abc import ABC, abstractmethod
import numpy as np


class NoiseGenerator(ABC):

    @abstractmethod
    def generate(self, size: int) -> np.ndarray:
        """
        Returns a size x size heightmap.
        """
        pass