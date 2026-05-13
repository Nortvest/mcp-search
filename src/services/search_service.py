import asyncio

from src.adapters.base import SearchEngineAdapter
from src.domain.models import SearchBatchResult, SearchQuery, SearchResult


class SearchService:
    def __init__(self, adapter: SearchEngineAdapter) -> None:
        self._adapter = adapter

    async def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:
        return await self._adapter.search(query)

    async def _search_one(self, item: SearchQuery) -> SearchBatchResult:
        search_results = await self._adapter.search(item)
        return SearchBatchResult(query=item.query, results=search_results)

    async def search_batch(
        self,
        queries: list[SearchQuery],
    ) -> list[SearchBatchResult]:
        tasks = [self._search_one(item) for item in queries]
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
