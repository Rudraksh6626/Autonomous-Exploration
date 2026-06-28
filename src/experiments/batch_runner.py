class BatchRunner:

    def __init__(self, benchmark_runner):

        self.benchmark_runner = benchmark_runner

    def run(self, worlds=100):

        self.benchmark_runner.run(worlds)