import logging
from typing import TYPE_CHECKING

from fastmcp import Context, FastMCP
from fastmcp.server.dependencies import CurrentContext
from mcp.types import Icon

from src.server.schemas import GetResultOutput, SearchOutput
from src.services.content_service import ContentFetchService
from src.services.search_service import SearchService

if TYPE_CHECKING:
    from src.core.di_container import DependencyContainer

mcp = FastMCP("mcp-search")


@mcp.tool(
    name="search",
    description="Search the internet using a configured search engine.",
    icons=[Icon(src="https://docs.searxng.org/_static/searxng-wordmark.svg", mimeType="image/svg+xml")],
)
async def search(  # noqa: PLR0913 PLR0917
    query: str,
    language: str = "en",
    categories: str = "general",
    engine: str | None = None,
    num_results: int = 10,

    ctx: Context = CurrentContext(),  # noqa: B008
) -> SearchOutput:
    logging.getLogger("mcp-search").info(f"Search by {query=}. {language=}. {categories=}. {num_results=}")

    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    search_adapter = container.get_adapter(container.settings.default_engine)
    service = SearchService(adapter=search_adapter)

    results = await service.search(
        query=query, engine=engine, num_results=num_results, language=language, categories=categories,
    )
    return SearchOutput(results=results)


@mcp.tool(
    name="fetch_website",
    description="Fetch full content from a URL returned by search.",
)
async def fetch_website(
    url: str,

    ctx: Context = CurrentContext(),  # noqa: B008
) -> GetResultOutput:
    logging.getLogger("mcp-search").info(f"Fetch Website {url}")

    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    content_fetcher = container.get_content_fetcher()
    service = ContentFetchService(content_fetcher=content_fetcher)

    content = await service.fetch(url=url)
    return GetResultOutput(url=content.url, title=content.title, text=content.text)
