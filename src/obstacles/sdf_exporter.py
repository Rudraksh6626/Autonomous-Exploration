from typing import List

from .obstacle_models import Obstacle


class SDFObstacleExporter:

    @staticmethod
    def export(
        obstacles: List[Obstacle]
    ) -> str:

        models = []

        for i, obstacle in enumerate(obstacles):

            models.append(
                f"""
<sdf version="1.7" name="{obstacle.obstacle_type}_{i}">
  <static>true</static>
  <pose>
    {obstacle.x}
    {obstacle.y}
    {obstacle.z}
    0 0 0
  </pose>

  <link name="link">

    <collision name="collision">
      <geometry>
        <cylinder>
          <radius>{obstacle.radius}</radius>
          <length>{obstacle.height}</length>
        </cylinder>
      </geometry>
    </collision>

    <visual name="visual">
      <geometry>
        <cylinder>
          <radius>{obstacle.radius}</radius>
          <length>{obstacle.height}</length>
        </cylinder>
      </geometry>
    </visual>

  </link>
</sdf>
"""
            )

        return "\n".join(models)