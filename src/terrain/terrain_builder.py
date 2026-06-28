from terrain.terrain_composer import TerrainComposer


class TerrainBuilder:

    def __init__(self):

        self.composer = TerrainComposer()

    def add(
        self,
        generator,
        weight=1.0
    ):

        self.composer.add_generator(
            generator,
            weight
        )

        return self

    def enable_smoothing(
        self,
        sigma=1.0
    ):

        self.composer.smoothing = True
        self.composer.smoothing_sigma = sigma

        return self

    def disable_normalization(self):

        self.composer.normalize_output = False

        return self

    def build(self):

        return self.composer.compose()