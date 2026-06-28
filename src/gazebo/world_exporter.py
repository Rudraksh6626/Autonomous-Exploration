from pathlib import Path


class GazeboWorldExporter:

    def export(
        self,
        image_path,
        world_path,
        obstacles
    ):

        world_xml = self._build_world(
            image_path,
            obstacles
        )

        world_path = Path(
            world_path
        )

        world_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        world_path.write_text(
            world_xml,
            encoding="utf-8"
        )

    def _build_world(
        self,
        image_path,
        obstacles
    ):

        obstacle_xml = "\n".join(
            self._build_obstacle(obstacle)
            for obstacle in obstacles
        )

        return f"""<?xml version="1.0" ?>
<sdf version="1.7">

    <world name="generated_world">

        <include>
            <uri>model://sun</uri>
        </include>

        <include>
            <uri>model://ground_plane</uri>
        </include>

        <model name="terrain">

            <static>true</static>

            <link name="terrain_link">

                <collision name="terrain_collision">

                    <geometry>

                        <heightmap>

                            <uri>{image_path}</uri>

                            <size>100 100 20</size>

                        </heightmap>

                    </geometry>

                </collision>

                <visual name="terrain_visual">

                    <geometry>

                        <heightmap>

                            <uri>{image_path}</uri>

                            <size>100 100 20</size>

                        </heightmap>

                    </geometry>

                </visual>

            </link>

        </model>

{obstacle_xml}

    </world>

</sdf>
"""

    def _build_obstacle(
        self,
        obstacle
    ):

        return f"""
        <model name="{obstacle.obstacle_type}_{int(obstacle.x)}_{int(obstacle.y)}">

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

        </model>
"""