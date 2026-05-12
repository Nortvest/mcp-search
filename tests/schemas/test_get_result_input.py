import pytest
from pydantic import ValidationError

from src.server.schemas import GetResultInput


class TestGetResultInputValidation:
    def test_valid_url_http(self) -> None:
        data = {"url": "http://example.com/page"}
        result = GetResultInput.model_validate(data)
        assert result.url == "http://example.com/page"

    def test_valid_url_https(self) -> None:
        data = {"url": "https://example.com/path/to/page"}
        result = GetResultInput.model_validate(data)
        assert result.url == "https://example.com/path/to/page"

    def test_invalid_url_no_scheme_raises(self) -> None:
        with pytest.raises(ValidationError):
            GetResultInput.model_validate({"url": "example.com/page"})

    def test_invalid_url_no_netloc_raises(self) -> None:
        with pytest.raises(ValidationError):
            GetResultInput.model_validate({"url": "file:///path/to/file"})

    def test_empty_url_raises(self) -> None:
        with pytest.raises(ValidationError):
            GetResultInput.model_validate({"url": ""})
