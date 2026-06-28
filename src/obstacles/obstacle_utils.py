from typing import List
import numpy as np

from .obstacle_models import Obstacle


def distance(
    x1: float,
    y1: float,
    x2: float,
    y2: float
) -> float:
    return float(np.hypot(x1 - x2, y1 - y2))


def valid_position(
    x: float,
    y: float,
    slope_map: np.ndarray,
    obstacles: List[Obstacle],
    min_spacing: float,
    spawn: tuple[float, float],
    goal: tuple[float, float],
    exclusion_radius: float = 5.0,
    max_slope: float = 0.4
) -> bool:

    rows, cols = slope_map.shape

    if x < 0 or y < 0:
        return False

    if x >= cols or y >= rows:
        return False

    if slope_map[int(y), int(x)] > max_slope:
        return False

    if distance(x, y, *spawn) < exclusion_radius:
        return False

    if distance(x, y, *goal) < exclusion_radius:
        return False

    for obstacle in obstacles:
        if distance(
            x,
            y,
            obstacle.x,
            obstacle.y
        ) < min_spacing:
            return False

    return True


def compute_slope_map(
    heightmap: np.ndarray
) -> np.ndarray:

    gx, gy = np.gradient(heightmap)

    return np.sqrt(gx ** 2 + gy ** 2)