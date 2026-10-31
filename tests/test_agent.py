import json

import pytest
from fastapi.testclient import TestClient

from app.agent.orchestrator import AgentOrchestrator
from app.agent.provider import ProviderResponse, ToolCallRequest
from app.config import Settings, get_settings
from app.main import app
from tests.conftest import FakeLlm

client = TestClient(app)


@pytest.fixture(autouse=True)
def _local_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_agent_one_question_one_tool_grounded_answer(llm_path_settings: Settings) -> None:
    tool_call_message = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "get_portfolio_summary",
                    "arguments": "{}",
                },
            }
        ],
    }
    fake = FakeLlm(
        [
            ProviderResponse(
                content=None,
                tool_calls=[
                    ToolCallRequest(
                        id="call_1",
                        name="get_portfolio_summary",
                        arguments_json="{}",
                    )
                ],
                raw_message=tool_call_message,
            )
        ]
    )

    result = AgentOrchestrator(settings=llm_path_settings, llm=fake).run(
        "Give me the portfolio showcase summary"
    )

    assert fake.calls == 1
    assert result.llm_calls == 1
    assert result.answer_source == "template"
    assert result.tool_activity[0].tool_name == "get_portfolio_summary"
    assert result.tool_activity[0].status == "ok"
    assert result.tool_activity[0].result is not None
    assert result.tool_activity[0].result["project_count"] == 3
    assert result.is_demo_dataset is True
    assert "3 projects" in result.answer


def test_agent_rejects_unknown_tool(llm_path_settings: Settings) -> None:
    tool_call_message = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_x",
                "type": "function",
                "function": {
                    "name": "run_sql",
                    "arguments": json.dumps({"sql": "SELECT 1"}),
                },
            }
        ],
    }
    fake = FakeLlm(
        [
            ProviderResponse(
                content=None,
                tool_calls=[
                    ToolCallRequest(
                        id="call_x",
                        name="run_sql",
                        arguments_json=json.dumps({"sql": "SELECT 1"}),
                    )
                ],
                raw_message=tool_call_message,
            )
        ]
    )

    result = AgentOrchestrator(settings=llm_path_settings, llm=fake).run(
        "Please invent a custom reporting query for me"
    )
    assert result.tool_activity[0].status == "rejected"
    assert result.answer_source == "template"
    assert fake.calls == 1
    assert "allowlisted" in result.answer.lower()


def test_chat_endpoint_requires_api_key_for_unrouted_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("AGENT_RULE_ROUTER", "false")
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()

    response = client.post(
        "/api/chat",
        json={"message": "Explain the technology matrix in detail please"},
    )
    assert response.status_code == 503
    get_settings.cache_clear()
