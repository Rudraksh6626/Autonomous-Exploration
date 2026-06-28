"""
Configuration management for the Autonomous Exploration pipeline.
Handles loading and validation of YAML/JSON configuration files.
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """
    Manages configuration loading and validation.
    Supports both YAML and JSON configuration file formats.
    """

    def __init__(self):
        """Initialize the configuration manager."""
        self.config = None

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file (YAML or JSON).
        
        Args:
            config_path: Path to configuration file (.yaml, .yml, or .json)
            
        Returns:
            Dictionary containing loaded configuration
            
        Raises:
            FileNotFoundError: If configuration file does not exist
            ValueError: If file format is unsupported or parsing fails
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            if path.suffix.lower() in ['.yaml', '.yml']:
                with open(path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported configuration format: {path.suffix}. "
                    "Expected .yaml, .yml, or .json"
                )
            
            return self.config
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse configuration file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key path.
        
        Args:
            key: Configuration key (supports dot notation: 'terrain_settings.seed')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if self.config is None:
            return default
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

    def validate(self, required_keys: list) -> bool:
        """
        Validate that configuration contains all required top-level keys.
        
        Args:
            required_keys: List of required configuration keys
            
        Returns:
            True if all required keys present
            
        Raises:
            ValueError: If any required key is missing
        """
        if self.config is None:
            raise ValueError("No configuration loaded")
        
        missing = [k for k in required_keys if k not in self.config]
        if missing:
            raise ValueError(f"Missing required configuration keys: {missing}")
        
        return True
