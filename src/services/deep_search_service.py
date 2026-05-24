import asyncio
import logging
from typing import TYPE_CHECKING

from src.core.exceptions import MaxContentLengthError
from src.domain.models import ContentResult, SearchBatchResult, SearchQuery, SearchResult
from src.services.content_service import ContentFetchService
from src.services.search_service import SearchService

if TYPE_CHECKING:
    from fastmcp import Context


class DeepSearchService:
    def __init__(self, search_service: SearchService, content_service: ContentFetchService) -> None:
        self._search_service = search_service
        self._content_service = content_service

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger("mcp-search")

    async def search(self, query: SearchQuery, ctx: "Context | None" = None) -> list[SearchResult]:
        search_results = await self._search_service.search(query)

        total = len(search_results)
        self._logger.debug(f"DeepSearchService.search start {total=}")

        if ctx:
            await ctx.report_progress(progress=0, total=total)

        tasks = [self._fetch_content_safe(result.url) for result in search_results]
        contents = await asyncio.gather(*tasks)

        enriched: list[SearchResult] = []
        for i, (search_result, content) in enumerate(zip(search_results, contents, strict=True)):
            if ctx:
                self._logger.debug(f"DeepSearchService.search complete {i + 1} / {total}")
                await ctx.report_progress(progress=i + 1, total=total)
            if content:
                enriched.append(
                    SearchResult(
                        title=search_result.title,
                        url=search_result.url,
                        snippet=f"{search_result.snippet}\n\n{content.text}",
                    ),
                )
            else:
                enriched.append(search_result)

        self._logger.debug(f"DeepSearchService.search complete {len(enriched)=}")
        return enriched

    async def search_batch(self, queries: list[SearchQuery], ctx: "Context | None" = None) -> list[SearchBatchResult]:
        total = len(queries)
        tasks = [self._deep_search_one(item, ctx) for item in queries]
        gathered = await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.debug(f"DeepSearchService.search_batch start {total=}")

        if ctx:
            await ctx.report_progress(progress=0, total=total)

        results: list[SearchBatchResult] = []
        for i, (item, result) in enumerate(zip(queries, gathered, strict=True)):
            if ctx:
                self._logger.debug(f"DeepSearchService.search_batch complete {i + 1} / {total}")
                await ctx.report_progress(progress=i + 1, total=total)
            results.append(self._process_batch_result(item, result))

        self._logger.debug(f"DeepSearchService.search_batch complete {len(results)=}")
        return results

    @staticmethod
    def _process_batch_result(item: SearchQuery, result: object) -> SearchBatchResult:
        if isinstance(result, SearchBatchResult):
            return result
        return SearchBatchResult(query=item.query, results=[], error=str(result))

    async def _fetch_content_safe(self, url: str) -> ContentResult | None:
        try:
            return await self._content_service.summarize_fetch(url=url)
        except MaxContentLengthError as e:
            self._logger.warning(str(e))
        except Exception:
            self._logger.exception(f"Failed to fetch content from {url=}")

        return None

    async def _deep_search_one(self, item: SearchQuery, ctx: "Context | None" = None) -> SearchBatchResult:
        enriched = await self.search(query=item, ctx=ctx)
        return SearchBatchResult(query=item.query, results=enriched)
