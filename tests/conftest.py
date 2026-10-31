import pytest

from app.config import Settings


@pytest.fixture
def llm_path_settings() -> Settings:
    """Force the LLM path (no rule router) while keeping answer templates on."""
    return Settings(
        llm_api_key="test-key",
        agent_rule_router=False,
        agent_template_answers=True,
    )


@pytest.fixture
def router_settings() -> Settings:
    return Settings(
        llm_api_key="test-key",
        agent_rule_router=True,
        agent_template_answers=True,
    )
