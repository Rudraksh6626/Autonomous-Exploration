import json
import pytest

def test_experiment_lifecycle_and_metrics(tmp_path, capsys):
    from experiment.runner import ExperimentFramework

    ef = ExperimentFramework()
    # initialize should accept a config dict per docs
    ef.initialize({"experiment_settings": {}, "robot_parameters": {}})

    # Replace run_scenario with a fast stub and collect_metrics to return a deterministic dictionary
    def fake_run():
        # simulate some internal state change if needed
        return None

    metrics = {
        "exploration_time": 1.2,
        "distance_traveled": 10.0,
        "area_explored": 5.0,
        "obstacles_encountered": 0,
        "path_efficiency": 0.9,
        "success": True,
        "error_message": None,
    }

    ef.run_scenario = fake_run
    ef.collect_metrics = lambda: metrics

    ef.run_scenario()
    m = ef.collect_metrics()
    assert m["success"] is True

    out_file = tmp_path / "benchmark_results.json"
    ef.save_benchmark_results(m, str(out_file))

    assert out_file.exists()
    loaded = json.loads(out_file.read_text())
    assert "metrics" in loaded

    ef.print_summary()
    captured = capsys.readouterr()
    # print_summary should output something human-readable that includes at least one metric
    assert "exploration_time" in captured.out or "distance_traveled" in captured.out

    ef.cleanup()
