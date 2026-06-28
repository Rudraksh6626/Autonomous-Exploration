from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True)
class Obstacle:
    x: float
    y: float
    z: float
    radius: float
    height: float
    obstacle_type: str

    def to_dict(self) -> Dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "radius": self.radius,
            "height": self.height,
            "type": self.obstacle_type
        }