import csv
from pathlib import Path


class CSVLogger:

    HEADER = [
        "seed",
        "difficulty",
        "coverage",
        "time",
        "distance",
        "efficiency"
    ]

    def __init__(self, filename):

        self.filename = Path(filename)

        self.filename.parent.mkdir(parents=True, exist_ok=True)

        self.file = None
        self.writer = None

    def initialize(self):

        self.file = open(self.filename, "w", newline="")

        self.writer = csv.writer(self.file)

        self.writer.writerow(self.HEADER)

    def write(
        self,
        seed,
        difficulty,
        coverage,
        time,
        distance,
        efficiency
    ):

        self.writer.writerow([
            seed,
            difficulty,
            coverage,
            time,
            distance,
            efficiency
        ])

    def close(self):

        if self.file:
            self.file.close()