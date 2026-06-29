from pathlib import Path
import pytest

def test_execute_world_generation_with_stub_pipeline(tmp_path):
    # Import the helper from main (execute_world_generation)
    import main as main_mod

    # Create a stub pipeline with the expected public methods; record the call order
    calls = []

    class StubPipeline:
        def initialize(self, config=None):
            calls.append("initialize")
        def generate_procedural_terrain(self):
            calls.append("terrain")
        def generate_procedural_noise(self):
            calls.append("noise")
        def compose_terrain(self):
            calls.append("compose")
        def generate_obstacles(self):
            calls.append("obstacles")
        def analyze_terrain_difficulty(self):
            calls.append("analyze")
        def export_heightmap(self, path):
            calls.append(("export_heightmap", path))
            Path(path).write_text("PNG")
        def export_gazebo_world(self, path):
            calls.append(("export_world", path))
            Path(path).write_text("<world/>")

    stub = StubPipeline()
    output_dir = tmp_path
    main_mod.execute_world_generation(stub, output_dir)

    # Check order includes the main sequence steps
    assert "terrain" in calls
    assert "noise" in calls
    assert ("export_heightmap", str(output_dir / "terrain_heightmap.png")) in calls
    assert ("export_world", str(output_dir / "environment.world")) in calls
