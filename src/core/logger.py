import logging
import sys


def setup_logger(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("mcp-search")
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
