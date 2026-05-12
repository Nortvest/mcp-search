from unittest.mock import AsyncMock, MagicMock

import pytest

from src.adapters.searxng import SearXNGAdapter, SearXNGEngineFetcher
from src.core.http_client import HttpClient
from src.domain.models import SearchQuery, SearchResult


class TestSearXNGEngineFetcher:
    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock(spec=HttpClient)

    @pytest.mark.asyncio
    async def test_fetch_returns_search_response(self, mock_http_client: MagicMock) -> None:
        json_body = b'{"results": [{"title": "Test", "url": "http://test.com", "content": "Snippet"}]}'
        mock_resp = MagicMock()
        mock_resp.read.return_value = json_body
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = SearXNGEngineFetcher(
            http_client=mock_http_client,
            base_url="http://searxng.local",
        )
        response = await fetcher.fetch({"q": "test", "format": "json"})
        assert len(response.results) == 1
        assert response.results[0].title == "Test"
        assert response.results[0].url == "http://test.com"
        assert response.results[0].snippet == "Snippet"

    @pytest.mark.asyncio
    async def test_fetch_empty_results(self, mock_http_client: MagicMock) -> None:
        json_body = b'{"results": []}'
        mock_resp = MagicMock()
        mock_resp.read.return_value = json_body
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = SearXNGEngineFetcher(
            http_client=mock_http_client,
            base_url="http://searxng.local",
        )
        response = await fetcher.fetch({"q": "test", "format": "json"})
        assert len(response.results) == 0

    @pytest.mark.asyncio
    async def test_fetch_uses_user_agent(self, mock_http_client: MagicMock) -> None:
        json_body = b'{"results": []}'
        mock_resp = MagicMock()
        mock_resp.read.return_value = json_body
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = SearXNGEngineFetcher(
            http_client=mock_http_client,
            base_url="http://searxng.local",
        )
        await fetcher.fetch({"q": "test", "format": "json"})
        call_kwargs = mock_http_client.get.call_args
        assert "User-Agent" in call_kwargs.kwargs["headers"]

    @pytest.mark.asyncio
    async def test_fetch_includes_api_key_header(self, mock_http_client: MagicMock) -> None:
        json_body = b'{"results": []}'
        mock_resp = MagicMock()
        mock_resp.read.return_value = json_body
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = SearXNGEngineFetcher(
            http_client=mock_http_client,
            base_url="http://searxng.local",
            api_key="secret123",
        )
        await fetcher.fetch({"q": "test", "format": "json"})
        call_kwargs = mock_http_client.get.call_args
        assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer secret123"

    @pytest.mark.asyncio
    async def test_fetch_excludes_auth_header_without_api_key(self, mock_http_client: MagicMock) -> None:
        json_body = b'{"results": []}'
        mock_resp = MagicMock()
        mock_resp.read.return_value = json_body
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = SearXNGEngineFetcher(
            http_client=mock_http_client,
            base_url="http://searxng.local",
        )
        await fetcher.fetch({"q": "test", "format": "json"})
        call_kwargs = mock_http_client.get.call_args
        assert "Authorization" not in call_kwargs.kwargs["headers"]

    @pytest.mark.asyncio
    async def test_fetch_uses_correct_endpoint(self, mock_http_client: MagicMock) -> None:
        json_body = b'{"results": []}'
        mock_resp = MagicMock()
        mock_resp.read.return_value = json_body
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = SearXNGEngineFetcher(
            http_client=mock_http_client,
            base_url="http://searxng.local",
        )
        await fetcher.fetch({"q": "test"})
        call_kwargs = mock_http_client.get.call_args
        assert call_kwargs.kwargs["url"] == "http://searxng.local/search"

    def test_fetcher_stores_base_url(self, mock_http_client: MagicMock) -> None:
        fetcher = SearXNGEngineFetcher(
            http_client=mock_http_client,
            base_url="http://searxng.local",
        )
        assert fetcher.base_url == "http://searxng.local"

    def test_fetcher_stores_api_key(self, mock_http_client: MagicMock) -> None:
        fetcher = SearXNGEngineFetcher(
            http_client=mock_http_client,
            base_url="http://searxng.local",
            api_key="key123",
        )
        assert fetcher.api_key == "key123"


class TestSearXNGAdapter:
    @pytest.fixture
    def mock_fetcher(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_config(self) -> MagicMock:
        return MagicMock()

    @pytest.mark.asyncio
    async def test_search_delegates_to_fetcher(
        self, mock_fetcher: AsyncMock, mock_config: MagicMock,
    ) -> None:
        results: list[SearchResult] = [SearchResult(title="T", url="http://t.com", snippet="S")]
        mock_fetcher.fetch = AsyncMock(return_value=type("SearchResponse", (), {"results": results})())

        adapter = SearXNGAdapter(fetcher=mock_fetcher, config=mock_config)
        query = SearchQuery(query="test query", engine="SEARXNG")
        result = await adapter.search(query)
        assert len(result) == 1
        assert result[0].title == "T"

    @pytest.mark.asyncio
    async def test_search_passes_query_params(
        self, mock_fetcher: AsyncMock, mock_config: MagicMock,
    ) -> None:
        results: list[SearchResult] = []
        mock_fetcher.fetch = AsyncMock(return_value=type("SearchResponse", (), {"results": results})())

        adapter = SearXNGAdapter(fetcher=mock_fetcher, config=mock_config)
        query = SearchQuery(query="test", engine="SEARXNG", language="ru", categories="news")
        await adapter.search(query)
        call_kwargs = mock_fetcher.fetch.call_args[0][0]
        assert call_kwargs["q"] == "test"
        assert call_kwargs["format"] == "json"
        assert call_kwargs["language"] == "ru"
        assert call_kwargs["categories"] == "news"

    @pytest.mark.asyncio
    async def test_search_includes_engines_param(
        self, mock_fetcher: AsyncMock, mock_config: MagicMock,
    ) -> None:
        results: list[SearchResult] = []
        mock_fetcher.fetch = AsyncMock(return_value=type("SearchResponse", (), {"results": results})())

        adapter = SearXNGAdapter(fetcher=mock_fetcher, config=mock_config)
        query = SearchQuery(query="test", engine="SEARXNG")
        await adapter.search(query)
        call_kwargs = mock_fetcher.fetch.call_args[0][0]
        assert call_kwargs["engines"] == "google,bing,duckduckgo"
