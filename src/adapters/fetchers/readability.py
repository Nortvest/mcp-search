import html
import re
from typing import Any

import httpx
from charset_normalizer import from_bytes
from lxml.etree import ParserError
from readability import Document
from readability.readability import Unparseable

from src.adapters.base import ContentFetcher
from src.core.http_client import HttpClient
from src.domain.models import ContentResult


class ReadabilityContentFetcher(ContentFetcher):
    _MIN_TEXT_LENGTH = 10

    def __init__(self, http_client: HttpClient) -> None:
        super().__init__()
        self.http_client = http_client

    async def fetch(self, url: str) -> ContentResult:
        self._logger.debug("ReadabilityContentFetcher.fetch url=%s", url)

        try:
            response = await self.http_client.get(url=url)
        except httpx.HTTPError as e:
            self._logger.warning("ReadabilityContentFetcher.fetch error=%s", e)
            return ContentResult(url=url, title="NO DATA", text="NO DATA")

        raw_html = response.read()
        decoded = from_bytes(raw_html).best()
        raw_html_str = str(decoded) if decoded else raw_html.decode("utf-8", errors="replace")

        doc = Document(input=raw_html_str)
        title, text = self._extract_content(doc, url)
        return ContentResult(url=url, title=title, text=text)

    def _extract_content(self, doc: Any, fallback_title: str) -> tuple[str, str]:
        try:
            title = doc.title() or fallback_title
            if not title.strip() or title == "[no-title]":
                title = fallback_title
            content_html = str(doc.content())
            text = re.sub(r"<[^>]+>", "", content_html)
            text = html.unescape(text)
            text = " ".join(text.split())
        except (Unparseable, ParserError):
            self._logger.warning("ReadabilityContentFetcher failed to extract content url=%s", fallback_title)
            return fallback_title, ""

        if len(text) < self._MIN_TEXT_LENGTH:
            text = ""

        return title, text
