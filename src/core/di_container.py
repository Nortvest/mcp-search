from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from src.adapters.base import ContentFetcher, EngineFetcher, SearchEngineAdapter
    from src.adapters.fetchers.readability import ReadabilityContentFetcher
    from src.adapters.fetchers.summarized_content import SummarizedContentFetcher
    from src.core.config import AppSettings
    from src.services.search_service import SearchService
    from src.services.content_service import ContentFetchService
    from src.services.deep_search_service import DeepSearchService


class DependencyContainer:
    """Lazy DI container. __init__ is cheap; build() does all heavy work."""

    def __init__(self, settings: "AppSettings") -> None:
        self.settings = settings
        self._logger: Any = None
        self._http_client: Any = None
        self._adapters: dict[str, type["SearchEngineAdapter"]] = {}
        self._engine_fetchers: dict[str, "EngineFetcher"] = {}
        self._content_fetcher: "ContentFetcher | None" = None
        self._readability_fetcher: "ReadabilityContentFetcher | None" = None
        self._summarized_content_fetcher: "SummarizedContentFetcher | None" = None
        self._cached_adapters: dict[str, "SearchEngineAdapter"] = {}

    def build(self) -> "DependencyContainer":
        """Perform all heavy initialization. Called once at startup."""
        from src.core.http_client import HttpClient  # noqa: PLC0415
        from src.core.logger import setup_logger  # noqa: PLC0415

        setup_logger(self.settings.log_level)
        self._http_client = HttpClient(
            timeout=self.settings.request_timeout,
            max_content_length=self.settings.max_content_length,
        )
        self._register_adapters()
        self._create_fetchers()
        self._create_content_fetcher()
        self._create_readability_fetcher()
        self._create_summarized_content_fetcher()
        return self

    @classmethod
    def create(cls, settings: "AppSettings | None" = None) -> "DependencyContainer":
        """Lazy factory - loads settings but doesn't build yet."""
        if settings is None:
            from src.core.config import AppSettings  # noqa: PLC0415

            settings = AppSettings()
        return cls(settings)

    # --- adapter registry ---

    def _register_adapters(self) -> None:
        """Map engine type strings to adapter classes (no instantiation)."""
        from src.adapters.engine.searxng import SearXNGAdapter  # noqa: PLC0415

        self._adapters["searxng"] = SearXNGAdapter

    def _create_fetchers(self) -> None:
        """Instantiate EngineFetcher per enabled engine."""
        for cfg in self.settings.engines.values():
            if cfg.enabled and cfg.type in self._adapters:
                from src.adapters.engine.searxng import SearXNGEngineFetcher  # noqa: PLC0415

                fetcher = SearXNGEngineFetcher(
                    http_client=self._http_client,
                    base_url=cfg.base_url or "",
                    api_key=cfg.api_key,
                )
                self._engine_fetchers[cfg.type] = fetcher

    def _create_content_fetcher(self) -> None:
        """Instantiate the global content fetcher for get_result."""
        from src.adapters.fetchers.content import ContentFetcherImpl  # noqa: PLC0415

        self._content_fetcher = ContentFetcherImpl(
            http_client=self._http_client,
        )

    def _create_readability_fetcher(self) -> None:
        """Instantiate the readability-based content fetcher."""
        from src.adapters.fetchers.readability import ReadabilityContentFetcher  # noqa: PLC0415
        from src.core.http_client import HttpClient  # noqa: PLC0415

        high_limit_client = HttpClient(
            timeout=self.settings.request_timeout,
            max_content_length=self.settings.summary.max_content_length_readability,
        )
        self._readability_fetcher = ReadabilityContentFetcher(
            http_client=high_limit_client,
        )

    def _create_summarized_content_fetcher(self) -> None:
        """Instantiate the summarized content fetcher."""
        from src.adapters.summarizer import SumySummarizer  # noqa: PLC0415

        if self._readability_fetcher is None:
            raise RuntimeError("ReadabilityContentFetcher not initialized")

        summarizer = SumySummarizer(max_sentences=self.settings.summary.max_sentences)
        from src.adapters.fetchers.summarized_content import SummarizedContentFetcher  # noqa: PLC0415

        self._summarized_content_fetcher = SummarizedContentFetcher(
            readability_fetcher=self._readability_fetcher,
            summarizer=summarizer,
        )

    def get_adapter(self, engine_name: str) -> "SearchEngineAdapter":
        """Return the cached adapter instance for an engine. Same instance on every call."""
        if engine_name in self._cached_adapters:
            return self._cached_adapters[engine_name]

        cfg = self.settings.engines.get(engine_name)
        if not cfg or cfg.type not in self._adapters:
            raise ValueError(f"Unknown engine: {engine_name}")

        fetcher = self._engine_fetchers[cfg.type]
        adapter = self._adapters[cfg.type](fetcher=fetcher, config=cfg)
        self._cached_adapters[engine_name] = adapter
        return adapter

    def get_content_fetcher(self) -> "ContentFetcher":
        if self._content_fetcher is None:
            raise RuntimeError("DependencyContainer not built - call build() first")
        return self._content_fetcher

    def get_readability_fetcher(self) -> "ReadabilityContentFetcher":
        if self._readability_fetcher is None:
            raise RuntimeError("DependencyContainer not built - call build() first")
        return self._readability_fetcher

    def get_summarized_content_fetcher(self) -> "SummarizedContentFetcher":
        if self._summarized_content_fetcher is None:
            raise RuntimeError("DependencyContainer not built - call build() first")
        return self._summarized_content_fetcher

    # --- services registry ---

    def get_search_service(self) -> "SearchService":
        from src.services.search_service import SearchService  # noqa: PLC0415

        search_adapter = self.get_adapter(self.settings.default_engine)
        return SearchService(adapter=search_adapter)

    def get_content_fetch_service(self) -> "ContentFetchService":
        from src.services.content_service import ContentFetchService  # noqa: PLC0415

        content_fetcher = self.get_content_fetcher()
        return ContentFetchService(content_fetcher=content_fetcher)

    def get_content_fetch_service_with_summarize(self) -> "ContentFetchService":
        from src.services.content_service import ContentFetchService  # noqa: PLC0415

        content_fetcher = self.get_content_fetcher()
        summarized_content_fetcher = self.get_summarized_content_fetcher()
        return ContentFetchService(
            content_fetcher=content_fetcher,
            summarized_content_fetcher=summarized_content_fetcher,
        )

    def get_deep_search_service(self) -> "DeepSearchService":
        from src.services.deep_search_service import DeepSearchService  # noqa: PLC0415

        search_service = self.get_search_service()
        content_service = self.get_content_fetch_service_with_summarize()
        return DeepSearchService(search_service=search_service, content_service=content_service)
