from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from src.core.config import AppSettings
from src.core.di_container import DependencyContainer
from src.server import mcp_server as mcp_module


def install_nltk_deps():
    import nltk
    nltk.download('punkt')


@asynccontextmanager
def lifespan() -> AsyncIterator[None]:
    install_nltk_deps()

    yield


def run() -> None:
    install_nltk_deps()

    settings = AppSettings()
    container = DependencyContainer.create(settings).build()

    mcp_module.mcp.container = container  # type: ignore[attr-defined]
    mcp_module.mcp.lifespan = lifespan

    mcp_module.mcp.run(transport="http", host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
