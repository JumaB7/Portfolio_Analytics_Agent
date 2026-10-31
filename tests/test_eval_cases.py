import json

import pytest

from app.agent.orchestrator import AgentOrchestrator
from app.agent.provider import ProviderResponse, ToolCallRequest
from app.config import Settings, get_settings
from app.eval.cases import EVAL_CASES, EvalCase
from tests.conftest import FakeLlm


@pytest.fixture(autouse=True)
def _local_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _script_for_case(case: EvalCase) -> list[ProviderResponse]:
    if case["kind"] in {"greeting", "unsupported"}:
        return [
            ProviderResponse(
                content=case["final_answer"],
                tool_calls=[],
                raw_message={"role": "assistant", "content": case["final_answer"]},
            )
        ]

    if case["kind"] == "rejected_tool":
        tool_call = ToolCallRequest(
            id="call_eval",
            name="run_sql",
            arguments_json=json.dumps({"sql": "SELECT 1"}),
        )
        return [
            ProviderResponse(
                content=None,
                tool_calls=[tool_call],
                raw_message={
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_eval",
                            "type": "function",
                            "function": {
                                "name": "run_sql",
                                "arguments": tool_call.arguments_json,
                            },
                        }
                    ],
                },
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
    assert fake.calls == 1
    assert result.llm_calls == 1

    if case["kind"] == "rejected_tool":
        assert activity.status == "rejected"
        assert result.answer_source == "template"
        assert "allowlisted" in result.answer.lower()
        return

    assert activity.tool_name == case["expected_tool"]
    assert activity.status == "ok"
    assert activity.result is not None
    assert result.answer_source == "template"
    grounding = case["grounding"] or {}

    if "project_count" in grounding:
        assert activity.result.get("project_count") == grounding["project_count"]
    if "years_experience" in grounding:
        assert activity.result.get("years_experience") == grounding["years_experience"]
    if "has_data" in grounding:
        assert activity.result["has_data"] is grounding["has_data"]
    if "name" in grounding:
        project = activity.result.get("project") or {}
        assert project.get("name") == grounding["name"]
        assert grounding["name"] in result.answer
    if "status" in grounding:
        project = activity.result.get("project") or {}
        assert project.get("status") == grounding["status"]
    if "top_technology_min_count" in grounding:
        techs = activity.result.get("technologies") or []
        assert techs
        assert techs[0]["project_count"] >= grounding["top_technology_min_count"]
    if "category_count_min" in grounding:
        categories = activity.result.get("categories") or []
        assert len(categories) >= grounding["category_count_min"]


def test_eval_catalog_has_at_least_eight_cases() -> None:
    assert len(EVAL_CASES) >= 8
    kinds = {case["kind"] for case in EVAL_CASES}
    assert {"tool_grounded", "empty_data", "unsupported", "greeting", "rejected_tool"} <= kinds
