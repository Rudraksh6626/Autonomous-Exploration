"""
Factory for creating obstacle generator instances from configuration.
Manages instantiation of obstacle generators by type name with configurable parameters.
"""
import logging
from typing import Any, List


logger = logging.getLogger(__name__)


class ObstacleFactory:
    """
    Factory for creating obstacle generator instances.
    Provides type-safe instantiation of registered obstacle generators.
    """

    # Registry of available obstacle generators
    _registry = {}

    @classmethod
    def register(cls, name: str, generator_class):
        """
        Register an obstacle generator class by name.

        Args:
            name: The name to register the generator under (e.g., 'barrier_wall', 'forest_cluster')
            generator_class: The generator class to register
        """
        cls._registry[name] = generator_class
        logger.debug(f"Registered obstacle generator: {name} -> {generator_class.__name__}")

    @classmethod
    def create(cls, generator_type: str, **kwargs):
        """
        Create an obstacle generator instance by type name.

        Args:
            generator_type: Name of the generator type
            **kwargs: Parameters to pass to the generator constructor

        Returns:
            An instance of the requested obstacle generator

        Raises:
            ValueError: If the generator type is not registered
        """
        if generator_type not in cls._registry:
            raise ValueError(
                f"Unknown obstacle generator type: '{generator_type}'. "
                f"Available types: {list(cls._registry.keys())}"
            )

        generator_class = cls._registry[generator_type]
        logger.debug(f"Creating obstacle generator: {generator_type}")

        return generator_class(**kwargs)

    @classmethod
    def list_available(cls) -> List[str]:
        """
        Get list of available obstacle generator types.

        Returns:
            List of registered generator type names
        """
        return list(cls._registry.keys())

    @classmethod
    def from_config(cls, config: dict) -> List[Any]:
        """
        Create obstacle generators from configuration dictionary.

        Args:
            config: Configuration dict with format:
                {
                    "obstacles": [
                        {"type": "barrier_wall", "parameters": {...}},
                        {"type": "forest_cluster", "parameters": {...}}
                    ]
                }

        Returns:
            List of obstacle generator instances

        Raises:
            ValueError: If configuration is invalid or generator creation fails
        """
        obstacles_config = config.get("obstacles", [])

        if not obstacles_config:
            logger.warning("No obstacle generators specified in configuration")
            return []

        generators = []

        for obs_config in obstacles_config:
            obs_type = obs_config.get("type")
            params = obs_config.get("parameters", {})

            if not obs_type:
                raise ValueError("Obstacle generator config missing 'type' key")

            try:
                generator = cls.create(obs_type, **params)
                generators.append(generator)
                logger.info(f"Loaded obstacle generator: {obs_type}")
            except ValueError as e:
                logger.error(f"Failed to create obstacle generator '{obs_type}': {e}")
                raise

        return generators
