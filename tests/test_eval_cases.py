import json
from typing import Any

import pytest

from app.agent.orchestrator import AgentOrchestrator
from app.agent.provider import ProviderResponse, ToolCallRequest
from app.config import Settings
from app.db.seed import initialize_demo_database
from app.eval.cases import EVAL_CASES, EvalCase


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


def _script_for_case(case: EvalCase) -> list[ProviderResponse]:
    if case["kind"] in {"greeting", "unsupported"}:
        return [
            ProviderResponse(
                content=case["final_answer"],
                tool_calls=[],
                raw_message={"role": "assistant", "content": case["final_answer"]},
            )
        ]

    assert case["expected_tool"] is not None
    assert case["tool_arguments"] is not None
    args_json = json.dumps(case["tool_arguments"])
    tool_call = ToolCallRequest(
        id="call_eval",
        name=case["expected_tool"],
        arguments_json=args_json,
    )
    raw_message = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_eval",
                "type": "function",
                "function": {
                    "name": case["expected_tool"],
                    "arguments": args_json,
                },
            }
        ],
    }
    # With templates enabled, a successful/rejected tool ends the turn (no 2nd LLM call).
    return [
        ProviderResponse(
            content=None,
            tool_calls=[tool_call],
            raw_message=raw_message,
        )
    ]


@pytest.mark.parametrize("case", EVAL_CASES, ids=lambda c: c["id"])
def test_eval_case(case: EvalCase, llm_path_settings: Settings) -> None:
    fake = FakeLlm(_script_for_case(case))
    result = AgentOrchestrator(settings=llm_path_settings, llm=fake).run(case["prompt"])

    if case["kind"] in {"greeting", "unsupported"}:
        assert result.tool_activity == []
        assert result.answer_source == "llm"
        assert result.llm_calls == 1
        assert result.answer == case["final_answer"]
        return

    assert len(result.tool_activity) == 1
    activity = result.tool_activity[0]
    assert activity.tool_name == case["expected_tool"]
    assert fake.calls == 1
    assert result.llm_calls == 1

    if case["kind"] == "rejected_tool":
        assert activity.status == "rejected"
        assert result.answer_source == "template"
        assert "allowlisted" in result.answer.lower()
        return

    assert activity.status == "ok"
    assert activity.result is not None
    assert result.answer_source == "template"
    grounding = case["grounding"] or {}

    if "total_revenue" in grounding:
        assert activity.result["total_revenue"] == grounding["total_revenue"]
        assert grounding["total_revenue"].split(".")[0] in result.answer.replace(",", "")
    if "order_count" in grounding:
        assert activity.result["order_count"] == grounding["order_count"]
    if "units_sold" in grounding:
        assert activity.result["units_sold"] == grounding["units_sold"]
    if "has_data" in grounding:
        assert activity.result["has_data"] is grounding["has_data"]
        if grounding["has_data"] is False:
            assert "125000" not in result.answer.replace(",", "")
    if "top_category" in grounding:
        categories = activity.result.get("categories") or []
        assert categories
        assert categories[0]["category"] == grounding["top_category"]
        assert grounding["top_category"] in result.answer
    if "current_revenue" in grounding:
        current = activity.result.get("current_period") or {}
        assert current["total_revenue"] == grounding["current_revenue"]
    if "product_name" in grounding:
        products = activity.result.get("products") or []
        assert products
        assert products[0]["product_name"] == grounding["product_name"]
        assert grounding["product_name"] in result.answer


def test_eval_catalog_has_at_least_eight_cases() -> None:
    assert len(EVAL_CASES) >= 8
    kinds = {case["kind"] for case in EVAL_CASES}
    assert {"tool_grounded", "empty_data", "unsupported", "greeting", "rejected_tool"} <= kinds
