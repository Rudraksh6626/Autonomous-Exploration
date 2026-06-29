import numpy as np

from .terrain_generator import TerrainGenerator


class FlatTerrain(TerrainGenerator):

    def __init__(
        self,
        size=256,
        height=0.0
    ):
        super().__init__(size)

        self.height = height

    def generate(self):

        return np.full(
            (self.size, self.size),
            self.height,
            dtype=np.float32
        )


class HillTerrain(TerrainGenerator):

    def __init__(
        self,
        size=256,
        hill_height=20.0,
        hill_radius=0.4
    ):
        super().__init__(size)

        self.hill_height = hill_height
        self.hill_radius = hill_radius

    def generate(self):

        x = np.linspace(-1, 1, self.size)
        y = np.linspace(-1, 1, self.size)

        xx, yy = np.meshgrid(x, y)

        distance = np.sqrt(
            xx**2 + yy**2
        )

        terrain = (
            self.hill_height *
            np.exp(
                -(distance**2)
                /
                (
                    2 *
                    self.hill_radius**2
                )
            )
        )

        return terrain.astype(np.float32)


class MountainTerrain(TerrainGenerator):

    def __init__(
        self,
        size=256,
        peak_height=50.0,
        steepness=8.0
    ):
        super().__init__(size)

        self.peak_height = peak_height
        self.steepness = steepness

    def generate(self):

        x = np.linspace(-1, 1, self.size)
        y = np.linspace(-1, 1, self.size)

        xx, yy = np.meshgrid(x, y)

        distance = np.sqrt(
            xx**2 + yy**2
        )

        terrain = (
            self.peak_height *
            np.exp(
                -distance *
                self.steepness
            )
        )

        return terrain.astype(np.float32)


class ValleyTerrain(TerrainGenerator):

    def __init__(
        self,
        size=256,
        depth=30.0,
        radius=0.5
    ):
        super().__init__(size)

        self.depth = depth
        self.radius = radius

    def generate(self):

        x = np.linspace(-1, 1, self.size)
        y = np.linspace(-1, 1, self.size)

        xx, yy = np.meshgrid(x, y)

        distance = np.sqrt(
            xx**2 + yy**2
        )

        terrain = (
            -self.depth *
            np.exp(
                -(distance**2)
                /
                (
                    2 *
                    self.radius**2
                )
            )
        )

        return terrain.astype(np.float32)


class RoughTerrain(TerrainGenerator):

    def __init__(
        self,
        size=256,
        roughness=10.0,
        seed=None
    ):
        super().__init__(size)

        self.roughness = roughness
        self.seed = seed

    def generate(self):

        rng = np.random.default_rng(
            self.seed
        )

        terrain = rng.normal(
            loc=0.0,
            scale=self.roughness,
            size=(self.size, self.size)
        )

        return terrain.astype(np.float32)