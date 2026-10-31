from typing import Any

import pytest

from app.agent.provider import ProviderResponse
from app.config import Settings


class FakeLlm:
    """Scripted LLM double shared by agent/eval tests."""

    def __init__(
        self, responses: list[ProviderResponse], model_name: str = "fake-model"
    ) -> None:
        self._responses = list(responses)
        self.model_name = model_name
        self.calls = 0

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ProviderResponse:
        self.calls += 1
        if not self._responses:
            raise AssertionError("FakeLlm has no more scripted responses")
        return self._responses.pop(0)


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
