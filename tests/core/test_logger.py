import logging

import pytest

from src.core.logger import setup_logger


class TestSetupLogger:
    def test_returns_logger(self) -> None:
        logger = setup_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "mcp-search"

    def test_default_level_is_info(self) -> None:
        logger = setup_logger()
        assert logger.level == logging.INFO

    def test_custom_level(self) -> None:
        logger = setup_logger(level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_warning_messages_pass(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level("INFO", logger="mcp-search"):
            logger = setup_logger()
            logger.warning("test warning")
            assert "test warning" in caplog.text

    def test_handler_configured(self) -> None:
        logger = setup_logger()
        handlers = logger.handlers
        stream_handlers = [h for h in handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) >= 1
