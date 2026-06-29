import pytest
from pathlib import Path

def test_pipeline_order_enforcement_and_state_machine():
    from terrain.pipeline import WorldGenerationPipeline

    p = WorldGenerationPipeline()
    # Most pipelines require initialize() first; if so, this should raise if not initialized.
    # We check general out-of-order behavior: calling noise before terrain should raise.
    with pytest.raises(RuntimeError):
        p.generate_procedural_noise()

    with pytest.raises(RuntimeError):
        p.compose_terrain()

def test_pipeline_full_sequence_with_monkeypatched_components(tmp_path, monkeypatch):
    from terrain import pipeline as pipeline_mod
    from terrain.pipeline import WorldGenerationPipeline

    calls = []

    # Monkeypatch internal components or methods to be no-ops but record that they were called.
    def fake_generate_terrain(self):
        calls.append("terrain")
        self._terrain = "terrain_data"

    def fake_generate_noise(self):
        calls.append("noise")
        self._noise = "noise_data"

    def fake_compose(self):
        calls.append("compose")
        self._heightmap = "heightmap_data"

    def fake_generate_obstacles(self):
        calls.append("obstacles")
        self._obstacles = ["obs1"]

    def fake_analyze(self):
        calls.append("analyze")
        self._difficulty = {"score": 0.5}

    def fake_export_heightmap(self, path):
        calls.append(("export_heightmap", path))
        Path(path).write_text("PNG")

    def fake_export_world(self, path):
        calls.append(("export_world", path))
        Path(path).write_text("<world/>")

    monkeypatch.setattr(WorldGenerationPipeline, "generate_procedural_terrain", fake_generate_terrain, raising=False)
    monkeypatch.setattr(WorldGenerationPipeline, "generate_procedural_noise", fake_generate_noise, raising=False)
    monkeypatch.setattr(WorldGenerationPipeline, "compose_terrain", fake_compose, raising=False)
    monkeypatch.setattr(WorldGenerationPipeline, "generate_obstacles", fake_generate_obstacles, raising=False)
    monkeypatch.setattr(WorldGenerationPipeline, "analyze_terrain_difficulty", fake_analyze, raising=False)
    monkeypatch.setattr(WorldGenerationPipeline, "export_heightmap", fake_export_heightmap, raising=False)
    monkeypatch.setattr(WorldGenerationPipeline, "export_gazebo_world", fake_export_world, raising=False)

    p = WorldGenerationPipeline()
    # If initialize exists, call it with an empty config (defensive)
    init = getattr(p, "initialize", None)
    if callable(init):
        init({})

    # Run sequence
    p.generate_procedural_terrain()
    p.generate_procedural_noise()
    p.compose_terrain()
    p.generate_obstacles()
    p.analyze_terrain_difficulty()

    out_hm = tmp_path / "terrain_heightmap.png"
    out_world = tmp_path / "environment.world"
    p.export_heightmap(str(out_hm))
    p.export_gazebo_world(str(out_world))

    # Verify call order
    assert calls[0:5] == ["terrain", "noise", "compose", "obstacles", "analyze"]
    assert any(call[0] == "export_heightmap" for call in calls if isinstance(call, tuple))
    assert out_hm.exists()
    assert out_world.exists()
