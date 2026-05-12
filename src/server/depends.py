from typing import Annotated

from fastmcp import Context
from fastmcp.dependencies import Depends

from src.core.di_container import DependencyContainer
from src.services.content_service import ContentFetchService
from src.services.search_service import SearchService


def get_dependency_container(ctx: Context) -> DependencyContainer:
    return ctx.fastmcp.container  # type: ignore[no-any-return, attr-defined]


def get_search_service(
    container: Annotated[DependencyContainer, Depends(get_dependency_container)],
) -> SearchService:
    search_adapter = container.get_adapter(container.settings.default_engine)
    return SearchService(adapter=search_adapter)


def get_content_fetcher(
    container: Annotated[DependencyContainer, Depends(get_dependency_container)],
) -> ContentFetchService:
    content_fetcher = container.get_content_fetcher()
    return ContentFetchService(content_fetcher=content_fetcher)
