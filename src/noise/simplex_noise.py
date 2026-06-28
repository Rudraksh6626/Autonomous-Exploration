import numpy as np
from noise import snoise2

from noise.base_noise import BaseNoiseGenerator


class SimplexNoiseGenerator(BaseNoiseGenerator):

    def generate(self, size: int) -> np.ndarray:

        heightmap = np.zeros((size, size))

        for y in range(size):
            for x in range(size):

                value = snoise2(
                    x / self.scale,
                    y / self.scale,
                    octaves=self.octaves,
                    persistence=self.persistence,
                    lacunarity=self.lacunarity,
                    base=self.seed
                )

                heightmap[y, x] = value

        return heightmap