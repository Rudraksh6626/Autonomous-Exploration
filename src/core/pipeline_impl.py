from pathlib import Path
import json
import random

import numpy as np

from terrain.terrain_composer import TerrainComposer
from terrain.heightmap_exporter import HeightmapExporter
from metrics.terrain_difficulty_analyzer import TerrainDifficultyAnalyzer
from gazebo.world_exporter import GazeboWorldExporter


class WorldGenerationPipelineImpl:
    """
    Implementation class for world generation pipeline. Keep this internal so
    we can refactor internals while preserving the public WorldGenerationPipeline
    name and import path.
    """

    def __init__(
        self,
        terrain_generators,
        noise_generator,
        obstacle_generators,
        output_directory,
        seed=42,
        gazebo_exporter=None,
    ):
        self.terrain_generators = terrain_generators
        self.noise_generator = noise_generator
        self.obstacle_generators = obstacle_generators

        self.output_directory = Path(output_directory)
        self.seed = seed

        self.output_directory.mkdir(parents=True, exist_ok=True)

        # Allow injection of a Gazebo exporter (DI seam). If not supplied,
        # keep original behavior by instantiating the default exporter.
        self._gazebo_exporter = gazebo_exporter or GazeboWorldExporter()

    def generate(self):
        self._initialize_seed()
        heightmap = self._generate_heightmap()
        obstacles = self._generate_obstacles(heightmap)
        difficulty = self._analyze_difficulty(heightmap, obstacles)

        heightmap_path = self.output_directory / "heightmap.png"
        HeightmapExporter.export_png(heightmap, heightmap_path)

        world_path = self.output_directory / "world.world"
        # Use injected exporter
        self._gazebo_exporter.export(
            image_path=str(heightmap_path),
            world_path=str(world_path),
            obstacles=obstacles,
        )

        metadata_path = self.output_directory / "metadata.json"
        self._save_metadata(metadata_path, difficulty, obstacles)

        return {"heightmap": heightmap_path, "world": world_path, "metadata": metadata_path}

    def _initialize_seed(self):
        random.seed(self.seed)
        np.random.seed(self.seed)

    def _generate_heightmap(self):
        composer = TerrainComposer()
        for item in self.terrain_generators:
            if isinstance(item, tuple):
                generator, weight = item
                composer.add_generator(generator, weight)
            else:
                composer.add_generator(item)

        terrain = composer.compose()
        size = terrain.shape[0]
        noise = self.noise_generator.generate(size=size)
        return terrain + noise

    def _generate_obstacles(self, heightmap):
        gradient_y, gradient_x = np.gradient(heightmap)
        slope_map = np.sqrt(gradient_x ** 2 + gradient_y ** 2)

        obstacles = []
        spawn = (5.0, 5.0)
        goal = (heightmap.shape[1] - 5.0, heightmap.shape[0] - 5.0)

        for generator in self.obstacle_generators:
            generated = generator.generate(heightmap, slope_map, spawn, goal)
            obstacles.extend(generated)

        return obstacles

    def _analyze_difficulty(self, heightmap, obstacles):
        obstacle_layout = np.zeros(heightmap.shape, dtype=np.uint8)
        for obstacle in obstacles:
            x = int(obstacle.x)
            y = int(obstacle.y)
            if 0 <= x < obstacle_layout.shape[1] and 0 <= y < obstacle_layout.shape[0]:
                obstacle_layout[y, x] = 1

        analyzer = TerrainDifficultyAnalyzer()
        return analyzer.analyze(heightmap, obstacle_layout)

    def _save_metadata(self, output_path, difficulty, obstacles):
        metadata = {
            "seed": self.seed,
            "terrain_generators": [
                type(item[0] if isinstance(item, tuple) else item).__name__
                for item in self.terrain_generators
            ],
            "noise_generator": type(self.noise_generator).__name__,
            "obstacle_generators": [type(generator).__name__ for generator in self.obstacle_generators],
            "difficulty": {
                "average_slope": difficulty.average_slope,
                "maximum_slope": difficulty.maximum_slope,
                "surface_roughness": difficulty.surface_roughness,
                "obstacle_density": difficulty.obstacle_density,
                "traversability_score": difficulty.traversability_score,
                "difficulty_score": difficulty.difficulty_score,
                "category": difficulty.category,
            },
            "obstacle_count": len(obstacles),
        }

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)
