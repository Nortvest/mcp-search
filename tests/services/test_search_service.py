from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.domain.models import SearchQuery, SearchResult
from src.services.search_service import SearchService


class TestSearchService:
    @pytest.fixture
    def mock_adapter(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def search_service(self, mock_adapter: AsyncMock) -> SearchService:
        return SearchService(adapter=mock_adapter)

    @pytest.mark.asyncio
    async def test_search_delegates_to_adapter(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        results = [SearchResult(title="T", url="http://t.com", snippet="S")]
        mock_adapter.search = AsyncMock(return_value=results)

        result = await search_service.search(query="test query")
        assert len(result) == 1
        assert result[0].title == "T"

    @pytest.mark.asyncio
    async def test_search_passes_query_to_adapter(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])

        await search_service.search(query="python tutorial", language="ru", categories="news")
        call_args = mock_adapter.search.call_args[0][0]
        assert isinstance(call_args, SearchQuery)
        assert call_args.query == "python tutorial"
        assert call_args.language == "ru"
        assert call_args.categories == "news"

    @pytest.mark.asyncio
    async def test_search_default_language(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])
        await search_service.search(query="test")
        call_args = mock_adapter.search.call_args[0][0]
        assert call_args.language == "en"

    @pytest.mark.asyncio
    async def test_search_default_categories(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])
        await search_service.search(query="test")
        call_args = mock_adapter.search.call_args[0][0]
        assert call_args.categories == "general"

    @pytest.mark.asyncio
    async def test_search_passes_num_results(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])
        await search_service.search(query="test", num_results=5)
        call_args = mock_adapter.search.call_args[0][0]
        assert call_args.num_results == 5

    @pytest.mark.asyncio
    async def test_search_passes_engine(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])
        await search_service.search(query="test", engine="BRAVE")
        call_args = mock_adapter.search.call_args[0][0]
        assert call_args.engine == "BRAVE"
