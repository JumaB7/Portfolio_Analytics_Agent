import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.agent.orchestrator import AgentOrchestrator
from app.agent.provider import ProviderResponse, ToolCallRequest
from app.config import Settings, get_settings
from app.db.seed import initialize_demo_database
from app.main import app

client = TestClient(app)


class FakeLlm:
    def __init__(self, responses: list[ProviderResponse], model_name: str = "fake-model") -> None:
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


@pytest.fixture(scope="module", autouse=True)
def _seed_demo_db() -> None:
    initialize_demo_database()


@pytest.fixture
def llm_path_settings() -> Settings:
    return Settings(
        llm_api_key="test-key",
        agent_rule_router=False,
        agent_template_answers=True,
    )


def test_agent_one_question_one_tool_grounded_answer(llm_path_settings: Settings) -> None:
    tool_call_message = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "get_sales_summary",
                    "arguments": json.dumps(
                        {"start_date": "2026-09-01", "end_date": "2026-09-30"}
                    ),
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
                        name="get_sales_summary",
                        arguments_json=json.dumps(
                            {"start_date": "2026-09-01", "end_date": "2026-09-30"}
                        ),
                    )
                ],
                raw_message=tool_call_message,
            )
        ]
    )

    result = AgentOrchestrator(settings=llm_path_settings, llm=fake).run(
        "What were our total sales for September?"
    )

    assert fake.calls == 1
    assert result.llm_calls == 1
    assert result.answer_source == "template"
    assert result.tool_activity[0].tool_name == "get_sales_summary"
    assert result.tool_activity[0].status == "ok"
    assert result.tool_activity[0].result is not None
    assert result.tool_activity[0].result["total_revenue"] == "125000.00"
    assert result.is_demo_dataset is True
    assert "125" in result.answer.replace(",", "")


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
    get_settings.cache_clear()

    response = client.post(
        "/api/chat",
        json={"message": "Can you summarise something unusual about margin mix?"},
    )
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["code"] == "llm_not_configured"
    assert "LLM_API_KEY" in detail["message"]

    get_settings.cache_clear()


def test_chat_endpoint_router_works_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("AGENT_RULE_ROUTER", "true")
    get_settings.cache_clear()

    response = client.post(
        "/api/chat",
        json={"message": "What were our total sales last month?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer_source"] == "router"
    assert body["llm_calls"] == 0
    assert body["tool_activity"][0]["tool_name"] == "get_sales_summary"

    get_settings.cache_clear()


def test_agent_empty_data_path_does_not_invent_revenue(llm_path_settings: Settings) -> None:
    tool_call_message = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_empty",
                "type": "function",
                "function": {
                    "name": "get_sales_summary",
                    "arguments": json.dumps(
                        {"start_date": "2019-01-01", "end_date": "2019-01-31"}
                    ),
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
                        id="call_empty",
                        name="get_sales_summary",
                        arguments_json=json.dumps(
                            {"start_date": "2019-01-01", "end_date": "2019-01-31"}
                        ),
                    )
                ],
                raw_message=tool_call_message,
            )
        ]
    )

    result = AgentOrchestrator(settings=llm_path_settings, llm=fake).run(
        "Tell me revenue for an empty custom window please"
    )
    assert result.tool_activity[0].result is not None
    assert result.tool_activity[0].result["has_data"] is False
    assert result.answer_source == "template"
    assert fake.calls == 1
    assert "125000" not in result.answer.replace(",", "")
