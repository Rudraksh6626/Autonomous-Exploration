from .scenarios import (
    EasyScenario,
    MediumScenario,
    HardScenario,
    ExtremeScenario,
)


class ScenarioManager:

    def __init__(self):

        self._scenarios = {
            "easy": EasyScenario,
            "medium": MediumScenario,
            "hard": HardScenario,
            "extreme": ExtremeScenario,
        }

    def available(self):
        return list(self._scenarios.keys())

    def get(self, name):

        key = name.lower()

        if key not in self._scenarios:
            raise ValueError(f"Unknown scenario: {name}")

        return self._scenarios[key]()

    def configure(
        self,
        terrain_generator,
        obstacle_generator,
        noise_generator,
        scenario_name,
    ):

        scenario = self.get(scenario_name)

        terrain_generator.set_terrain_type(
            scenario.terrain
        )

        noise_generator.configure(
            noise_type=scenario.noise_type,
            scale=scenario.noise_scale,
            octaves=scenario.octaves,
            persistence=scenario.persistence,
            lacunarity=scenario.lacunarity,
        )

        obstacle_generator.set_density(
            scenario.obstacle_density
        )

        obstacle_generator.enable_types(
            scenario.obstacle_types
        )

        return scenario