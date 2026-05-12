import logging
from abc import ABC, abstractmethod
from typing import Any

from src.domain.models import ContentResult, SearchQuery, SearchResponse, SearchResult


class SearchEngineAdapter(ABC):
    def __init__(self, fetcher: "EngineFetcher", config: Any) -> None:
        self.fetcher = fetcher
        self.config = config

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger("mcp-search")

    @abstractmethod
    async def search(self, query: SearchQuery) -> list[SearchResult]:
        raise NotImplementedError


class ContentFetcher(ABC):
    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger("mcp-search")

    @abstractmethod
    async def fetch(self, url: str) -> ContentResult:
        raise NotImplementedError


class EngineFetcher(ABC):
    def __init__(self, http_client: Any, base_url: str, api_key: str | None = None) -> None:
        self.http_client = http_client
        self.base_url = base_url
        self.api_key = api_key

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger("mcp-search")

    @abstractmethod
    async def fetch(self, params: dict[str, Any]) -> SearchResponse:
        raise NotImplementedError
