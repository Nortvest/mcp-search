from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.models import ContentResult, SearchResult
from src.server import mcp_server as mcp_module


class TestMcpServerToolRegistration:
    def test_mcp_instance_exists(self) -> None:
        assert hasattr(mcp_module, "mcp")
        assert mcp_module.mcp is not None

    @pytest.mark.asyncio
    async def test_search_tool_returns_output_schema(
        self,
    ) -> None:
        components = mcp_module.mcp._local_provider._components
        tool = components.get("tool:search@")
        assert tool is not None
        assert tool.name == "search"

    @pytest.mark.asyncio
    async def test_fetch_website_tool_returns_output_schema(
        self,
    ) -> None:
        components = mcp_module.mcp._local_provider._components
        tool = components.get("tool:fetch_website@")
        assert tool is not None
        assert tool.name == "fetch_website"


@pytest.fixture
def search_service_mock() -> MagicMock:
    service = MagicMock()
    service.search = AsyncMock(return_value=[SearchResult(title="Test", url="http://test.com", snippet="Snippet")])
    return service


@pytest.fixture
def content_fetcher_mock() -> MagicMock:
    fetcher = MagicMock()
    fetcher.fetch = AsyncMock(
        return_value=ContentResult(url="http://example.com", title="Title", text="Text"),
    )
    return fetcher
