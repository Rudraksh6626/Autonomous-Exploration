from pathlib import Path

import numpy as np

try:
    from PIL import Image
except ImportError:
    Image = None


class HeightmapExporter:

    @staticmethod
    def export_png(
        heightmap,
        output_path
    ):

        if Image is None:
            raise ImportError(
                "Pillow is required."
            )

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        minimum = np.min(heightmap)
        maximum = np.max(heightmap)

        if maximum - minimum == 0:

            normalized = np.zeros_like(
                heightmap,
                dtype=np.uint8
            )

        else:

            normalized = (
                (
                    heightmap - minimum
                )
                /
                (
                    maximum - minimum
                )
                * 255
            ).astype(np.uint8)

        image = Image.fromarray(
            normalized
        )

        image.save(
            output_path
        )

    @staticmethod
    def export_npy(
        heightmap,
        output_path
    ):

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        np.save(
            output_path,
            heightmap
        )

    @staticmethod
    def export_csv(
        heightmap,
        output_path
    ):

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        np.savetxt(
            output_path,
            heightmap,
            delimiter=","
        )

    @staticmethod
    def export_all(
        heightmap,
        output_directory
    ):

        output_directory = Path(
            output_directory
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        HeightmapExporter.export_png(
            heightmap,
            output_directory / "terrain.png"
        )

        HeightmapExporter.export_npy(
            heightmap,
            output_directory / "terrain.npy"
        )

        HeightmapExporter.export_csv(
            heightmap,
            output_directory / "terrain.csv"
        )