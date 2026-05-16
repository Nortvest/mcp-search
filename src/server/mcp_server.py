import logging
from typing import TYPE_CHECKING

from fastmcp import Context, FastMCP
from fastmcp.server.dependencies import CurrentContext
from mcp.types import Icon

from src.domain.models import SearchQuery
from src.server.schemas import GetResultOutput, SearchBatchOutput, SearchInput, SearchOutput
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
async def search(
    query: SearchInput,

    ctx: Context = CurrentContext(),  # noqa: B008
) -> SearchOutput:
    logging.getLogger("mcp-search").info(
        f"Search by {query.query=}. {query.language=}. {query.categories=}. {query.num_results=}",
    )

    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    search_adapter = container.get_adapter(container.settings.default_engine)
    service = SearchService(adapter=search_adapter)

    item = SearchQuery(
        query=query.query,
        language=query.language,
        categories=query.categories,
        engine=query.engine or "",
        num_results=query.num_results,
    )

    results = await service.search(item)
    return SearchOutput(results=results)


@mcp.tool(
    name="search_batch",
    description="Search the internet using a configured search engine with multiple queries at once.",
    icons=[Icon(src="https://docs.searxng.org/_static/searxng-wordmark.svg", mimeType="image/svg+xml")],
)
async def search_batch(
    queries: list[SearchInput],

    ctx: Context = CurrentContext(),  # noqa: B008
) -> SearchBatchOutput:
    logging.getLogger("mcp-search").info(f"Batch search with {len(queries)} queries")

    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    search_adapter = container.get_adapter(container.settings.default_engine)
    service = SearchService(adapter=search_adapter)

    batch_items = [
        SearchQuery(
            query=q.query,
            language=q.language,
            categories=q.categories,
            engine=q.engine or "",
            num_results=q.num_results,
        )
        for q in queries
    ]
    results = await service.search_batch(queries=batch_items)
    return SearchBatchOutput(results=results)


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


@mcp.tool(
    name="fetch_and_summarize_website",
    description="Fetch content from a URL and return a concise summary.",
)
async def fetch_and_summarize_website(
    url: str,

    ctx: Context = CurrentContext(),  # noqa: B008
) -> GetResultOutput:
    logging.getLogger("mcp-search").info(f"Fetch and Summarize Website {url}")

    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    content_fetcher = container.get_content_fetcher()
    summarized_content_fetcher = container.get_summarized_content_fetcher()
    service = ContentFetchService(
        content_fetcher=content_fetcher,
        summarized_content_fetcher=summarized_content_fetcher,
    )

    content = await service.summarize_fetch(url=url)
    return GetResultOutput(url=content.url, title=content.title, text=content.text)
