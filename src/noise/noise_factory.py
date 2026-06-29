from .perlin_noise import PerlinNoiseGenerator
from .simplex_noise import SimplexNoiseGenerator
from .fractal_noise import FractalNoiseGenerator


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