from charset_normalizer import from_bytes
from fake_useragent import UserAgent
from html2text import html2text

from src.adapters.base import ContentFetcher
from src.core.http_client import HttpClient
from src.domain.models import ContentResult


class ContentFetcherImpl(ContentFetcher):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__()
        self.http_client = http_client
        self._user_agent = UserAgent()

    async def fetch(self, url: str) -> ContentResult:
        self._logger.debug("ContentFetcherImpl.fetch url=%s", url)
        headers = {"User-Agent": self._user_agent.random}
        response = await self.http_client.get(url=url, headers=headers)
        raw_html = response.read()
        decoded = from_bytes(raw_html).best()
        html = str(decoded) if decoded else raw_html.decode("utf-8", errors="replace")
        text = html2text(html)
        try:
            start = html.lower().index("<title>") + 7
            end = html.lower().index("</title>", start)
            title = html[start:end].strip()
        except (ValueError, IndexError):
            self._logger.warning("ContentFetcherImpl.fetch no <title> tag found url=%s", url)
            title = url
        return ContentResult(url=url, title=title, text=text)
