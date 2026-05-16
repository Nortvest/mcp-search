from unittest.mock import AsyncMock, MagicMock

import pytest

from src.adapters.fetchers.readability import ReadabilityContentFetcher
from src.adapters.fetchers.summarized_content import SummarizedContentFetcher
from src.adapters.summarizer import SumySummarizer
from src.core.http_client import HttpClient
from src.domain.models import ContentResult


class TestSummarizedContentFetcher:
    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock(spec=HttpClient)

    @pytest.fixture
    def readability_fetcher(self, mock_http_client: MagicMock) -> ReadabilityContentFetcher:
        return ReadabilityContentFetcher(http_client=mock_http_client)

    @pytest.fixture
    def summarizer(self) -> SumySummarizer:
        return SumySummarizer(max_sentences=3)

    @pytest.fixture
    def summarized_fetcher(
        self, readability_fetcher: ReadabilityContentFetcher, summarizer: SumySummarizer,
    ) -> SummarizedContentFetcher:
        return SummarizedContentFetcher(
            readability_fetcher=readability_fetcher,
            summarizer=summarizer,
        )

    @pytest.mark.asyncio
    async def test_compose_pipeline_works_correctly(
        self, summarized_fetcher: SummarizedContentFetcher, mock_http_client: MagicMock,
    ) -> None:
        html = (
            b"<html><head><title>Test Page</title></head>"
            b"<body><article><p>This is the first sentence of the article. "
            b"This is the second sentence. This is the third sentence. "
            b"This is the fourth sentence that should not appear in summary. "
            b"This is the fifth sentence also excluded.</p></article></body></html>"
        )
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        result = await summarized_fetcher.fetch("http://example.com")

        assert isinstance(result, ContentResult)
        assert len(result.text) > 0

    @pytest.mark.asyncio
    async def test_summarized_text_is_shorter_than_original(
        self, summarized_fetcher: SummarizedContentFetcher, mock_http_client: MagicMock,
    ) -> None:
        long_article = " ".join([f"This is sentence number {i} with some additional content." for i in range(1, 51)])
        html = (
            b"<html><head><title>Long Article</title></head>"
            b"<body><article><p>" + long_article.encode() + b"</p></article></body></html>"
        )
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        result = await summarized_fetcher.fetch("http://example.com")

        assert len(result.text) < len(long_article), "Summary should be shorter than original text"

    @pytest.mark.asyncio
    async def test_url_and_title_preserved_from_readability_result(
        self, summarized_fetcher: SummarizedContentFetcher, mock_http_client: MagicMock,
    ) -> None:
        html = b"<html><head><title>Preserved Title</title></head><body><p>content</p></body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        result = await summarized_fetcher.fetch("http://example.com/page")

        assert result.url == "http://example.com/page"
        assert result.title == "Preserved Title"

    @pytest.mark.asyncio
    async def test_empty_text_returns_empty_summary(
        self, summarized_fetcher: SummarizedContentFetcher, mock_http_client: MagicMock,
    ) -> None:
        html = b"<html><head><title>Empty</title></head><body></body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        result = await summarized_fetcher.fetch("http://example.com")

        assert isinstance(result, ContentResult)
        assert not result.text

    @pytest.mark.asyncio
    async def test_short_text_returns_full_content(
        self, summarized_fetcher: SummarizedContentFetcher, mock_http_client: MagicMock,
    ) -> None:
        html = b"<html><head><title>Short</title></head><body><p>One sentence only.</p></body></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_http_client.get = AsyncMock(return_value=mock_resp)

        result = await summarized_fetcher.fetch("http://example.com")

        assert isinstance(result, ContentResult)
        assert len(result.text.strip()) > 0
