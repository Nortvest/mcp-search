import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from src.domain.models import ContentResult, SearchQuery, SearchResponse, SearchResult

if TYPE_CHECKING:
    import httpx


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
    def __init__(self, http_client: "httpx.AsyncClient", base_url: str, api_key: str | None = None) -> None:
        self.http_client = http_client
        self.base_url = base_url
        self.api_key = api_key

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger("mcp-search")

    @abstractmethod
    async def fetch(self, params: dict[str, Any]) -> SearchResponse:
        raise NotImplementedError


class Summarizer(ABC):
    @abstractmethod
    def summarize(self, text: str) -> str:
        raise NotImplementedError
