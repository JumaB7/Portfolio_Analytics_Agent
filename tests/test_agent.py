import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.agent.orchestrator import AgentOrchestrator
from app.agent.provider import ProviderResponse, ToolCallRequest
from app.config import get_settings
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


def test_agent_one_question_one_tool_grounded_answer() -> None:
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
            ),
            ProviderResponse(
                content=(
                    "Total sales for 2026-09-01 to 2026-09-30 were ZAR 125000.00 "
                    "across 30 orders (synthetic demo data)."
                ),
                tool_calls=[],
                raw_message={
                    "role": "assistant",
                    "content": (
                        "Total sales for 2026-09-01 to 2026-09-30 were ZAR 125000.00 "
                        "across 30 orders (synthetic demo data)."
                    ),
                },
            ),
        ]
    )

    result = AgentOrchestrator(llm=fake).run(
        "What were our total sales last month?"
    )

    assert fake.calls == 2
    assert result.iterations == 2
    assert result.tool_activity[0].tool_name == "get_sales_summary"
    assert result.tool_activity[0].status == "ok"
    assert result.is_demo_dataset is True
    assert "125000" in result.answer


def test_agent_rejects_unknown_tool() -> None:
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
            ),
            ProviderResponse(
                content="I can only use allowlisted analytics tools, not raw SQL.",
                tool_calls=[],
                raw_message={
                    "role": "assistant",
                    "content": "I can only use allowlisted analytics tools, not raw SQL.",
                },
            ),
        ]
    )

    result = AgentOrchestrator(llm=fake).run("Run SELECT * FROM orders")
    assert result.tool_activity[0].status == "rejected"
    assert "allowlisted" in result.answer.lower() or "sql" in result.answer.lower()


def test_chat_endpoint_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()

    response = client.post("/api/chat", json={"message": "What were total sales last month?"})
    assert response.status_code == 503
    assert "LLM_API_KEY" in response.json()["detail"]

    get_settings.cache_clear()
