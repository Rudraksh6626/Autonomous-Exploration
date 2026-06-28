class WorldBuilder:

    def __init__(self):

        self.obstacles = []

    def add_obstacles(self, obstacles):

        self.obstacles.extend(obstacles)

    def build(self):

        return {
            "obstacles": self.obstacles
        }