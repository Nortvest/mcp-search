import logging
from typing import TYPE_CHECKING

from fastmcp import Context, FastMCP
from fastmcp.server.dependencies import CurrentContext

from src.domain.models import SearchQuery
from src.server.schemas import GetResultOutput, SearchBatchOutput, SearchInput, SearchOutput

if TYPE_CHECKING:
    from src.core.di_container import DependencyContainer
    from src.services.content_service import ContentFetchService
    from src.services.deep_search_service import DeepSearchService
    from src.services.search_service import SearchService

mcp = FastMCP("mcp-search")


@mcp.tool(
    name="search",
    description="Search the internet using a configured search engine.",
)
async def search(
    item: SearchInput,

    ctx: Context = CurrentContext(),  # noqa: B008
) -> SearchOutput:
    logging.getLogger("mcp-search").info(
        f"Search by {item.query=}. {item.language=}. {item.categories=}. {item.num_results=}",
    )

    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    service: "SearchService" = container.get_search_service()

    item_dto = SearchQuery(
        query=item.query,
        language=item.language,
        categories=item.categories,
        engine=item.engine or "",
        num_results=item.num_results,
    )

    results = await service.search(item_dto)
    return SearchOutput(results=results)


@mcp.tool(
    name="search_batch",
    description="Search the internet using a configured search engine with multiple queries at once.",
)
async def search_batch(
    queries: list[SearchInput],

    ctx: Context = CurrentContext(),  # noqa: B008
) -> SearchBatchOutput:
    logging.getLogger("mcp-search").info(f"Batch search with {len(queries)} queries")

    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    service: "SearchService" = container.get_search_service()

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
    service: "ContentFetchService" = container.get_content_fetch_service()

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
    service = container.get_content_fetch_service_with_summarize()

    content = await service.summarize_fetch(url=url)
    return GetResultOutput(url=content.url, title=content.title, text=content.text)


@mcp.tool(
    name="deep_search",
    description="Search the internet and fetch+summarize content from top results for deeper analysis.",
)
async def deep_search(
    item: SearchInput,

    ctx: Context = CurrentContext(),  # noqa: B008
) -> SearchOutput:
    logging.getLogger("mcp-search").info(
        f"Deep search by {item.query=}. "
        f"{item.language=}. "
        f"{item.categories=}. "
        f"{item.num_results=}",
    )

    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    deep_search_service: "DeepSearchService" = container.get_deep_search_service()

    item_dto = SearchQuery(
        query=item.query,
        language=item.language,
        categories=item.categories,
        engine=item.engine or "",
        num_results=item.num_results,
    )

    results = await deep_search_service.search(item_dto, ctx=ctx)
    return SearchOutput(results=results)


@mcp.tool(
    name="deep_search_batch",
    description="Deep search with multiple queries — searches and fetches+summarizes content from top results.",
)
async def deep_search_batch(
    queries: list[SearchInput],

    ctx: Context = CurrentContext(),  # noqa: B008
) -> SearchBatchOutput:
    logger = logging.getLogger("mcp-search")
    logger.info(f"Deep batch search with {len(queries)} queries")

    container: "DependencyContainer" = ctx.fastmcp.container  # type: ignore[attr-defined]
    deep_search_service: "DeepSearchService" = container.get_deep_search_service()

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
    results = await deep_search_service.search_batch(queries=batch_items, ctx=ctx)
    return SearchBatchOutput(results=results)
