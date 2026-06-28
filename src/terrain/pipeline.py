"""
Adapter layer that exposes granular pipeline methods expected by main.py
while delegating to the core implementation in world_generation_pipeline.py
"""
from pathlib import Path
import json
import random
import numpy as np

from terrain.terrain_composer import TerrainComposer
from terrain.heightmap_exporter import HeightmapExporter
from metrics.terrain_difficulty_analyzer import TerrainDifficultyAnalyzer
from gazebo.world_exporter import GazeboWorldExporter


class WorldGenerationPipeline:
    """
    Public-facing interface for terrain generation pipeline.
    Exposes granular methods that main.py expects, while maintaining
    the internal architecture of world_generation_pipeline.py.
    """

    def __init__(self):
        """Initialize pipeline state variables."""
        self.terrain_generators = []
        self.noise_generator = None
        self.obstacle_generators = []
        self.output_directory = Path("./output")
        self.seed = 42
        
        # Internal state holders
        self._heightmap = None
        self._noise = None
        self._terrain = None
        self._obstacles = None
        self._difficulty = None

    def initialize(self, config: dict) -> None:
        """
        Initialize pipeline from configuration dictionary.
        
        Args:
            config: Configuration dictionary with keys:
                - terrain_settings
                - experiment_settings
                - robot_parameters
        """
        terrain_settings = config.get("terrain_settings", {})
        
        self.seed = terrain_settings.get("seed", 42)
        output_dir = terrain_settings.get("output_directory", "./output")
        self.output_directory = Path(output_dir)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # These would be populated from config in a full implementation
        # For now, they're expected to be set via external means
        if not self.terrain_generators:
            # Placeholder - actual generators should come from factory
            pass

    def generate_procedural_terrain(self) -> None:
        """
        Generate base terrain from terrain generators.
        This step composes multiple terrain types into a single heightmap.
        """
        composer = TerrainComposer()
        
        for item in self.terrain_generators:
            if isinstance(item, tuple):
                generator, weight = item
                composer.add_generator(generator, weight)
            else:
                composer.add_generator(item)
        
        self._terrain = composer.compose()

    def generate_procedural_noise(self) -> None:
        """
        Apply noise overlay to terrain.
        Noise generators add detail and variation to the base terrain.
        """
        if self._terrain is None:
            raise RuntimeError("Terrain must be generated before noise.")
        
        if self.noise_generator is None:
            raise RuntimeError("Noise generator not configured.")
        
        size = self._terrain.shape[0]
        self._noise = self.noise_generator.generate(size=size)

    def compose_terrain(self) -> None:
        """
        Combine terrain and noise into final heightmap.
        This creates the complete heightmap used for obstacle placement and analysis.
        """
        if self._terrain is None:
            raise RuntimeError("Terrain must be generated first.")
        if self._noise is None:
            raise RuntimeError("Noise must be generated first.")
        
        self._heightmap = self._terrain + self._noise

    def generate_obstacles(self) -> None:
        """
        Generate obstacles on the heightmap.
        Uses rejection sampling and slope analysis to place obstacles appropriately.
        """
        if self._heightmap is None:
            raise RuntimeError("Heightmap must be composed before generating obstacles.")
        
        gradient_y, gradient_x = np.gradient(self._heightmap)
        slope_map = np.sqrt(gradient_x ** 2 + gradient_y ** 2)
        
        spawn = (5.0, 5.0)
        goal = (
            self._heightmap.shape[1] - 5.0,
            self._heightmap.shape[0] - 5.0
        )
        
        obstacles = []
        for generator in self.obstacle_generators:
            generated = generator.generate(
                self._heightmap,
                slope_map,
                spawn,
                goal
            )
            obstacles.extend(generated)
        
        self._obstacles = obstacles

    def analyze_terrain_difficulty(self) -> None:
        """
        Analyze terrain difficulty metrics.
        Computes traversability scores, slope gradients, and obstacle density.
        """
        if self._heightmap is None:
            raise RuntimeError("Heightmap must be composed before analysis.")
        if self._obstacles is None:
            raise RuntimeError("Obstacles must be generated before analysis.")
        
        obstacle_layout = np.zeros(self._heightmap.shape, dtype=np.uint8)
        
        for obstacle in self._obstacles:
            x = int(obstacle.x)
            y = int(obstacle.y)
            
            if (0 <= x < obstacle_layout.shape[1] and
                0 <= y < obstacle_layout.shape[0]):
                obstacle_layout[y, x] = 1
        
        analyzer = TerrainDifficultyAnalyzer()
        self._difficulty = analyzer.analyze(self._heightmap, obstacle_layout)

    def export_heightmap(self, output_path: str) -> None:
        """
        Export heightmap to file.
        Supports PNG, NPY, and CSV formats.
        
        Args:
            output_path: Path where heightmap should be saved (PNG format)
        """
        if self._heightmap is None:
            raise RuntimeError("Heightmap must be generated before export.")
        
        HeightmapExporter.export_png(self._heightmap, output_path)

    def export_gazebo_world(self, output_path: str) -> None:
        """
        Export Gazebo world file (SDF format).
        Includes terrain mesh and all obstacles.
        
        Args:
            output_path: Path where world file should be saved
        """
        if self._heightmap is None or self._obstacles is None:
            raise RuntimeError("Heightmap and obstacles must be generated before world export.")
        
        # Create temporary heightmap PNG for world export
        heightmap_png_path = Path(output_path).parent / "terrain_mesh.png"
        HeightmapExporter.export_png(self._heightmap, str(heightmap_png_path))
        
        # Export Gazebo world
        exporter = GazeboWorldExporter()
        exporter.export(
            image_path=str(heightmap_png_path),
            world_path=output_path,
            obstacles=self._obstacles
        )

    def _initialize_seed(self) -> None:
        """Initialize random seeds for reproducibility."""
        random.seed(self.seed)
        np.random.seed(self.seed)

    def _save_metadata(self, output_path: str) -> None:
        """
        Save pipeline execution metadata to JSON.
        
        Args:
            output_path: Path where metadata JSON should be saved
        """
        if self._difficulty is None:
            raise RuntimeError("Terrain analysis must be completed before metadata export.")
        
        metadata = {
            "seed": self.seed,
            "terrain_generators": [
                type(
                    item[0] if isinstance(item, tuple) else item
                ).__name__
                for item in self.terrain_generators
            ],
            "noise_generator": type(self.noise_generator).__name__,
            "obstacle_generators": [
                type(generator).__name__
                for generator in self.obstacle_generators
            ],
            "difficulty": {
                "average_slope": self._difficulty.average_slope,
                "maximum_slope": self._difficulty.maximum_slope,
                "surface_roughness": self._difficulty.surface_roughness,
                "obstacle_density": self._difficulty.obstacle_density,
                "traversability_score": self._difficulty.traversability_score,
                "difficulty_score": self._difficulty.difficulty_score,
                "category": self._difficulty.category,
            },
            "obstacle_count": len(self._obstacles) if self._obstacles else 0,
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
