import asyncio
import logging

from src.core.exceptions import MaxContentLengthError
from src.domain.models import ContentResult, SearchBatchResult, SearchQuery, SearchResult
from src.services.content_service import ContentFetchService
from src.services.search_service import SearchService


class DeepSearchService:
    def __init__(self, search_service: SearchService, content_service: ContentFetchService) -> None:
        self._search_service = search_service
        self._content_service = content_service

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger("mcp-search")

    async def search(self, query: SearchQuery) -> list[SearchResult]:
        search_results = await self._search_service.search(query)

        tasks = [self._fetch_content_safe(result.url) for result in search_results]
        contents = await asyncio.gather(*tasks)

        enriched: list[SearchResult] = []
        for search_result, content in zip(search_results, contents, strict=True):
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

        return enriched

    async def search_batch(self, queries: list[SearchQuery]) -> list[SearchBatchResult]:
        tasks = [self._deep_search_one(item) for item in queries]
        gathered = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[SearchBatchResult] = []
        for item, result in zip(queries, gathered, strict=True):
            if isinstance(result, SearchBatchResult):
                results.append(result)
            elif isinstance(result, ValueError):
                results.append(SearchBatchResult(query=item.query, results=[], error=str(result)))
            else:
                results.append(SearchBatchResult(query=item.query, results=[], error=str(result)))

        return results

    async def _fetch_content_safe(self, url: str) -> ContentResult | None:
        try:
            return await self._content_service.summarize_fetch(url=url)
        except MaxContentLengthError as e:
            self._logger.warning(str(e))
        except Exception:
            self._logger.exception("Failed to fetch content from url")

        return None

    async def _deep_search_one(self, item: SearchQuery) -> SearchBatchResult:
        enriched = await self.search(query=item)
        return SearchBatchResult(query=item.query, results=enriched)
