from typing import TYPE_CHECKING, Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from mcp.types import Icon

from src.server.schemas import GetResultOutput, SearchOutput
from src.server.depends import get_content_fetcher, get_search_service

if TYPE_CHECKING:
    from src.services.content_service import ContentFetchService
    from src.services.search_service import SearchService


mcp = FastMCP("mcp-search")


@mcp.tool(
    name="search",
    description="Search the internet using a configured search engine.",
    icons=[Icon(src="https://docs.searxng.org/_static/searxng-wordmark.svg")],
)
async def search(  # noqa: PLR0913 PLR0917
    service: Annotated["SearchService", Depends(get_search_service)],

    query: str,
    language: str = "en",
    categories: str = "general",
    engine: str | None = None,
    num_results: int = 10,
) -> SearchOutput:
    results = await service.search(
        query=query, engine=engine, num_results=num_results, language=language, categories=categories,
    )
    return SearchOutput(results=results)


@mcp.tool(
    name="fetch_website",
    description="Fetch full content from a URL returned by search.",
)
async def fetch_website(
    service: Annotated["ContentFetchService", get_content_fetcher],

    url: str,
) -> GetResultOutput:

    content = await service.fetch(url=url)
    return GetResultOutput(url=content.url, title=content.title, text=content.text)
