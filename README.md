# Autonomous-Exploration

Procedural terrain synthesis and autonomous exploration benchmarking pipeline for Gazebo + ROS2.

## Overview

Autonomous-Exploration provides a configurable Python pipeline to:

- Procedurally generate terrain heightmaps using composable terrain generators and noise.
- Place obstacles using slope-aware rejection sampling.
- Export environments as PNG heightmaps and Gazebo SDF world files.
- Run ROS2-based exploration experiments, collect telemetry, and export benchmark JSONs.

This repository is intended for researchers and engineers evaluating exploration and mapping strategies in simulated environments.

---

## Quickstart

Requirements:
- Python 3.8+ with pip
- For experiment execution: ROS2 (and rclpy) and Gazebo installed and sourced

Install Python dependencies (minimum):

```bash
pip install pyyaml numpy scipy
```

Example run (generate environment + run experiments):

```bash
# create output dir
mkdir -p ./output ./logs

# run the orchestrator
python src/main.py --config path/to/config.yaml --output_dir ./output

# add verbose logging
python src/main.py --config path/to/config.yaml --output_dir ./output --verbose
```

Expected artifacts in `--output_dir`:

```
output/
├── terrain_heightmap.png      # Generated heightmap image
├── environment.world          # Gazebo SDF world file
├── benchmark_results.json     # Metrics and results
└── metadata.json              # Pipeline metadata
```

---

## Architecture (concise)

- Orchestrator: `src/main.py` drives three phases: bootstrap (config + logging), terrain pipeline, experiment framework.
- Adapter layer: terrain wrapper exposes granular pipeline methods and delegates to existing core implementations.
- Experiment framework: encapsulates ROS2 initialization, scenario execution, metrics collection, and result export.

Stack summary:
- Language: Python
- Simulation: Gazebo (SDF)
- Middleware: ROS2 (rclpy)
- Primary libs: numpy, PyYAML, SciPy (smoothing), noise/perlin (procedural)

---

## Folder layout (top-level)

```
Autonomous-Exploration/
├── README.md
├── INDEX.md
├── FIX_SUMMARY.md
├── ANALYSIS_AND_FIXES.md
├── EXECUTION_FLOW.md
├── REPOSITORY_CHANGES.md
├── package.xml
├── setup.py
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── world_generation_pipeline.py
│   │   └── ...
│   ├── terrain/
│   ├── noise/
│   ├── obstacles/
│   ├── gazebo/
│   ├── metrics/
│   └── experiment/
│       └── runner.py
└── launch/
```

See repository docs (INDEX.md, EXECUTION_FLOW.md) for full tree and diagrams.

---

## Configuration

Supported formats: YAML (`.yaml`, `.yml`) or JSON (`.json`).

Required top-level keys (main.py will validate these):
- `terrain_settings`
- `experiment_settings`
- `robot_parameters`
- `logging`

Example `config.yaml`:

```yaml
terrain_settings:
  seed: 42
  output_directory: ./output
  generators:
    - name: perlin
      weight: 0.7
    - name: ridged
      weight: 0.3

experiment_settings:
  scenario: tsp
  max_duration: 300
  map_resolution: 0.1

robot_parameters:
  name: robot
  max_velocity: 1.0
  sensor_range: 5.0

logging:
  level: INFO
  output_dir: ./logs
  file_name: autonomous_exploration.log
```

How to load/configure in code:
- `ConfigManager` is provided at `src/core/config.py` with `load_config(path)`, `get(key, default)` (dot notation), and `validate(required_keys)`.

---

## Execution flow (what main.py does)

Phase 1 — Bootstrap:
- parse CLI args (`--config`, `--output_dir`, `--verbose`)
- create output directory
- load config via `ConfigManager.load_config()`
- validate top-level keys
- initialize logging via `LoggerSetup`

