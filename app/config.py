from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-based application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Portfolio Analytics Agent"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    # CORS origins for the Angular UI (comma-separated in .env)
    cors_origins: str = "http://localhost:4200"

    # LLM provider (used in later milestones; kept here for config shape)
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str = "gpt-4o-mini"

    # Demo analytics database (used in later milestones)
    database_url: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
