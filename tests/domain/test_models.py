import pytest

from pydantic import ValidationError

from src.domain.models import SearchQuery, SearchResult, ContentResult


class TestSearchQuery:
    def test_default_values(self):
        query = SearchQuery(query="test", engine="SEARXNG")
        assert query.query == "test"
        assert query.engine == "SEARXNG"
        assert query.num_results == 10
        assert query.language == "en"
        assert query.categories == "general"

    def test_custom_values(self):
        query = SearchQuery(
            query="python tutorial",
            engine="BRAVE",
            num_results=5,
            language="ru",
            categories="news",
        )
        assert query.query == "python tutorial"
        assert query.engine == "BRAVE"
        assert query.num_results == 5
        assert query.language == "ru"
        assert query.categories == "news"

    def test_query_cannot_be_empty(self):
        with pytest.raises(ValidationError):
            SearchQuery(query="", engine="")


class TestSearchResult:
    def test_creation(self):
        result = SearchResult(title="Test Title", url="http://example.com", snippet="A snippet")
        assert result.title == "Test Title"
        assert result.url == "http://example.com"
        assert result.snippet == "A snippet"

    def test_serialization(self):
        result = SearchResult(title="T", url="http://x.com", snippet="S")
        data = result.model_dump()
        assert data == {"title": "T", "url": "http://x.com", "snippet": "S"}


class TestContentResult:
    def test_creation(self):
        content = ContentResult(url="http://example.com", title="Page Title", text="Some text")
        assert content.url == "http://example.com"
        assert content.title == "Page Title"
        assert content.text == "Some text"

    def test_serialization(self):
        content = ContentResult(url="http://x.com", title="T", text="text")
        data = content.model_dump()
        assert data == {"url": "http://x.com", "title": "T", "text": "text"}
