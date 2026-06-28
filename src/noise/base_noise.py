from abc import ABC
from noise_generator import NoiseGenerator


class BaseNoiseGenerator(NoiseGenerator, ABC):

    def __init__(
        self,
        scale=50.0,
        octaves=4,
        persistence=0.5,
        lacunarity=2.0,
        seed=0
    ):
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.seed = seed