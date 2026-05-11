import pytest

from src.core.config import AppSettings


@pytest.fixture
def settings() -> AppSettings:
    return AppSettings(
        host="127.0.0.1",
        port=9999,
        log_level="DEBUG",
    )


@pytest.fixture
def searxng_settings() -> AppSettings:
    return AppSettings(
        host="127.0.0.1",
        port=9999,
        log_level="DEBUG",
        request_timeout=5.0,
        max_content_length=100000,
    )
