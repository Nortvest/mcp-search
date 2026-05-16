from html2text import html2text
from readability import Document as ReadabilityDocument

from src.adapters.base import ContentFetcher
from src.core.http_client import HttpClient
from src.domain.models import ContentResult


class ReadabilityContentFetcher(ContentFetcher):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__()
        self.http_client = http_client

    async def fetch(self, url: str) -> ContentResult:
        self._logger.debug("ReadabilityContentFetcher.fetch url=%s", url)
        response = await self.http_client.get(url=url)
        html = response.read().decode("utf-8", errors="replace")

        if not html.strip():
            self._logger.warning("ReadabilityContentFetcher.fetch html is empty")
            return ContentResult(url=url, title=url, text="")

        doc = ReadabilityDocument(html, url=url)
        title = doc.title() or ""
        if not title.strip() or title == "[no-title]":
            title = url
            self._logger.warning(
                "ReadabilityContentFetcher.fetch no title found url=%s using fallback",
                url,
            )

        summary_html = doc.summary()
        text = html2text(summary_html)

        return ContentResult(url=url, title=title.strip(), text=text)
