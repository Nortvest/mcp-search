from typing import TYPE_CHECKING

from fastmcp import Context

from src.services.content_service import ContentFetchService
from src.services.search_service import SearchService

if TYPE_CHECKING:
    from src.core.di_container import DependencyContainer


async def get_search_service(
    ctx: Context,
) -> SearchService:
    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    search_adapter = container.get_adapter(container.settings.default_engine)
    return SearchService(adapter=search_adapter)


async def get_content_fetcher(
    ctx: Context,
) -> ContentFetchService:
    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    content_fetcher = container.get_content_fetcher()
    return ContentFetchService(content_fetcher=content_fetcher)
