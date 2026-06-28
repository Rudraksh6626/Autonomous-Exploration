class ParameterSweep:

    def execute(self):

        terrain_scales = [1,2,3,4]
        obstacle_counts = [10,20,30]

        for scale in terrain_scales:
            for obstacles in obstacle_counts:

                yield {
                    "scale": scale,
                    "obstacles": obstacles
                }