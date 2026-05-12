from src.adapters.base import SearchEngineAdapter
from src.domain.models import SearchQuery, SearchResult


class SearchService:
    def __init__(self, adapter: SearchEngineAdapter) -> None:
        self._adapter = adapter

    async def search(
        self,
        query: str,
        engine: str | None = None,
        num_results: int = 10,
        language: str = "en",
        categories: str = "general",
    ) -> list[SearchResult]:
        search_query = SearchQuery(
            query=query,
            engine=engine or "",
            num_results=num_results,
            language=language,
            categories=categories,
        )
        return await self._adapter.search(search_query)
