import numpy as np

from src.noise.perlin_noise import PerlinNoiseGenerator
from src.noise.simplex_noise import SimplexNoiseGenerator
from src.noise.fractal_noise import FractalNoiseGenerator


def test_perlin_shape():

    gen = PerlinNoiseGenerator()

    heightmap = gen.generate(64)

    assert heightmap.shape == (64, 64)


def test_simplex_shape():

    gen = SimplexNoiseGenerator()

    heightmap = gen.generate(64)

    assert heightmap.shape == (64, 64)


def test_fractal_shape():

    gen = FractalNoiseGenerator()

    heightmap = gen.generate(64)

    assert heightmap.shape == (64, 64)


def test_seed_reproducibility():

    gen1 = PerlinNoiseGenerator(seed=42)
    gen2 = PerlinNoiseGenerator(seed=42)

    h1 = gen1.generate(64)
    h2 = gen2.generate(64)

    assert np.allclose(h1, h2)


def test_different_seeds():

    gen1 = PerlinNoiseGenerator(seed=1)
    gen2 = PerlinNoiseGenerator(seed=2)

    h1 = gen1.generate(64)
    h2 = gen2.generate(64)

    assert not np.allclose(h1, h2)


def test_noise_variation():

    gen = PerlinNoiseGenerator()

    heightmap = gen.generate(64)

    assert np.std(heightmap) > 0.01