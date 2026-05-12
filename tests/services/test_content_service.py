from unittest.mock import AsyncMock

import pytest

from src.domain.models import ContentResult
from src.services.content_service import ContentFetchService


class TestContentFetchService:
    @pytest.fixture
    def mock_fetcher(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def content_service(self, mock_fetcher: AsyncMock) -> ContentFetchService:
        return ContentFetchService(content_fetcher=mock_fetcher)

    @pytest.mark.asyncio
    async def test_fetch_delegates_to_content_fetcher(
        self, content_service: ContentFetchService, mock_fetcher: AsyncMock,
    ) -> None:
        result = ContentResult(url="http://example.com", title="Page Title", text="Some text")
        mock_fetcher.fetch = AsyncMock(return_value=result)

        response = await content_service.fetch("http://example.com")
        assert isinstance(response, ContentResult)
        assert response.url == "http://example.com"
        assert response.title == "Page Title"
        assert response.text == "Some text"

    @pytest.mark.asyncio
    async def test_fetch_passes_url(
        self, content_service: ContentFetchService, mock_fetcher: AsyncMock,
    ) -> None:
        result = ContentResult(url="http://example.com", title="T", text="text")
        mock_fetcher.fetch = AsyncMock(return_value=result)

        await content_service.fetch("http://example.com/page")
        mock_fetcher.fetch.assert_called_once_with("http://example.com/page")
