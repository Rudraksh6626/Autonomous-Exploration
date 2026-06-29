import logging
import os
import pytest

def test_initialize_logging_and_set_level(tmp_path):
    from core.logger import LoggerSetup

    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    cfg = {"logging": {"level": "INFO", "output_dir": str(log_dir), "file_name": "test.log"}}

    ls = LoggerSetup()
    ls.initialize_logging(cfg)
    logger = ls.get_logger("test_logger")

    # Logger level should be INFO by default per config
    assert logger.getEffectiveLevel() == logging.INFO or logger.level == logging.INFO

    # There should be at least one file handler that writes to test.log
    root_handlers = logging.getLogger().handlers
    assert any("test.log" in getattr(h, "baseFilename", "") for h in root_handlers if hasattr(h, "baseFilename"))

    # Changing level via set_level should affect the logger
    ls.set_level("DEBUG")
    assert logger.getEffectiveLevel() == logging.DEBUG

    # cleanup
    ls.close()

def test_initialize_logging_dir_not_writable(tmp_path, monkeypatch):
    from core.logger import LoggerSetup
    # Simulate an unwritable directory by creating a dir and removing write perms (platform dependent)
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    # On some systems changing permissions in CI is unreliable; monkeypatch handler creation to raise
    original_init = logging.FileHandler

    def fake_filehandler(*args, **kwargs):
        raise PermissionError("no write permission")

    monkeypatch.setattr("logging.handlers.RotatingFileHandler", fake_filehandler)
    ls = LoggerSetup()
    cfg = {"logging": {"level": "INFO", "output_dir": str(log_dir), "file_name": "test.log"}}
    # Should not crash the test runner; the module should handle handler creation errors gracefully.
    ls.initialize_logging(cfg)
    ls.close()
    # restore not required because monkeypatch fixture reverts automatically
