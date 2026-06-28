from dataclasses import dataclass


@dataclass
class Scenario:

    name: str

    terrain: str

    noise_type: str

    noise_scale: float
    octaves: int
    persistence: float
    lacunarity: float

    obstacle_density: float
    obstacle_types: list[str]

    target_difficulty: float


class EasyScenario(Scenario):

    def __init__(self):
        super().__init__(
            name="easy",
            terrain="rolling_hills",
            noise_type="perlin",
            noise_scale=120.0,
            octaves=3,
            persistence=0.40,
            lacunarity=2.0,
            obstacle_density=0.05,
            obstacle_types=[
                "rocks",
            ],
            target_difficulty=0.25,
        )


class MediumScenario(Scenario):

    def __init__(self):
        super().__init__(
            name="medium",
            terrain="mixed",
            noise_type="perlin",
            noise_scale=80.0,
            octaves=4,
            persistence=0.50,
            lacunarity=2.1,
            obstacle_density=0.12,
            obstacle_types=[
                "rocks",
                "forest",
            ],
            target_difficulty=0.50,
        )


class HardScenario(Scenario):

    def __init__(self):
        super().__init__(
            name="hard",
            terrain="mountainous",
            noise_type="fbm",
            noise_scale=55.0,
            octaves=6,
            persistence=0.55,
            lacunarity=2.2,
            obstacle_density=0.20,
            obstacle_types=[
                "rocks",
                "forest",
                "walls",
                "passages",
            ],
            target_difficulty=0.75,
        )


class ExtremeScenario(Scenario):

    def __init__(self):
        super().__init__(
            name="extreme",
            terrain="rugged",
            noise_type="ridged",
            noise_scale=35.0,
            octaves=8,
            persistence=0.65,
            lacunarity=2.4,
            obstacle_density=0.35,
            obstacle_types=[
                "rocks",
                "forest",
                "walls",
                "passages",
                "dead_ends",
            ],
            target_difficulty=1.00,
        )