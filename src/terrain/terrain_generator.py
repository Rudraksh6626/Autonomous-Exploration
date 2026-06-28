from abc import ABC
from abc import abstractmethod

import numpy as np


class TerrainGenerator(ABC):

    def __init__(self, size=256):
        self.size = size

    @abstractmethod
    def generate(self) -> np.ndarray:
        pass

    @staticmethod
    def normalize(heightmap):

        minimum = np.min(heightmap)
        maximum = np.max(heightmap)

        if maximum - minimum == 0:
            return np.zeros_like(heightmap)

        return (
            heightmap - minimum
        ) / (
            maximum - minimum
        )