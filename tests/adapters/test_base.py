from __future__ import annotations

from typing import Any

import pytest

from src.adapters.base import ContentFetcher, EngineFetcher, SearchEngineAdapter
from src.domain.models import ContentResult, SearchQuery, SearchResponse, SearchResult


class TestSearchEngineAdapter:
    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            _adapter = SearchEngineAdapter(fetcher=None, config=None)  # type: ignore[arg-type, abstract]

    def test_concrete_subclass_works(self) -> None:
        class TestAdapter(SearchEngineAdapter):
            async def search(self, query: SearchQuery) -> list[SearchResult]:  # noqa: ARG002
                return [SearchResult(title="T", url="http://t.com", snippet="S")]

        adapter = TestAdapter(fetcher=None, config=None)  # type: ignore[arg-type]
        assert isinstance(adapter, SearchEngineAdapter)


class TestContentFetcher:
    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            _fetcher = ContentFetcher()  # type: ignore[abstract]

    def test_concrete_subclass_works(self) -> None:
        class TestFetcher(ContentFetcher):
            async def fetch(self, url: str) -> ContentResult:
                return ContentResult(url=url, title="T", text="text")

        fetcher = TestFetcher()
        assert isinstance(fetcher, ContentFetcher)


class TestEngineFetcher:
    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            _ef = EngineFetcher(http_client=None, base_url="http://test.com")  # type: ignore[abstract]

    def test_concrete_subclass_works(self) -> None:
        class MockHttpClient:
            pass

        class TestFetcher(EngineFetcher):
            async def fetch(self, _params: dict[str, Any]) -> SearchResponse:
                return SearchResponse(results=[])

        client = MockHttpClient()
        fetcher = TestFetcher(http_client=client, base_url="http://test.com", api_key="key")
        assert isinstance(fetcher, EngineFetcher)
        assert fetcher.http_client is client
        assert fetcher.base_url == "http://test.com"
        assert fetcher.api_key == "key"
