from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.adapters.base import ContentFetcher, EngineFetcher, SearchEngineAdapter
    from src.core.config import AppSettings


class DependencyContainer:
    """Lazy DI container. __init__ is cheap; build() does all heavy work."""

    def __init__(self, settings: "AppSettings") -> None:
        self.settings = settings
        self._logger: Any = None
        self._http_client: Any = None
        self._adapters: dict[str, type["SearchEngineAdapter"]] = {}
        self._engine_fetchers: dict[str, "EngineFetcher"] = {}
        self._content_fetcher: "ContentFetcher | None" = None
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
        from src.adapters.searxng import SearXNGAdapter  # noqa: PLC0415

        self._adapters["searxng"] = SearXNGAdapter

    def _create_fetchers(self) -> None:
        """Instantiate EngineFetcher per enabled engine."""
        for cfg in self.settings.engines.values():
            if cfg.enabled and cfg.type in self._adapters:
                from src.adapters.searxng import SearXNGEngineFetcher  # noqa: PLC0415

                fetcher = SearXNGEngineFetcher(
                    http_client=self._http_client,
                    base_url=cfg.base_url or "",
                    api_key=cfg.api_key,
                )
                self._engine_fetchers[cfg.type] = fetcher

    def _create_content_fetcher(self) -> None:
        """Instantiate the global content fetcher for get_result."""
        from src.adapters.content_fetcher import ContentFetcherImpl  # noqa: PLC0415

        self._content_fetcher = ContentFetcherImpl(
            http_client=self._http_client,
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
