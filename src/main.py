import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np

from experiments import ScenarioManager
from terrain.terrain_types import (
    FlatTerrain,
    HillTerrain,
    MountainTerrain,
    ValleyTerrain,
    RoughTerrain,
)
from terrain.terrain_composer import TerrainComposer
from terrain.heightmap_exporter import HeightmapExporter
from noise.noise_factory import NoiseFactory
from obstacles.rock_field_generator import RockFieldGenerator
from obstacles.forest_cluster_generator import ForestClusterGenerator
from obstacles.barrier_wall_generator import BarrierWallGenerator
from obstacles.dead_end_generator import DeadEndGenerator
from obstacles.narrow_passage_generator import NarrowPassageGenerator
from gazebo.world_builder import WorldBuilder
from gazebo.world_exporter import GazeboWorldExporter
from metrics.terrain_difficulty_analyzer import TerrainDifficultyAnalyzer
from obstacles.sdf_exporter import SDFObstacleExporter


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for world generation.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Procedural Terrain & Obstacle Generation for Autonomous Exploration"
    )

    parser.add_argument(
        "--scenario",
        type=str,
        default="medium",
        choices=["easy", "medium", "hard", "extreme"],
        help="Difficulty scenario (default: medium)",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default="./generated",
        help="Output directory for generated files (default: ./generated)",
    )

    parser.add_argument(
        "--heightmap_size",
        type=int,
        default=256,
        help="Heightmap resolution (default: 256x256)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def setup_logging(verbose: bool) -> logging.Logger:
    """
    Initialize logging infrastructure.

    Args:
        verbose: If True, set level to DEBUG

    Returns:
        logging.Logger: Configured logger
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    return logging.getLogger(__name__)


def instantiate_terrain_generators(size: int) -> list:
    """
    Create terrain generator instances.

    Args:
        size: Heightmap size

    Returns:
        list: Terrain generator instances
    """
    generators = [
        HillTerrain(size=size, hill_height=15.0),
        ValleyTerrain(size=size, depth=15.0),
    ]

    return generators


def generate_terrain(
    logger: logging.Logger, scenario_name: str, heightmap_size: int, seed: int
) -> np.ndarray:
    """
    Generate procedural terrain for the scenario.

    Execution sequence:
    1. Load scenario configuration
    2. Compose base terrain from multiple generators
    3. Apply noise (Perlin/FBM/Ridged)
    4. Return blended heightmap

    Args:
        logger: Logger instance
        scenario_name: Scenario name (easy|medium|hard|extreme)
        heightmap_size: Heightmap resolution
        seed: Random seed

    Returns:
        np.ndarray: Composed and noisy heightmap
    """
    logger.info(f"Generating terrain for scenario: {scenario_name}")

    # Set seed
    np.random.seed(seed)

    # Load scenario
    scenario_manager = ScenarioManager()
    scenario = scenario_manager.get(scenario_name)
    logger.info(
        f"Scenario: {scenario.name} | Noise: {scenario.noise_type} | "
        f"Difficulty: {scenario.target_difficulty}"
    )

    # Compose terrain
    logger.info("Composing terrain generators...")
    composer = TerrainComposer(normalize=True, smoothing=False)

    terrain_generators = instantiate_terrain_generators(heightmap_size)
    for gen in terrain_generators:
        composer.add_generator(gen, weight=1.0)

    composed_terrain = composer.compose()
    logger.info(f"Composed terrain shape: {composed_terrain.shape}")

    # Generate noise
    logger.info(f"Generating {scenario.noise_type} noise...")
    noise_generator = NoiseFactory.create(
        scenario.noise_type,
        scale=scenario.noise_scale,
        octaves=scenario.octaves,
        persistence=scenario.persistence,
        lacunarity=scenario.lacunarity,
        seed=seed,
    )

    noise_array = noise_generator.generate(size=heightmap_size)
    logger.info(f"Noise shape: {noise_array.shape}")

    # Blend terrain and noise
    heightmap = composed_terrain + (noise_array * 0.3)

    logger.info(f"Final heightmap range: [{heightmap.min():.2f}, {heightmap.max():.2f}]")

    return heightmap


def generate_obstacles(
    logger: logging.Logger, heightmap: np.ndarray, scenario_name: str
) -> list:
    """
    Generate obstacles using rejection sampling.

    Args:
        logger: Logger instance
        heightmap: Terrain heightmap
        scenario_name: Scenario name (for obstacle selection)

    Returns:
        list: List of Obstacle objects
    """
    logger.info(f"Generating obstacles for {scenario_name} scenario...")

    # Compute slope map
    gradient_y, gradient_x = np.gradient(heightmap)
    slope_map = np.sqrt(gradient_x**2 + gradient_y**2)

    rows, cols = heightmap.shape
    spawn = (5.0, 5.0)
    goal = (cols - 5.0, rows - 5.0)

    # Instantiate generators based on scenario
    generators = []

    if scenario_name in ["easy", "medium", "hard", "extreme"]:
        generators.append(RockFieldGenerator(rock_count=50))

    if scenario_name in ["medium", "hard", "extreme"]:
        generators.append(ForestClusterGenerator(cluster_count=3))

    if scenario_name in ["hard", "extreme"]:
        generators.append(BarrierWallGenerator(wall_length=25.0))

    if scenario_name == "extreme":
        generators.append(DeadEndGenerator(dead_end_count=2))
        generators.append(NarrowPassageGenerator(passage_count=2))

    # Generate obstacles
    all_obstacles = []
    for generator in generators:
        logger.info(f"  - {generator.__class__.__name__}...")
        obstacles = generator.generate(heightmap, slope_map, spawn, goal)
        all_obstacles.extend(obstacles)
        logger.info(f"    Generated {len(obstacles)} obstacles")

    logger.info(f"Total obstacles: {len(all_obstacles)}")

    return all_obstacles


def analyze_terrain(
    logger: logging.Logger, heightmap: np.ndarray, obstacles: list
) -> dict:
    """
    Analyze terrain difficulty.

    Args:
        logger: Logger instance
        heightmap: Terrain heightmap
        obstacles: List of Obstacle objects

    Returns:
        dict: Difficulty analysis results
    """
    logger.info("Analyzing terrain difficulty...")

    analyzer = TerrainDifficultyAnalyzer()

    # Build obstacle layout
    obstacle_layout = np.zeros(heightmap.shape, dtype=np.uint8)
    for obstacle in obstacles:
        x = int(obstacle.x)
        y = int(obstacle.y)
        if 0 <= x < heightmap.shape[1] and 0 <= y < heightmap.shape[0]:
            obstacle_layout[y, x] = 1

    # Analyze
    result = analyzer.analyze(heightmap, obstacle_layout)

    logger.info(f"  - Average slope: {result.average_slope:.2f}°")
    logger.info(f"  - Max slope: {result.maximum_slope:.2f}°")
    logger.info(f"  - Surface roughness: {result.surface_roughness:.2f}")
    logger.info(f"  - Obstacle density: {result.obstacle_density:.2%}")
    logger.info(f"  - Traversability: {result.traversability_score:.1f}%")
    logger.info(f"  - Difficulty score: {result.difficulty_score:.1f}/100 ({result.category})")

    return {
        "average_slope": result.average_slope,
        "maximum_slope": result.maximum_slope,
        "surface_roughness": result.surface_roughness,
        "obstacle_density": result.obstacle_density,
        "traversability_score": result.traversability_score,
        "difficulty_score": result.difficulty_score,
        "category": result.category,
    }


def export_heightmap(
    logger: logging.Logger, heightmap: np.ndarray, output_dir: Path
) -> None:
    """
    Export heightmap to PNG, NPY, and CSV.

    Args:
        logger: Logger instance
        heightmap: Terrain heightmap
        output_dir: Output directory
    """
    logger.info(f"Exporting heightmap to {output_dir}...")

    HeightmapExporter.export_all(heightmap, output_dir)

    logger.info("  - terrain.png (PNG image)")
    logger.info("  - terrain.npy (NumPy binary)")
    logger.info("  - terrain.csv (CSV data)")


def export_gazebo_world(
    logger: logging.Logger,
    heightmap: np.ndarray,
    obstacles: list,
    output_dir: Path,
) -> None:
    """
    Export Gazebo SDF world file.

    Args:
        logger: Logger instance
        heightmap: Terrain heightmap
        obstacles: List of Obstacle objects
        output_dir: Output directory
    """
    logger.info("Building Gazebo world...")

    # Build world
    builder = WorldBuilder()
    builder.add_obstacles(obstacles)

    # Export heightmap
    heightmap_path = output_dir / "terrain.png"
    HeightmapExporter.export_png(heightmap, heightmap_path)

    # Export world
    world_path = output_dir / "environment.world"
    logger.info(f"Exporting SDF world to {world_path}...")

    exporter = GazeboWorldExporter()
    exporter.export(
        image_path=str(heightmap_path),
        world_path=str(world_path),
        obstacles=obstacles,
    )

    logger.info(f"  - {world_path}")


def export_metadata(
    logger: logging.Logger,
    output_dir: Path,
    difficulty: dict,
    obstacles: list,
    seed: int,
) -> None:
    """
    Export metadata (difficulty info, obstacle count, seed).

    Args:
        logger: Logger instance
        output_dir: Output directory
        difficulty: Difficulty analysis results
        obstacles: List of obstacles
        seed: Random seed
    """
    logger.info("Exporting metadata...")

    metadata = {
        "seed": seed,
        "obstacle_count": len(obstacles),
        "difficulty": difficulty,
    }

    metadata_path = output_dir / "metadata.json"

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    logger.info(f"  - {metadata_path}")


def main() -> int:
    """
    Main orchestration function.

    Execution flow:
    1. Parse CLI arguments
    2. Setup logging
    3. Create output directory
    4. Generate terrain
    5. Generate obstacles
    6. Analyze terrain difficulty
    7. Export heightmap (PNG/NPY/CSV)
    8. Export Gazebo world
    9. Export metadata

    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    args = parse_arguments()

    logger = setup_logging(args.verbose)

    try:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # Phase 1: Generate terrain
        heightmap = generate_terrain(logger, args.scenario, args.heightmap_size, args.seed)

        # Phase 2: Generate obstacles
        obstacles = generate_obstacles(logger, heightmap, args.scenario)

        # Phase 3: Analyze terrain
        difficulty = analyze_terrain(logger, heightmap, obstacles)

        # Phase 4: Export heightmap
        export_heightmap(logger, heightmap, output_dir)

        # Phase 5: Export Gazebo world
        export_gazebo_world(logger, heightmap, obstacles, output_dir)

        # Phase 6: Export metadata
        export_metadata(logger, output_dir, difficulty, obstacles, args.seed)

        logger.info("✓ World generation completed successfully!")

        return 0

    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