Phase 2 — Terrain pipeline:
- instantiate `WorldGenerationPipeline` (adapter)
- `initialize(config)` → sets seed, output dir, registers generators
- `generate_procedural_terrain()` → calls terrain generators and composes base terrain
- `generate_procedural_noise()` → noise generation matching terrain size
- `compose_terrain()` → terrain + noise → heightmap
- `generate_obstacles()` → compute slopes and place obstacles using rejection sampling
- `analyze_terrain_difficulty()` → produce difficulty metrics
- `export_heightmap(path)` and `export_gazebo_world(path)` → write artifacts

Phase 3 — Experiment execution:
- instantiate `ExperimentFramework`
- `initialize(config)` → rclpy.init() and scenario setup
- `run_scenario()` → spawn agent(s), run exploration loop
- `collect_metrics()` → returns metrics dict
- `save_benchmark_results(metrics)` → JSON export
- `print_summary()` → formatted summary

---

## Public API (class & method summaries)

- core.config.ConfigManager
  - `load_config(config_path: str) -> dict`
  - `get(key: str, default=None) -> Any` (dot notation)
  - `validate(required_keys: list) -> bool`

- core.logger.LoggerSetup
  - `initialize_logging(config: dict) -> None`
  - `get_logger(name: str) -> logging.Logger`
  - `set_level(level: str) -> None`
  - `close() -> None`

- terrain.pipeline.WorldGenerationPipeline (adapter)
  - `initialize(config: dict) -> None`
  - `generate_procedural_terrain() -> None`
  - `generate_procedural_noise() -> None`
  - `compose_terrain() -> None`
  - `generate_obstacles() -> None`
  - `analyze_terrain_difficulty() -> None`
  - `export_heightmap(output_path: str) -> None`
  - `export_gazebo_world(output_path: str) -> None`

- experiment.runner.ExperimentFramework
  - `initialize(config: dict) -> None`
  - `run_scenario() -> None`
  - `collect_metrics() -> dict`
  - `save_benchmark_results(metrics: dict, path: Optional[str] = None) -> None`
  - `print_summary() -> None`
  - `cleanup() -> None`

(See implementation files in `src/core`, `src/terrain`, and `src/experiment` for details.)

---

## Benchmarking & Metrics

Metrics collected by `ExperimentFramework.collect_metrics()`:

- `exploration_time` (float, seconds)
- `distance_traveled` (float, meters)
- `area_explored` (float, m^2)
- `obstacles_encountered` (int)
- `path_efficiency` (float, 0.0-1.0)
- `success` (bool)
- `error_message` (string or null)

Benchmark JSON format (written to `output/benchmark_results.json`):

```json
{
  "experiment_config": { ... },
  "metrics": { ... },
  "timestamp": "ISO8601",
  "pipeline_metadata": { "seed": 42, "heightmap_shape": [Nx, Ny], "obstacle_count": N }
}
```

Tips:
- Run experiments for multiple seeds and aggregate mean/std for robust comparisons.
- Compare `exploration_time` and `area_explored` normalized by `path_efficiency` for ranking algorithms.

---

## Testing & Development notes

- Unit tests should mock `rclpy` and ROS2 topics if you want headless testing of `ExperimentFramework`.
- Validate configuration parsing separately with `ConfigManager.load_config()` and `ConfigManager.validate()`.
- Use `--verbose` to turn on DEBUG logging when investigating order-of-operations or numerical results.

---

## Troubleshooting

- Missing config or parse errors: ensure YAML/JSON syntax and file path are correct.
- ROS2/Gazebo experiments fail: confirm ROS2 installation, environment sourcing, and matching Gazebo version.
- File I/O issues: check permissions for `--output_dir` and `logging.output_dir`.

---

## Where to read next

- `FIX_SUMMARY.md` — quick overview and verification checklist
- `ANALYSIS_AND_FIXES.md` — detailed analysis of interface mismatch and fixes
- `EXECUTION_FLOW.md` — phase diagrams and state machine details
- `INDEX.md` — documentation index and example config snippets

---

## License & Contributing

See repository root for license or contact the repository owner.

Contributions: open PRs with clear tests and keep the orchestrator call order intact.
