from abc import ABC, abstractmethod
import numpy as np

class NoiseGenerator(ABC):

    @abstractmethod
    def generate(self, size: int) -> np.ndarray:
        pass


class TerrainGenerator(ABC):

    @abstractmethod
    def generate(self) -> np.ndarray:
        pass


class ObstacleGenerator(ABC):

    @abstractmethod
    def generate(self):
        pass


class WorldExporter(ABC):

    @abstractmethod
    def export(self):
        pass


class MetricsCollector(ABC):

    @abstractmethod
    def collect(self):
        pass