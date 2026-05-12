from src.adapters.base import ContentFetcher
from src.domain.models import ContentResult


class ContentFetchService:
    def __init__(self, content_fetcher: ContentFetcher) -> None:
        self._content_fetcher = content_fetcher

    async def fetch(self, url: str) -> ContentResult:
        return await self._content_fetcher.fetch(url)
