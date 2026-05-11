import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class EngineConfig(BaseSettings):
    enabled: bool = False
    type: str = ""  # "searxng", etc.
    base_url: str | None = None
    api_key: str | None = None

    model_config = SettingsConfigDict(env_prefix="ENGINE_", extra="ignore")


class AppSettings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8080
    mcp_name: str = "mcp-search"
    default_engine: str = "SEARXNG"
    max_content_length: int = 50000
    request_timeout: float = 10.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def engines(self) -> dict[str, EngineConfig]:
        """Parse ENGINE_<NAME>_* env vars into engine configs."""
        engines: dict[str, EngineConfig] = {}
        prefix = "ENGINE_"
        raw: dict[str, dict[str, str]] = {}

        for key, value in os.environ.items():
            if key.startswith(prefix):
                remainder = key[len(prefix):]
                parts = remainder.split("_", 1)
                if len(parts) < 2:
                    continue
                name, field = parts[0], parts[1].lower()
                if name not in raw:
                    raw[name] = {}
                raw[name][field] = value

        for name, fields in raw.items():
            enabled_str = fields.get("enabled", "false")
            type_val = fields.get("type", "")
            base_url = fields.get("base_url")
            api_key = fields.get("api_key")

            cfg = EngineConfig(
                enabled=enabled_str.lower() == "true" if enabled_str else False,
                type=type_val,
                base_url=base_url,
                api_key=api_key,
            )
            engines[f"{name}"] = cfg

        return engines
