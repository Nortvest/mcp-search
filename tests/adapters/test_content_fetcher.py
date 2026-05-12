from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.adapters.content_fetcher import ContentFetcherImpl
from src.core.http_client import HttpClient
from src.domain.models import ContentResult


class TestContentFetcherImpl:
    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock(spec=HttpClient)

    @pytest.mark.asyncio
    async def test_fetch_returns_content_result(self, mock_http_client: MagicMock) -> None:
        html = b"<html><head><title>Test Page</title></head><body><p>Hello world</p></body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ContentFetcherImpl(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")

        assert isinstance(result, ContentResult)
        assert result.url == "http://example.com"
        assert result.title == "Test Page"
        assert "Hello world" in result.text

    @pytest.mark.asyncio
    async def test_fetch_uses_user_agent(self, mock_http_client: MagicMock) -> None:
        html = b"<html><body>test</body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ContentFetcherImpl(http_client=mock_http_client)
        await fetcher.fetch("http://example.com")
        call_kwargs = mock_http_client.get.call_args
        assert "User-Agent" in call_kwargs.kwargs["headers"]

    @pytest.mark.asyncio
    async def test_fetch_passes_url(self, mock_http_client: MagicMock) -> None:
        html = b"<html><body>test</body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ContentFetcherImpl(http_client=mock_http_client)
        await fetcher.fetch("http://example.com/page")
        assert mock_http_client.get.call_args.kwargs["url"] == "http://example.com/page"

    @pytest.mark.asyncio
    async def test_fetch_title_extraction(self, mock_http_client: MagicMock) -> None:
        html = b"<html><head><title>My Amazing Page</title></head><body>content</body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ContentFetcherImpl(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")
        assert result.title == "My Amazing Page"

    @pytest.mark.asyncio
    async def test_fetch_fallback_title_when_no_title_tag(self, mock_http_client: MagicMock) -> None:
        html = b"<html><body>no title tag here</body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ContentFetcherImpl(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")
        assert result.title == "http://example.com"

    @pytest.mark.asyncio
    async def test_fetch_handles_uppercase_title_tag(self, mock_http_client: MagicMock) -> None:
        html = b"<HTML><HEAD><TITLE>Uppercase</TITLE></HEAD><BODY>body</BODY></HTML>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        fetcher = ContentFetcherImpl(http_client=mock_http_client)
        result = await fetcher.fetch("http://example.com")
        assert result.title == "Uppercase"
