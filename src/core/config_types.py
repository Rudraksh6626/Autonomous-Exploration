from dataclasses import dataclass
from typing import Optional

# Backwards-compatible config types and loader for Autonomous-Exploration
# New lightweight dataclass to represent configuration without forcing
# import-time parsing. Existing module-level behavior is preserved via
# GLOBAL_CONFIG which calls load_config() with defaults.

@dataclass
class Config:
    world_size: int = 100
    noise_type: str = "perlin"
    output_dir: str = "./output"
    seed: int = 42
    # add other fields as needed in the future


def load_config(path: Optional[str] = None, env: Optional[dict] = None) -> Config:
    """
    Load configuration from a JSON/YAML file or environment dictionary and
    return a Config dataclass instance.

    This function is safe to call at import-time but does not perform heavy
    parsing by default; callers can pass a path to load a file.
    """
    # Minimal safe defaults. Preserve older behavior by returning defaults when
    # no path is provided.
    cfg = Config()

    # If an env dict is provided it overrides defaults
    if env:
        if "WORLD_SIZE" in env:
            try:
                cfg.world_size = int(env["WORLD_SIZE"])
            except Exception:
                pass
        if "NOISE_TYPE" in env:
            cfg.noise_type = env["NOISE_TYPE"]
        if "OUTPUT_DIR" in env:
            cfg.output_dir = env["OUTPUT_DIR"]
        if "SEED" in env:
            try:
                cfg.seed = int(env["SEED"])
            except Exception:
                pass

    # If a path is provided, attempt to parse JSON or YAML but swallow errors
    # and fall back to defaults to remain non-breaking.
    if path:
        from pathlib import Path
        import json
        try:
            import yaml  # optional dependency in the original project
        except Exception:
            yaml = None

        p = Path(path)
        if p.exists():
            try:
                if p.suffix.lower() in (".json",):
                    with p.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                elif p.suffix.lower() in (".yaml", ".yml") and yaml is not None:
                    with p.open("r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                else:
                    data = None

                if isinstance(data, dict):
                    if "world_size" in data:
                        try:
                            cfg.world_size = int(data["world_size"])
                        except Exception:
                            pass
                    if "noise_type" in data:
                        cfg.noise_type = data["noise_type"]
                    if "output_dir" in data:
                        cfg.output_dir = data["output_dir"]
                    if "seed" in data:
                        try:
                            cfg.seed = int(data["seed"])
                        except Exception:
                            pass
            except Exception:
                # Intentionally swallow parsing errors to preserve previous
                # behavior for callers that don't expect exceptions here.
                pass

    return cfg


# Backwards-compatible module-level global used by older code.
# Existing importers that relied on module-level parsing can continue to use
# core.config.GLOBAL_CONFIG
GLOBAL_CONFIG = load_config()
