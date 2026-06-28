import pytest

from terrain.terrain_composer import TerrainComposer

from terrain.terrain_types import (
    MountainTerrain,
    HillTerrain,
    ValleyTerrain
)


def test_weighted_composition():

    composer = TerrainComposer()

    composer.add_generator(
        MountainTerrain(size=64),
        weight=0.5
    )

    composer.add_generator(
        HillTerrain(size=64),
        weight=0.3
    )

    composer.add_generator(
        ValleyTerrain(size=64),
        weight=0.2
    )

    terrain = composer.compose()

    assert terrain.shape == (
        64,
        64
    )


def test_normalization():

    composer = TerrainComposer(
        normalize=True
    )

    composer.add_generator(
        MountainTerrain(size=64),
        weight=1.0
    )

    terrain = composer.compose()

    assert terrain.min() >= 0.0
    assert terrain.max() <= 1.0


def test_empty_composer():

    composer = TerrainComposer()

    with pytest.raises(
        ValueError
    ):
        composer.compose()


def test_invalid_weight():

    composer = TerrainComposer()

    with pytest.raises(
        ValueError
    ):

        composer.add_generator(
            MountainTerrain(size=64),
            weight=0
        )


def test_shape_validation():

    composer = TerrainComposer()

    composer.add_generator(
        MountainTerrain(size=64),
        weight=1.0
    )

    composer.add_generator(
        HillTerrain(size=128),
        weight=1.0
    )

    with pytest.raises(
        ValueError
    ):
        composer.compose()