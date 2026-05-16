import os
from functools import cached_property

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EngineConfig(BaseSettings):
    enabled: bool = False
    type: str = ""  # "searxng", etc.
    base_url: str | None = None
    api_key: str | None = None

    model_config = SettingsConfigDict(env_prefix="ENGINE_", extra="ignore")


class SummarySettings(BaseSettings):
    enable: bool = True
    max_sentences: int = 128
    max_content_length_readability: int = 512000

    model_config = SettingsConfigDict(env_prefix="SUMMARY_", env_file=".env", extra="ignore")


class AppSettings(BaseSettings):
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8080
    mcp_name: str = "mcp-search"
    default_engine: str = "SEARXNG"
    max_content_length: int = 50000
    request_timeout: float = 10.0
    log_level: str = "INFO"

    summary: SummarySettings = SummarySettings()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v: str) -> str:
        return v.upper()

    @cached_property
    def engines(self) -> dict[str, EngineConfig]:  # noqa: PLR0915
        """Parse ENGINE_<NAME>_* env vars into engine configs."""
        min_parts_of_env = 2
        engines: dict[str, EngineConfig] = {}
        prefix = "ENGINE_"
        raw: dict[str, dict[str, str]] = {}

        for key, value in os.environ.items():
            if key.startswith(prefix):
                remainder = key[len(prefix):]
                parts = remainder.split("_", 1)
                if len(parts) < min_parts_of_env:
                    continue
                name, field = parts[0], parts[1].lower()
                if name not in raw:
                    raw[name] = {}
                raw[name][field] = value

        for name, fields in raw.items():
            cfg = self._create_engine_config(fields)
            engines[name] = cfg

        return engines

    @staticmethod
    def _create_engine_config(fields: dict[str, str]) -> EngineConfig:
        """Create an EngineConfig from parsed field values."""
        enabled_str = fields.get("enabled", "false")
        type_val = fields.get("type", "")
        base_url = fields.get("base_url")
        api_key = fields.get("api_key")

        return EngineConfig(
            enabled=enabled_str.lower() == "true" if enabled_str else False,
            type=type_val,
            base_url=base_url,
            api_key=api_key,
        )
