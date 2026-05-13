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

    async def search_batch(
        self,
        queries: list[SearchQuery],
    ) -> list[SearchBatchResult]:
        results: list[SearchBatchResult] = []
        for item in queries:
            try:
                engine = item.engine or ""
                search_query = SearchQuery(
                    query=item.query,
                    engine=engine,
                    num_results=item.num_results,
                    language=item.language,
                    categories=item.categories,
                )
                search_results = await self._adapter.search(search_query)
                results.append(SearchBatchResult(query=item.query, results=search_results))
            except ValueError as e:
                results.append(SearchBatchResult(query=item.query, results=[], error=str(e)))
        return results
