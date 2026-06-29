"""
Factory for creating terrain generator instances from configuration.
Supports instantiation of terrain generators by name with configurable parameters.
"""
import logging
from typing import Any, List, Tuple


logger = logging.getLogger(__name__)


class TerrainFactory:
    """
    Factory for creating terrain generator instances.
    Currently provides a placeholder interface since concrete terrain generators
    are not yet implemented in the codebase.
    """

    # Registry of available terrain generators (to be populated as implementations are added)
    _registry = {}

    @classmethod
    def register(cls, name: str, generator_class):
        """
        Register a terrain generator class by name.

        Args:
            name: The name to register the generator under (e.g., 'perlin', 'ridged')
            generator_class: The generator class to register
        """
        cls._registry[name] = generator_class
        logger.debug(f"Registered terrain generator: {name} -> {generator_class.__name__}")

    @classmethod
    def create(cls, generator_type: str, size: int = 256, **kwargs):
        """
        Create a terrain generator instance by type name.

        Args:
            generator_type: Name of the generator type (e.g., 'perlin', 'ridged')
            size: Size of the heightmap to generate (default 256)
            **kwargs: Additional parameters to pass to the generator

        Returns:
            An instance of the requested terrain generator

        Raises:
            ValueError: If the generator type is not registered
        """
        if generator_type not in cls._registry:
            raise ValueError(
                f"Unknown terrain generator type: '{generator_type}'. "
                f"Available types: {list(cls._registry.keys())}"
            )

        generator_class = cls._registry[generator_type]
        logger.debug(f"Creating terrain generator: {generator_type} (size={size})")

        # Instantiate with size as default parameter, allow kwargs to override
        return generator_class(size=size, **kwargs)

    @classmethod
    def list_available(cls) -> List[str]:
        """
        Get list of available terrain generator types.

        Returns:
            List of registered generator type names
        """
        return list(cls._registry.keys())

    @classmethod
    def from_config(cls, config: dict) -> List[Tuple[Any, float]]:
        """
        Create terrain generators from configuration dictionary.

        Args:
            config: Configuration dict with format:
                {
                    "generators": [
                        {"name": "perlin", "weight": 0.7, "size": 256, ...},
                        {"name": "ridged", "weight": 0.3, ...}
                    ]
                }

        Returns:
            List of (generator_instance, weight) tuples

        Raises:
            ValueError: If configuration is invalid or generator creation fails
        """
        generators_config = config.get("generators", [])

        if not generators_config:
            logger.warning("No terrain generators specified in configuration")
            return []

        generators = []

        for gen_config in generators_config:
            name = gen_config.get("name")
            weight = gen_config.get("weight", 1.0)
            size = gen_config.get("size", 256)
            params = gen_config.get("parameters", {})

            if not name:
                raise ValueError("Terrain generator config missing 'name' key")

            if weight <= 0:
                raise ValueError(f"Terrain generator weight must be positive, got {weight}")

            try:
                generator = cls.create(name, size=size, **params)
                generators.append((generator, weight))
                logger.info(f"Loaded terrain generator: {name} (weight={weight})")
            except ValueError as e:
                logger.error(f"Failed to create terrain generator '{name}': {e}")
                raise

        return generators
