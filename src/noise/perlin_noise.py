import numpy as np
from noise import pnoise2

from noise.base_noise import BaseNoiseGenerator


class PerlinNoiseGenerator(BaseNoiseGenerator):

    def generate(self, size: int) -> np.ndarray:

        heightmap = np.zeros((size, size))

        for y in range(size):
            for x in range(size):

                value = pnoise2(
                    x / self.scale,
                    y / self.scale,
                    octaves=self.octaves,
                    persistence=self.persistence,
                    lacunarity=self.lacunarity,
                    repeatx=1024,
                    repeaty=1024,
                    base=self.seed
                )

                heightmap[y, x] = value

        return heightmap