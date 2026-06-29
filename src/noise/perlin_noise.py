import numpy as np
from noise import pnoise2

from .base_noise import BaseNoiseGenerator


class PerlinNoiseGenerator(BaseNoiseGenerator):

    def generate(self, size: int) -> np.ndarray:
        """Generate a Perlin heightmap.

        Optimizations (preserve API/semantics):
        - Precompute scaled x/y coordinate arrays to avoid repeated division.
        - Use dtype float32 to reduce memory and improve cache use.
        - Cache attributes and pnoise2 lookup to locals to reduce attribute/global lookups.
        """

        # Local aliases / hoisted attributes
        inv_scale = 1.0 / float(self.scale)
        octaves = int(self.octaves)
        persistence = float(self.persistence)
        lacunarity = float(self.lacunarity)
        seed = int(self.seed)
        _pnoise2 = pnoise2

        # Precompute coordinates as float32
        xs = (np.arange(size, dtype=np.float32) * inv_scale)
        ys = (np.arange(size, dtype=np.float32) * inv_scale)

        # Allocate output once (float32 to save memory)
        heightmap = np.empty((size, size), dtype=np.float32)

        # Generate per-row to keep inner loop tight
        for y_idx, yv in enumerate(ys):
            for x_idx, xv in enumerate(xs):
                val = _pnoise2(
                    xv,
                    yv,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    repeatx=1024,
                    repeaty=1024,
                    base=seed,
                )
                heightmap[y_idx, x_idx] = val

        return heightmap
