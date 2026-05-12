import os
from typing import Generator

import pytest

from src.core.config import AppSettings
from src.core.di_container import DependencyContainer


@pytest.fixture
def searxng_env_vars() -> Generator[None, None, None]:
    original = dict(os.environ)
    os.environ["ENGINE_SEARXNG_ENABLED"] = "true"
    os.environ["ENGINE_SEARXNG_TYPE"] = "searxng"
    os.environ["ENGINE_SEARXNG_BASE_URL"] = "http://test-searxng.local"
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


def test_app_settings_loads_from_env(searxng_env_vars: Generator[None, None, None]) -> None:  # noqa: ARG001
    settings = AppSettings()
    assert "SEARXNG" in settings.engines
    engine = settings.engines["SEARXNG"]
    assert engine.enabled is True
    assert engine.type == "searxng"
    assert engine.base_url == "http://test-searxng.local"


def test_dependency_container_build_with_searxng(searxng_env_vars: Generator[None, None, None]) -> None:  # noqa: ARG001
    settings = AppSettings()
    container = DependencyContainer.create(settings).build()

    adapter = container.get_adapter("SEARXNG")
    assert adapter is not None

    content_fetcher = container.get_content_fetcher()
    assert content_fetcher is not None


def test_dependency_container_cached_adapters(searxng_env_vars: Generator[None, None, None]) -> None:  # noqa: ARG001
    settings = AppSettings()
    container = DependencyContainer.create(settings).build()

    adapter1 = container.get_adapter("SEARXNG")
    adapter2 = container.get_adapter("SEARXNG")
    assert adapter1 is adapter2


def test_run_uses_default_engine() -> None:
    settings = AppSettings()
    assert settings.default_engine == "SEARXNG"
