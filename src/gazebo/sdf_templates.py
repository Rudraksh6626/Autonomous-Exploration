CYLINDER_MODEL_TEMPLATE = """
<model name="{name}">
    <static>true</static>

    <pose>
        {x} {y} {z} 0 0 0
    </pose>

    <link name="link">

        <collision name="collision">
            <geometry>
                <cylinder>
                    <radius>{radius}</radius>
                    <length>{height}</length>
                </cylinder>
            </geometry>
        </collision>

        <visual name="visual">
            <geometry>
                <cylinder>
                    <radius>{radius}</radius>
                    <length>{height}</length>
                </cylinder>
            </geometry>
        </visual>

    </link>
</model>
"""