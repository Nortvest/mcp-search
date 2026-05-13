import pytest
from pydantic import ValidationError

from src.server.schemas import SearchInput


class TestSearchInputValidation:
    def test_valid_search_input_defaults(self) -> None:
        data = {"query": "test query"}
        result = SearchInput.model_validate(data)
        assert result.query == "test query"
        assert result.language == "auto"
        assert result.categories == "general"
        assert result.engine is None
        assert result.num_results == 10

    def test_valid_search_input_all_fields(self) -> None:
        data = {
            "query": "python tutorial",
            "language": "ru",
            "categories": "images,videos",
            "engine": "GOOGLE",
            "num_results": 5,
        }
        result = SearchInput.model_validate(data)
        assert result.query == "python tutorial"
        assert result.language == "ru"
        assert result.categories == "images,videos"
        assert result.engine == "GOOGLE"
        assert result.num_results == 5

    def test_num_results_min_boundary(self) -> None:
        data = {"query": "test", "num_results": 1}
        result = SearchInput.model_validate(data)
        assert result.num_results == 1

    def test_num_results_max_boundary(self) -> None:
        data = {"query": "test", "num_results": 50}
        result = SearchInput.model_validate(data)
        assert result.num_results == 50

    def test_num_results_too_low_raises(self) -> None:
        with pytest.raises(ValidationError):
            SearchInput.model_validate({"query": "test", "num_results": 0})

    def test_num_results_too_high_raises(self) -> None:
        with pytest.raises(ValidationError):
            SearchInput.model_validate({"query": "test", "num_results": 51})

    def test_language_uppercase_converted_to_lower(self) -> None:
        data = {"query": "test", "language": "EN"}
        result = SearchInput.model_validate(data)
        assert result.language == "en"

    def test_language_invalid_length_raises(self) -> None:
        with pytest.raises(ValidationError):
            SearchInput.model_validate({"query": "test", "language": "eng"})

    def test_language_non_alpha_raises(self) -> None:
        with pytest.raises(ValidationError):
            SearchInput.model_validate({"query": "test", "language": "e1"})
