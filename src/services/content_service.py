from typing import TYPE_CHECKING

from src.domain.models import ContentResult

if TYPE_CHECKING:
    from src.adapters.base import ContentFetcher


class ContentFetchService:
    def __init__(
        self,
        content_fetcher: "ContentFetcher",
        summarized_content_fetcher: "ContentFetcher | None" = None,
    ) -> None:
        self._content_fetcher = content_fetcher
        self._summarized_content_fetcher = summarized_content_fetcher

    async def fetch(self, url: str) -> ContentResult:
        return await self._content_fetcher.fetch(url)

    async def summarize_fetch(self, url: str) -> ContentResult:
        if self._summarized_content_fetcher is None:
            raise RuntimeError("SummarizedContentFetcher not configured")

        return await self._summarized_content_fetcher.fetch(url)
