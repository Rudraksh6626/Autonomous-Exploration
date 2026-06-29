import json
import pytest
from pathlib import Path

def test_load_yaml_and_dot_get_and_validate(tmp_path):
    content = """
terrain_settings:
  seed: 123
  output_directory: ./out
experiment_settings:
  scenario: tsp
robot_parameters:
  name: robot
"""
    p = tmp_path / "config.yaml"
    p.write_text(content)

    # Import here so tests fail fast if module missing
    from core.config import ConfigManager

    cm = ConfigManager()
    cfg = cm.load_config(str(p))
    # Basic structure check
    assert isinstance(cfg, dict)
    # Dot access
    assert cm.get("terrain_settings.seed") == 123
    assert cm.get("terrain_settings.output_directory") == "./out"
    # Validate required keys returns True for present keys
    assert cm.validate(["terrain_settings", "experiment_settings", "robot_parameters"]) is True

def test_load_json_and_missing_keys(tmp_path):
    data = {
        "terrain_settings": {"seed": 1},
        # experiment_settings intentionally omitted
        "robot_parameters": {"name": "r"}
    }
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))

    from core.config import ConfigManager
    cm = ConfigManager()
    cfg = cm.load_config(str(p))
    # validate raises ValueError when required keys are missing
with pytest.raises(ValueError):
    cm.validate(["terrain_settings", "experiment_settings", "robot_parameters"])

def test_load_nonexistent_file_raises(tmp_path):
    from core.config import ConfigManager
    cm = ConfigManager()
    with pytest.raises(FileNotFoundError):
        cm.load_config(str(tmp_path / "does_not_exist.yaml"))
