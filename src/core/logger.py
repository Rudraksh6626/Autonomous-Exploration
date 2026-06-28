"""
Logging configuration and setup for the Autonomous Exploration pipeline.
Provides centralized logging with file and console output.
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any


class LoggerSetup:
    """
    Manages logging configuration for the entire pipeline.
    Supports both console and file output with configurable levels.
    """

    def __init__(self):
        """Initialize the logger setup manager."""
        self.logger = None
        self.log_level = logging.INFO

    def initialize_logging(self, config: Dict[str, Any]) -> None:
        """
        Initialize logging based on configuration.
        
        Args:
            config: Configuration dictionary containing logging settings
                Expected keys:
                - logging.level: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
                - logging.output_dir: Directory for log files
                - logging.file_name: Name of log file
        """
        logging_config = config.get('logging', {})
        
        # Determine log level
        level_name = logging_config.get('level', 'INFO').upper()
        self.log_level = getattr(logging, level_name, logging.INFO)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if output directory specified)
        output_dir = logging_config.get('output_dir', './logs')
        if output_dir:
            log_dir = Path(output_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = logging_config.get('file_name', 'autonomous_exploration.log')
            log_path = log_dir / log_file
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logging initialized successfully")

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.
        
        Args:
            name: Logger name (typically __name__ of calling module)
            
        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)

    def set_level(self, level: str) -> None:
        """
        Set logging level for all handlers.
        
        Args:
            level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        level_name = level.upper()
        log_level = getattr(logging, level_name, logging.INFO)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        for handler in root_logger.handlers:
            handler.setLevel(log_level)
        
        self.log_level = log_level

    def close(self) -> None:
        """Close all logging handlers."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
