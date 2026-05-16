
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.adapters.fetchers.readability import ReadabilityContentFetcher
from src.core.http_client import HttpClient
from src.domain.models import ContentResult


class TestReadabilityContentFetcher:
    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock(spec=HttpClient)

    @pytest.mark.asyncio
    async def test_fetch_returns_content_result(
        self, mock_http_client: MagicMock,
    ) -> None:
        html = (
            b"<html><head><title>Test Page</title></head>"
            b"<body><article><p>Hello world article content</p></article>"
            b"</body></html>"
        )
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ReadabilityContentFetcher(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")

        assert isinstance(result, ContentResult)
        assert result.url == "http://example.com"
        assert result.title == "Test Page"
        assert len(result.text) > 0

    @pytest.mark.asyncio
    async def test_fetch_extracts_title_from_title_tag(
        self, mock_http_client: MagicMock,
    ) -> None:
        html = b"<html><head><title>My Amazing Article</title></head><body><p>content</p></body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ReadabilityContentFetcher(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")

        assert result.title == "My Amazing Article"

    @pytest.mark.asyncio
    async def test_fetch_fallback_to_url_when_no_title(
        self, mock_http_client: MagicMock,
    ) -> None:
        html = b"<html><body>no title tag here</body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ReadabilityContentFetcher(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com/page")

        assert result.title == "http://example.com/page"

    @pytest.mark.asyncio
    async def test_fetch_extracts_main_article_text(
        self, mock_http_client: MagicMock,
    ) -> None:
        html = (
            b"<html><head><title>Test</title></head>"
            b"<body>"
            b"<nav>Navigation links</nav>"
            b"<aside>Sidebar ads</aside>"
            b"<footer>Footer content</footer>"
            b"<article><h1>Main Article</h1><p>This is the main article text that should be extracted.</p></article>"
            b"</body></html>"
        )
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ReadabilityContentFetcher(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")

        assert "Main Article" in result.text
        assert "main article text that should be extracted" in result.text
        assert len(result.text) > 0

    @pytest.mark.asyncio
    async def test_fetch_handles_empty_html(
        self, mock_http_client: MagicMock,
    ) -> None:
        html = b""
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ReadabilityContentFetcher(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")

        assert isinstance(result, ContentResult)
        assert result.title == "http://example.com"

    @pytest.mark.asyncio
    async def test_fetch_handles_invalid_html(
        self, mock_http_client: MagicMock,
    ) -> None:
        html = b"<html><head><title>Broken</title></head><body>unclosed paragraph <div>content"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ReadabilityContentFetcher(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")

        assert isinstance(result, ContentResult)
        assert result.title == "Broken"

    @pytest.mark.asyncio
    async def test_fetch_handles_empty_title_tag(
        self, mock_http_client: MagicMock,
    ) -> None:
        html = b"<html><head><title>   </title></head><body><p>content</p></body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ReadabilityContentFetcher(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")

        assert result.title == "http://example.com"
