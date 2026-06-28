from .csv_logger import CSVLogger

class BenchmarkRunner:

    def __init__(
        self,
        world_generator,
        explorer,
        metrics_manager,
        output_csv="generated/reports/benchmark.csv"
    ):

        self.world_generator = world_generator
        self.explorer = explorer
        self.metrics_manager = metrics_manager

        self.csv_logger = CSVLogger(output_csv)

    def run(self, num_worlds=100):

        self.csv_logger.initialize()

        for i in range(num_worlds):

            world = self.world_generator.generate()

            metrics = self.explorer.run(world)

            self.csv_logger.write(
                seed=world.seed,
                difficulty=metrics.difficulty,
                coverage=metrics.coverage,
                time=metrics.time,
                distance=metrics.distance,
                efficiency=metrics.efficiency
            )

        self.csv_logger.close()