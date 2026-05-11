import pytest

from pydantic import ValidationError

from src.domain.models import SearchResponse, SearchResult


class TestSearchResponse:
    def test_creation_empty(self):
        response = SearchResponse(results=[])
        assert response.results == []

    def test_creation_with_results(self):
        results = [
            SearchResult(title="Result 1", url="http://example.com/1", snippet="Snippet 1"),
            SearchResult(title="Result 2", url="http://example.com/2", snippet="Snippet 2"),
        ]
        response = SearchResponse(results=results)
        assert len(response.results) == 2

    def test_serialization(self):
        results = [SearchResult(title="T", url="http://x.com", snippet="S")]
        response = SearchResponse(results=results)
        data = response.model_dump()
        assert "results" in data
        assert len(data["results"]) == 1

    def test_deserialization(self):
        data = {
            "results": [
                {"title": "T", "url": "http://x.com", "snippet": "S"}
            ]
        }
        response = SearchResponse(**data)
        assert len(response.results) == 1
        assert response.results[0].title == "T"
