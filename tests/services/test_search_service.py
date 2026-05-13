import asyncio
from unittest.mock import AsyncMock, patch

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

        result = await search_service.search(SearchQuery(query="test query", engine=""))
        assert len(result) == 1
        assert result[0].title == "T"

    @pytest.mark.asyncio
    async def test_search_passes_query_to_adapter(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])

        await search_service.search(SearchQuery(query="python tutorial", engine="", language="ru", categories="news"))
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
        await search_service.search(SearchQuery(query="test", engine=""))
        call_args = mock_adapter.search.call_args[0][0]
        assert call_args.language == "auto"

    @pytest.mark.asyncio
    async def test_search_default_categories(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])
        await search_service.search(SearchQuery(query="test", engine=""))
        call_args = mock_adapter.search.call_args[0][0]
        assert call_args.categories == "general"

    @pytest.mark.asyncio
    async def test_search_passes_num_results(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])
        await search_service.search(SearchQuery(query="test", engine="", num_results=5))
        call_args = mock_adapter.search.call_args[0][0]
        assert call_args.num_results == 5

    @pytest.mark.asyncio
    async def test_search_passes_engine(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])
        await search_service.search(SearchQuery(query="test", engine="BRAVE"))
        call_args = mock_adapter.search.call_args[0][0]
        assert call_args.engine == "BRAVE"

    @pytest.mark.asyncio
    async def test_search_batch_single_query(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        results = [SearchResult(title="T", url="http://t.com", snippet="S")]
        mock_adapter.search = AsyncMock(return_value=results)

        queries = [SearchQuery(query="test", engine="searxng")]
        batch_result = await search_service.search_batch(queries)

        assert len(batch_result) == 1
        assert batch_result[0].query == "test"
        assert len(batch_result[0].results) == 1
        assert batch_result[0].results[0].title == "T"
        assert batch_result[0].error is None

    @pytest.mark.asyncio
    async def test_search_batch_multiple_queries(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        results_a = [SearchResult(title="A", url="http://a.com", snippet="S")]
        results_b = [SearchResult(title="B", url="http://b.com", snippet="S")]
        mock_adapter.search.side_effect = [results_a, results_b]

        queries = [
            SearchQuery(query="query1", engine="searxng"),
            SearchQuery(query="query2", engine="brave"),
        ]
        batch_result = await search_service.search_batch(queries)

        assert len(batch_result) == 2
        assert batch_result[0].query == "query1"
        assert len(batch_result[0].results) == 1
        assert batch_result[0].results[0].title == "A"
        assert batch_result[1].query == "query2"
        assert len(batch_result[1].results) == 1
        assert batch_result[1].results[0].title == "B"

    @pytest.mark.asyncio
    async def test_search_batch_empty_queries(
        self, search_service: SearchService,
    ) -> None:
        batch_result = await search_service.search_batch([])
        assert len(batch_result) == 0

    @pytest.mark.asyncio
    async def test_search_batch_preserves_query_fields(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])

        queries = [SearchQuery(query="test", engine="searxng", num_results=5, language="ru", categories="news")]
        await search_service.search_batch(queries)

        call_args = mock_adapter.search.call_args[0][0]
        assert call_args.query == "test"
        assert call_args.engine == "searxng"
        assert call_args.num_results == 5
        assert call_args.language == "ru"
        assert call_args.categories == "news"

    @pytest.mark.asyncio
    async def test_search_batch_empty_engine_defaults_to_empty(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        mock_adapter.search = AsyncMock(return_value=[])

        queries = [SearchQuery(query="test", engine="")]
        await search_service.search_batch(queries)

        call_args = mock_adapter.search.call_args[0][0]
        assert not call_args.engine

    @pytest.mark.asyncio
    async def test_search_batch_error_handling(self, search_service: SearchService) -> None:
        async def failing_search(*args: object, **kwargs: object) -> list[SearchResult]:  # noqa: ARG001
            raise ValueError("engine not supported")

        queries = [
            SearchQuery(query="good", engine="searxng"),
            SearchQuery(query="bad", engine="unknown"),
        ]

        with patch.object(search_service._adapter, "search", failing_search):
            batch_result = await search_service.search_batch(queries)

        assert len(batch_result) == 2
        for result in batch_result:
            assert result.error == "engine not supported"
            assert result.results == []

    @pytest.mark.asyncio
    async def test_search_batch_all_errors(self, search_service: SearchService) -> None:
        async def failing_search(*args: object, **kwargs: object) -> list[SearchResult]:  # noqa: ARG001
            raise ValueError("all failed")

        queries = [
            SearchQuery(query="q1", engine="searxng"),
            SearchQuery(query="q2", engine="brave"),
        ]

        with patch.object(search_service._adapter, "search", failing_search):
            batch_result = await search_service.search_batch(queries)

        assert len(batch_result) == 2
        for result in batch_result:
            assert result.error is not None
            assert result.results == []

    @pytest.mark.asyncio
    async def test_search_batch_parallel_execution(
        self, search_service: SearchService, mock_adapter: AsyncMock,
    ) -> None:
        call_order: list[int] = []
        lock = asyncio.Lock()

        async def tracking_search(*args: object, **kwargs: object) -> list[SearchResult]:  # noqa: ARG001
            async with lock:
                call_order.append(1)
            await asyncio.sleep(0.05)
            return [SearchResult(title="T", url="http://t.com", snippet="S")]

        mock_adapter.search = tracking_search

        queries = [
            SearchQuery(query=f"q{i}", engine="searxng") for i in range(5)
        ]
        await search_service.search_batch(queries)

        assert len(call_order) == 5

    @pytest.mark.asyncio
    async def test_search_batch_mixed_success_and_error(self, search_service: SearchService) -> None:
        call_count = 0

        async def mixed_search(*args: object, **kwargs: object) -> list[SearchResult]:  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise ValueError("middle failure")
            return [SearchResult(title="T", url="http://t.com", snippet="S")]

        queries = [
            SearchQuery(query="q1", engine="searxng"),
            SearchQuery(query="q2", engine="brave"),
            SearchQuery(query="q3", engine="duckduckgo"),
        ]

        with patch.object(search_service._adapter, "search", mixed_search):
            batch_result = await search_service.search_batch(queries)

        assert len(batch_result) == 3
        assert batch_result[0].error is None
        assert batch_result[1].error == "middle failure"
        assert batch_result[2].error is None
