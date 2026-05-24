import logging
from typing import Any, Mapping, override

import httpx

from src.core.exceptions import MaxContentLengthError


class HttpClient(httpx.AsyncClient):
    def __init__(self, timeout: float = 10.0, max_content_length: int = 50000) -> None:
        super().__init__(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_connections=100),
        )
        self.max_content_length = max_content_length

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger("mcp-search")

    @override
    async def get(
        self,
        url: str | httpx.URL,
        *,
        params: Any = None,
        headers: Any = None,
        cookies: Any = None,
        auth: Any = None,
        follow_redirects: Any = True,
        timeout: Any = None,
        extensions: Mapping[str, Any] | None = None,
    ) -> httpx.Response:
        self._logger.debug(f"HttpClient.GET start {url=}")

        response = await super().get(
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )
        body = response.read()
        if len(body) > self.max_content_length:
            raise MaxContentLengthError(content_length=len(body), max_content_length=self.max_content_length)

        self._logger.debug(f"HttpClient.GET complete {url=}")
        return response
