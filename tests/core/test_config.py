import os

from src.core.config import AppSettings, EngineConfig


class TestEngineConfig:
    def test_defaults(self):
        cfg = EngineConfig()
        assert cfg.enabled is False
        assert cfg.type == ""
        assert cfg.base_url is None
        assert cfg.api_key is None

    def test_with_values(self):
        cfg = EngineConfig(enabled=True, type="searxng", base_url="http://localhost:8080", api_key="secret")
        assert cfg.enabled is True
        assert cfg.type == "searxng"
        assert cfg.base_url == "http://localhost:8080"
        assert cfg.api_key == "secret"


class TestAppSettings:
    def test_defaults(self):
        settings = AppSettings()
        assert settings.host == "0.0.0.0"
        assert settings.port == 8080
        assert settings.mcp_name == "mcp-search"
        assert settings.default_engine == "SEARXNG"
        assert settings.max_content_length == 50000
        assert settings.request_timeout == 10.0
        assert settings.log_level == "INFO"

    def test_custom_values(self):
        settings = AppSettings(host="127.0.0.1", port=9999, mcp_name="test-search")
        assert settings.host == "127.0.0.1"
        assert settings.port == 9999
        assert settings.mcp_name == "test-search"

    def test_engines_parse_enabled(self, monkeypatch):
        monkeypatch.setenv("ENGINE_SEARXNG_ENABLED", "true")
        monkeypatch.setenv("ENGINE_SEARXNG_TYPE", "searxng")
        monkeypatch.setenv("ENGINE_SEARXNG_BASE_URL", "http://localhost:8081")
        settings = AppSettings()
        engines = settings.engines
        assert "SEARXNG" in engines
        assert engines["SEARXNG"].enabled is True
        assert engines["SEARXNG"].type == "searxng"
        assert engines["SEARXNG"].base_url == "http://localhost:8081"

    def test_engines_parse_disabled(self, monkeypatch):
        monkeypatch.setenv("ENGINE_BRAVE_ENABLED", "false")
        monkeypatch.setenv("ENGINE_BRAVE_TYPE", "brave")
        settings = AppSettings()
        engines = settings.engines
        assert "BRAVE" in engines
        assert engines["BRAVE"].enabled is False

    def test_engines_parse_api_key(self, monkeypatch):
        monkeypatch.setenv("ENGINE_SEARXNG_ENABLED", "true")
        monkeypatch.setenv("ENGINE_SEARXNG_TYPE", "searxng")
        monkeypatch.setenv("ENGINE_SEARXNG_API_KEY", "my-secret-key")
        settings = AppSettings()
        engines = settings.engines
        assert engines["SEARXNG"].api_key == "my-secret-key"

    def test_engines_multiple(self, monkeypatch):
        monkeypatch.setenv("ENGINE_SEARXNG_ENABLED", "true")
        monkeypatch.setenv("ENGINE_SEARXNG_TYPE", "searxng")
        monkeypatch.setenv("ENGINE_BRAVE_ENABLED", "true")
        monkeypatch.setenv("ENGINE_BRAVE_TYPE", "brave")
        settings = AppSettings()
        engines = settings.engines
        assert "SEARXNG" in engines
        assert "BRAVE" in engines

    def test_engines_empty_when_no_env(self):
        # Ensure no ENGINE_* vars are set for this test
        keys_to_remove = [k for k in os.environ if k.startswith("ENGINE_")]
        removed = {}
        for k in keys_to_remove:
            removed[k] = os.environ.pop(k)

        try:
            settings = AppSettings()
            engines = settings.engines
            assert len(engines) == 0
        finally:
            for k, v in removed.items():
                os.environ[k] = v
