from src.server.schemas import GetResultOutput


class TestGetResultOutput:
    def test_get_result_output_creation(self) -> None:
        output = GetResultOutput(
            url="http://example.com",
            title="Example Page",
            text="Some extracted text content here.",
        )
        assert output.url == "http://example.com"
        assert output.title == "Example Page"
        assert output.text == "Some extracted text content here."

    def test_get_result_output_serialization(self) -> None:
        output = GetResultOutput(url="http://test.com", title="Test", text="Text")
        data = output.model_dump()
        assert data["url"] == "http://test.com"
        assert data["title"] == "Test"
        assert data["text"] == "Text"
