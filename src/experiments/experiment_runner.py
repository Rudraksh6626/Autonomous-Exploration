class ExperimentRunner:

    def __init__(
        self,
        launcher,
        metrics_manager
    ):

        self.launcher = launcher
        self.metrics_manager = metrics_manager

    def run(self, world):

        self.launcher.launch(world)

        return self.metrics_manager.collect()