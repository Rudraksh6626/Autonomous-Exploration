import numpy as np

from src.metrics import (
    TerrainDifficultyAnalyzer
)


def test_flat_easy_terrain():

    heightmap = np.zeros((100, 100))

    obstacles = np.zeros((100, 100))

    analyzer = TerrainDifficultyAnalyzer()

    result = analyzer.analyze(
        heightmap,
        obstacles
    )

    assert result.category == "Easy"
    assert result.difficulty_score < 25


def test_obstacle_density():

    heightmap = np.zeros((100, 100))

    obstacles = np.zeros((100, 100))

    obstacles[20:80, 20:80] = 1

    analyzer = TerrainDifficultyAnalyzer()

    result = analyzer.analyze(
        heightmap,
        obstacles
    )

    assert result.obstacle_density > 0.0


def test_traversability_reduction():

    heightmap = np.zeros((100, 100))

    obstacles = np.ones((100, 100))

    analyzer = TerrainDifficultyAnalyzer()

    result = analyzer.analyze(
        heightmap,
        obstacles
    )

    assert result.traversability_score == 0.0


def test_hard_terrain():

    x = np.linspace(
        0,
        50,
        100
    )

    heightmap = np.tile(
        x,
        (100, 1)
    )

    obstacles = np.zeros(
        (100, 100)
    )

    analyzer = TerrainDifficultyAnalyzer()

    result = analyzer.analyze(
        heightmap,
        obstacles
    )

    assert result.difficulty_score > 25


def test_category_bounds():

    analyzer = TerrainDifficultyAnalyzer()

    assert analyzer._difficulty_category(10) == "Easy"
    assert analyzer._difficulty_category(40) == "Medium"
    assert analyzer._difficulty_category(65) == "Hard"
    assert analyzer._difficulty_category(90) == "Extreme"