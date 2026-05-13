from typing import Any, Mapping, override

import httpx


class HttpClient(httpx.AsyncClient):
    def __init__(self, timeout: float = 10.0, max_content_length: int = 50000) -> None:
        super().__init__(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_connections=100),
        )
        self.max_content_length = max_content_length

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
            raise ValueError(
                f"Response exceeds max content length of {self.max_content_length}. Context length: {len(body)}",
            )
        return response
