from noise.perlin_noise import PerlinNoiseGenerator
from noise.simplex_noise import SimplexNoiseGenerator
from noise.fractal_noise import FractalNoiseGenerator


class NoiseFactory:

    @staticmethod
    def create(noise_type: str, **kwargs):

        mapping = {
            "perlin": PerlinNoiseGenerator,
            "simplex": SimplexNoiseGenerator,
            "fractal": FractalNoiseGenerator,
        }

        if noise_type not in mapping:
            raise ValueError(
                f"Unsupported noise type: {noise_type}"
            )

        return mapping[noise_type](**kwargs)