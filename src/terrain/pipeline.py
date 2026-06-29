"""
Adapter layer that exposes granular pipeline methods expected by main.py
while delegating to the core implementation in world_generation_pipeline.py
"""
import logging
from pathlib import Path
import json
import random
import numpy as np

from terrain.terrain_composer import TerrainComposer
from terrain.heightmap_exporter import HeightmapExporter
from terrain.terrain_factory import TerrainFactory
from noise.noise_factory import NoiseFactory
from obstacles.obstacle_factory import ObstacleFactory
from metrics.terrain_difficulty_analyzer import TerrainDifficultyAnalyzer
from gazebo.world_exporter import GazeboWorldExporter


logger = logging.getLogger(__name__)


class WorldGenerationPipeline:
    """
    Public-facing interface for terrain generation pipeline.
    Exposes granular methods that main.py expects, while maintaining
    the internal architecture of world_generation_pipeline.py.
    
    This class fully initializes all terrain generators, noise generators,
    and obstacle generators from configuration during initialize().
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
        
        logger.debug("WorldGenerationPipeline initialized")

    def initialize(self, config: dict) -> None:
        """
        Initialize pipeline from configuration dictionary.
        
        This method fully initializes:
        - Terrain generators from terrain_settings.generators
        - Noise generator from terrain_settings.noise
        - Obstacle generators from terrain_settings.obstacles
        
        Args:
            config: Configuration dictionary with keys:
                - terrain_settings (required):
                  - seed: Random seed for reproducibility
                  - output_directory: Where to save outputs
                  - generators: List of terrain generator configs
                  - noise: Noise generator configuration
                  - obstacles: List of obstacle generator configs
                - experiment_settings: Experiment parameters
                - robot_parameters: Robot configuration
                
        Raises:
            ValueError: If configuration is invalid or generator creation fails
            KeyError: If required configuration keys are missing
        """
        logger.info("Initializing WorldGenerationPipeline from configuration")
        
        terrain_settings = config.get("terrain_settings", {})
        
        # Extract basic settings
        self.seed = terrain_settings.get("seed", 42)
        output_dir = terrain_settings.get("output_directory", "./output")
        self.output_directory = Path(output_dir)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"Seed: {self.seed}")
        logger.debug(f"Output directory: {self.output_directory}")
        
        # Initialize random seeds
        self._initialize_seed()
        
        # Load terrain generators from config
        logger.info("Loading terrain generators from configuration")
        try:
            self.terrain_generators = TerrainFactory.from_config(terrain_settings)
            logger.info(f"Loaded {len(self.terrain_generators)} terrain generator(s)")
        except ValueError as e:
            logger.error(f"Failed to load terrain generators: {e}")
            raise
        
        # Load noise generator from config
        logger.info("Loading noise generator from configuration")
        try:
            noise_config = terrain_settings.get("noise", {})
            if noise_config:
                noise_type = noise_config.get("type", "perlin")
                noise_params = noise_config.get("parameters", {})
                self.noise_generator = NoiseFactory.create(noise_type, seed=self.seed, **noise_params)
                logger.info(f"Loaded noise generator: {noise_type}")
            else:
                logger.warning("No noise generator specified in configuration, using default Perlin")
                self.noise_generator = NoiseFactory.create("perlin", seed=self.seed)
        except ValueError as e:
            logger.error(f"Failed to load noise generator: {e}")
            raise
        
        # Load obstacle generators from config
        logger.info("Loading obstacle generators from configuration")
        try:
            self.obstacle_generators = ObstacleFactory.from_config(terrain_settings)
            logger.info(f"Loaded {len(self.obstacle_generators)} obstacle generator(s)")
        except ValueError as e:
            logger.error(f"Failed to load obstacle generators: {e}")
            raise
        
        logger.info("Pipeline initialization complete")

    def generate_procedural_terrain(self) -> None:
        """
        Generate base terrain from terrain generators.
        This step composes multiple terrain types into a single heightmap.
        
        Raises:
            RuntimeError: If no terrain generators are configured
            ValueError: If terrain generators produce incompatible output
        """
        logger.info("Generating procedural terrain")
        
        if not self.terrain_generators:
            raise RuntimeError(
                "No terrain generators configured. "
                "Call initialize(config) with terrain_settings.generators first."
            )
        
        composer = TerrainComposer()
        
        for item in self.terrain_generators:
            if isinstance(item, tuple):
                generator, weight = item
                logger.debug(f"Adding terrain generator with weight {weight}")
                composer.add_generator(generator, weight)
            else:
                logger.debug(f"Adding terrain generator with default weight")
                composer.add_generator(item)
        
        try:
            self._terrain = composer.compose()
            logger.info(f"Terrain generation complete: shape={self._terrain.shape}")
        except ValueError as e:
            logger.error(f"Terrain composition failed: {e}")
            raise

    def generate_procedural_noise(self) -> None:
        """
        Apply noise overlay to terrain.
        Noise generators add detail and variation to the base terrain.
        
        Raises:
            RuntimeError: If terrain hasn't been generated or noise generator not configured
        """
        logger.info("Generating procedural noise")
        
        if self._terrain is None:
            raise RuntimeError("Terrain must be generated before noise.")
        
        if self.noise_generator is None:
            raise RuntimeError("Noise generator not configured.")
        
        size = self._terrain.shape[0]
        logger.debug(f"Generating noise for size {size}")
        self._noise = self.noise_generator.generate(size=size)
        logger.info(f"Noise generation complete: shape={self._noise.shape}")

    def compose_terrain(self) -> None:
        """
        Combine terrain and noise into final heightmap.
        This creates the complete heightmap used for obstacle placement and analysis.
        
        Raises:
            RuntimeError: If terrain or noise haven't been generated
        """
        logger.info("Composing terrain and noise")
        
        if self._terrain is None:
            raise RuntimeError("Terrain must be generated first.")
        if self._noise is None:
            raise RuntimeError("Noise must be generated first.")
        
        self._heightmap = self._terrain + self._noise
        logger.info(f"Terrain composition complete: shape={self._heightmap.shape}")

    def generate_obstacles(self) -> None:
        """
        Generate obstacles on the heightmap.
        Uses rejection sampling and slope analysis to place obstacles appropriately.
        
        Raises:
            RuntimeError: If heightmap hasn't been composed or no obstacle generators configured
        """
        logger.info("Generating obstacles")
        
        if self._heightmap is None:
            raise RuntimeError("Heightmap must be composed before generating obstacles.")
        
        gradient_y, gradient_x = np.gradient(self._heightmap)
        slope_map = np.sqrt(gradient_x ** 2 + gradient_y ** 2)
        
        spawn = (5.0, 5.0)
        goal = (
            self._heightmap.shape[1] - 5.0,
            self._heightmap.shape[0] - 5.0
        )
        
        logger.debug(f"Spawn point: {spawn}, Goal point: {goal}")
        
        obstacles = []
        for i, generator in enumerate(self.obstacle_generators):
            logger.debug(f"Running obstacle generator {i+1}/{len(self.obstacle_generators)}")
            generated = generator.generate(
                self._heightmap,
                slope_map,
                spawn,
                goal
            )
            obstacles.extend(generated)
            logger.debug(f"Generated {len(generated)} obstacles")
        
        self._obstacles = obstacles
        logger.info(f"Obstacle generation complete: total {len(obstacles)} obstacles")

    def analyze_terrain_difficulty(self) -> None:
        """
        Analyze terrain difficulty metrics.
        Computes traversability scores, slope gradients, and obstacle density.
        
        Raises:
            RuntimeError: If heightmap or obstacles haven't been generated
        """
        logger.info("Analyzing terrain difficulty")
        
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
        logger.info(f"Terrain difficulty analysis complete: category={self._difficulty.category}")

    def export_heightmap(self, output_path: str) -> None:
        """
        Export heightmap to file.
        Supports PNG format.
        
        Args:
            output_path: Path where heightmap should be saved (PNG format)
            
        Raises:
            RuntimeError: If heightmap hasn't been generated
        """
        logger.info(f"Exporting heightmap to {output_path}")
        
        if self._heightmap is None:
            raise RuntimeError("Heightmap must be generated before export.")
        
        HeightmapExporter.export_png(self._heightmap, output_path)
        logger.info(f"Heightmap exported: {output_path}")

    def export_gazebo_world(self, output_path: str) -> None:
        """
        Export Gazebo world file (SDF format).
        Includes terrain mesh and all obstacles.
        
        Args:
            output_path: Path where world file should be saved
            
        Raises:
            RuntimeError: If heightmap or obstacles haven't been generated
        """
        logger.info(f"Exporting Gazebo world to {output_path}")
        
        if self._heightmap is None or self._obstacles is None:
            raise RuntimeError("Heightmap and obstacles must be generated before world export.")
        
        # Create temporary heightmap PNG for world export
        heightmap_png_path = Path(output_path).parent / "terrain_mesh.png"
        logger.debug(f"Creating temporary heightmap PNG: {heightmap_png_path}")
        HeightmapExporter.export_png(self._heightmap, str(heightmap_png_path))
        
        # Export Gazebo world
        logger.debug(f"Exporting Gazebo world SDF: {output_path}")
        exporter = GazeboWorldExporter()
        exporter.export(
            image_path=str(heightmap_png_path),
            world_path=output_path,
            obstacles=self._obstacles
        )
        logger.info(f"Gazebo world exported: {output_path}")

    def _initialize_seed(self) -> None:
        """Initialize random seeds for reproducibility."""
        logger.debug(f"Initializing random seeds with seed={self.seed}")
        random.seed(self.seed)
        np.random.seed(self.seed)

    def _save_metadata(self, output_path: str) -> None:
        """
        Save pipeline execution metadata to JSON.
        
        Args:
            output_path: Path where metadata JSON should be saved
            
        Raises:
            RuntimeError: If terrain analysis hasn't been completed
        """
        logger.debug(f"Saving metadata to {output_path}")
        
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
        
        logger.info(f"Metadata saved: {output_path}")
