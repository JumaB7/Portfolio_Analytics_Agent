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
    # Include both localhost and 127.0.0.1 — browsers treat them as different origins.
    cors_origins: str = "http://localhost:4200,http://127.0.0.1:4200"

    # LLM provider (server-side only). OpenAI-compatible Chat Completions API.
    llm_api_key: str | None = None
    llm_base_url: str | None = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 45.0
    agent_max_tool_iterations: int = 4
    # Skip second LLM call: render grounded text from tool JSON in Python.
    agent_template_answers: bool = True
    # Answer common demo prompts with rules (0 LLM calls) when pattern is clear.
    agent_rule_router: bool = True

    # Shared showcase dataset from PortfolioAPI (same payload as the dashboard).
    # Example: http://127.0.0.1:5157 — agent calls GET {base}/api/dashboard/analytics
    portfolio_api_base_url: str | None = "http://127.0.0.1:5157"
    portfolio_api_timeout_seconds: float = 5.0

    # Legacy LocalDB e-commerce seed (unused by portfolio tools; kept for older scripts).
    database_url: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
