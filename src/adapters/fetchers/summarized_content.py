from src.adapters.base import ContentFetcher
from src.adapters.fetchers.readability import ReadabilityContentFetcher
from src.adapters.summarizer import SumySummarizer
from src.domain.models import ContentResult


class SummarizedContentFetcher(ContentFetcher):
    def __init__(
        self,
        readability_fetcher: ReadabilityContentFetcher,
        summarizer: SumySummarizer,
    ) -> None:
        super().__init__()
        self._readability_fetcher = readability_fetcher
        self._summarizer = summarizer

    async def fetch(self, url: str) -> ContentResult:
        self._logger.debug("SummarizedContentFetcher.fetch url=%s", url)
        full_result = await self._readability_fetcher.fetch(url)
        summarized_text = self._summarizer.summarize(full_result.text)

        return ContentResult(
            url=full_result.url,
            title=full_result.title,
            text=summarized_text,
        )
