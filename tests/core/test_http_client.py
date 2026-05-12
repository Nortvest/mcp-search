from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.core.http_client import HttpClient


class TestHttpClient:
    @pytest.fixture
    def mock_response(self) -> MagicMock:
        response = MagicMock(spec=httpx.Response)
        response.read.return_value = b'{"results": []}'
        return response

    @pytest.mark.asyncio
    async def test_inherits_from_async_client(self) -> None:
        assert issubclass(HttpClient, httpx.AsyncClient)

    @pytest.mark.asyncio
    async def test_default_timeout(self) -> None:
        with patch.object(HttpClient, "__aenter__", new_callable=AsyncMock):
            client = HttpClient()
            assert client.timeout.connect == pytest.approx(10.0)

    @pytest.mark.asyncio
    async def test_custom_timeout(self) -> None:
        with patch.object(HttpClient, "__aenter__", new_callable=AsyncMock):
            client = HttpClient(timeout=30.0)
            assert client.timeout.connect == pytest.approx(30.0)

    @pytest.mark.asyncio
    async def test_max_content_length_default(self) -> None:
        with patch.object(HttpClient, "__aenter__", new_callable=AsyncMock):
            client = HttpClient()
            assert client.max_content_length == 50000

    @pytest.mark.asyncio
    async def test_custom_max_content_length(self) -> None:
        with patch.object(HttpClient, "__aenter__", new_callable=AsyncMock):
            client = HttpClient(max_content_length=100000)
            assert client.max_content_length == 100000

    @pytest.mark.asyncio
    async def test_get_returns_response(self, mock_response: MagicMock) -> None:
        with (
            patch.object(HttpClient, "__aenter__", new_callable=AsyncMock, return_value=AsyncMock()),
            patch.object(httpx.AsyncClient, "get", return_value=mock_response),
        ):
            client = HttpClient()
            response = await client.get("http://example.com")
            assert response == mock_response

    @pytest.mark.asyncio
    async def test_get_enforces_max_content_length(self) -> None:
        with (
            patch.object(HttpClient, "__aenter__", new_callable=AsyncMock, return_value=AsyncMock()),
            patch.object(httpx.AsyncClient, "get"),
        ):
            big_body = b"x" * 60000
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.read.return_value = big_body

            with patch.object(httpx.AsyncClient, "get", return_value=mock_resp):
                client = HttpClient(max_content_length=50000)
                with pytest.raises(ValueError, match="exceeds max content length"):
                    await client.get("http://example.com")

    @pytest.mark.asyncio
    async def test_get_passes_params_and_headers(self) -> None:
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.read.return_value = b"{}"

        with (
            patch.object(HttpClient, "__aenter__", new_callable=AsyncMock, return_value=AsyncMock()),
            patch.object(httpx.AsyncClient, "get") as mock_get,
        ):
            mock_get.return_value = mock_resp
            client = HttpClient()
            await client.get("http://example.com", params={"q": "test"}, headers={"X-Custom": "val"})
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args.kwargs
            assert call_kwargs["url"] == "http://example.com"
            assert call_kwargs["params"] == {"q": "test"}
            assert call_kwargs["headers"] == {"X-Custom": "val"}
