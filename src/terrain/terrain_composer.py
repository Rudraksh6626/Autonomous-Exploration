import numpy as np

try:
    from scipy.ndimage import gaussian_filter
except ImportError:
    gaussian_filter = None


class TerrainComposer:

    def __init__(
        self,
        normalize=True,
        smoothing=False,
        smoothing_sigma=1.0
    ):
        self.normalize_output = normalize
        self.smoothing = smoothing
        self.smoothing_sigma = smoothing_sigma
        self.generators = []

    def add_generator(
        self,
        generator,
        weight=1.0
    ):

        if weight <= 0:
            raise ValueError(
                "Weight must be positive."
            )

        self.generators.append(
            (
                generator,
                float(weight)
            )
        )

    def compose(self):

        if not self.generators:
            raise ValueError(
                "No terrain generators added."
            )

        total_weight = sum(
            weight
            for _, weight in self.generators
        )

        if total_weight <= 0:
            raise ValueError(
                "Total weight must be positive."
            )

        expected_shape = None
        combined = None

        for generator, weight in self.generators:

            terrain = generator.generate()

            if not isinstance(
                terrain,
                np.ndarray
            ):
                raise TypeError(
                    f"{generator.__class__.__name__} "
                    "must return a numpy.ndarray."
                )

            if expected_shape is None:

                expected_shape = terrain.shape

            elif terrain.shape != expected_shape:

                raise ValueError(
                    "All terrain generators must "
                    "produce heightmaps of the same shape. "
                    f"Expected {expected_shape}, "
                    f"got {terrain.shape}."
                )

            normalized_weight = (
                weight / total_weight
            )

            terrain = terrain.astype(
                np.float32
            )

            if combined is None:

                combined = (
                    terrain *
                    normalized_weight
                )

            else:

                combined += (
                    terrain *
                    normalized_weight
                )

        if self.smoothing:
            combined = self._smooth(
                combined
            )

        if self.normalize_output:
            combined = self._normalize(
                combined
            )

        return combined

    def _normalize(
        self,
        terrain
    ):

        minimum = np.min(
            terrain
        )

        maximum = np.max(
            terrain
        )

        if maximum - minimum == 0:

            return np.zeros_like(
                terrain,
                dtype=np.float32
            )

        return (
            terrain - minimum
        ) / (
            maximum - minimum
        )

    def _smooth(
        self,
        terrain
    ):

        if gaussian_filter is None:

            raise ImportError(
                "scipy is required "
                "for terrain smoothing."
            )

        return gaussian_filter(
            terrain,
            sigma=self.smoothing_sigma
        )