import numpy as np
from noise import pnoise2

from noise.base_noise import BaseNoiseGenerator


class FractalNoiseGenerator(BaseNoiseGenerator):

    def generate(self, size: int) -> np.ndarray:

        heightmap = np.zeros((size, size))

        for y in range(size):
            for x in range(size):

                frequency = 1.0
                amplitude = 1.0

                total = 0.0
                max_amplitude = 0.0

                for _ in range(self.octaves):

                    total += amplitude * pnoise2(
                        x * frequency / self.scale,
                        y * frequency / self.scale,
                        base=self.seed
                    )

                    max_amplitude += amplitude

                    amplitude *= self.persistence
                    frequency *= self.lacunarity

                heightmap[y, x] = total / max_amplitude

        return heightmap