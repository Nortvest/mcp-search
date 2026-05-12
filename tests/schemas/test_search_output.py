from src.domain.models import SearchResult
from src.server.schemas import SearchOutput


class TestSearchOutput:
    def test_search_output_with_results(self) -> None:
        results = [
            SearchResult(title="Result 1", url="http://example.com/1", snippet="Snippet 1"),
            SearchResult(title="Result 2", url="http://example.com/2", snippet="Snippet 2"),
        ]
        output = SearchOutput(results=results)
        assert len(output.results) == 2
        assert output.results[0].title == "Result 1"

    def test_search_output_empty_results(self) -> None:
        output = SearchOutput(results=[])
        assert output.results == []

    def test_search_output_serialization(self) -> None:
        results = [SearchResult(title="Test", url="http://test.com", snippet="Snippet")]
        output = SearchOutput(results=results)
        data = output.model_dump()
        assert "results" in data
        assert len(data["results"]) == 1
