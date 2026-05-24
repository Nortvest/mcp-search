import json
from typing import Any

import httpx
from fake_useragent import UserAgent

from src.adapters.base import EngineFetcher, SearchEngineAdapter
from src.core.config import EngineConfig
from src.core.http_client import HttpClient
from src.domain.models import SearchQuery, SearchResponse, SearchResult


class SearXNGEngineFetcher(EngineFetcher):
    def __init__(self, http_client: HttpClient, base_url: str, api_key: str | None = None) -> None:
        super().__init__(http_client, base_url, api_key)
        self._user_agent = UserAgent()

    async def fetch(self, params: dict[str, Any]) -> SearchResponse:
        headers = {"User-Agent": self._user_agent.random}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._logger.debug("SearXNGEngineFetcher.fetch url=%s params=%s", f"{self.base_url}/json", params)

        try:
            response = await self.http_client.get(
                url=f"{self.base_url}/search", params=params, headers=headers,
            )
        except httpx.HTTPError as e:
            self._logger.warning(f"SearXNGEngineFetcher.fetch http exception={e}")
            return SearchResponse(results=[])

        try:
            data = json.loads(response.read())
        except json.decoder.JSONDecodeError as e:
            self._logger.warning(
                f"SearXNGEngineFetcher.fetch http exception={e} | {response.status_code} | {response.read()!r}",
            )
            return SearchResponse(results=[])

        results = []
        for item in data.get("results", []):
            results.append(SearchResult(
                title=item["title"],
                url=item["url"],
                snippet=item.get("content", ""),
            ))

        self._logger.debug("SearXNGEngineFetcher.fetch returning %d results", len(results))
        return SearchResponse(results=results)


class SearXNGAdapter(SearchEngineAdapter):
    def __init__(self, fetcher: EngineFetcher, config: EngineConfig) -> None:
        super().__init__(fetcher=fetcher, config=config)

    async def search(self, query: SearchQuery) -> list[SearchResult]:
        self._logger.debug("SearXNGAdapter.search query=%s", query.query)
        response = await self.fetcher.fetch({
            "q": query.query,
            "format": "json",
            "categories": query.categories,
            "language": query.language,
            "engines": "google,bing,duckduckgo",
        })
        return response.results[:query.num_results]
