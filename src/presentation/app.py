from src.core.config import AppSettings
from src.core.di_container import DependencyContainer
from src.server import mcp_server as mcp_module


def run() -> None:
    settings = AppSettings()
    container = DependencyContainer.create(settings).build()

    mcp_module.mcp.container = container  # type: ignore[attr-defined]

    mcp_module.mcp.run(transport="http", host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
