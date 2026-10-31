from datetime import date

from app.agent.answers import render_tool_answer
from app.agent.orchestrator import AgentOrchestrator
from app.agent.router import route_message
from app.config import Settings
from app.db.seed import initialize_demo_database


def setup_module() -> None:
    initialize_demo_database()


def test_route_total_sales_last_month() -> None:
    decision = route_message(
        "What were our total sales last month?",
        today=date(2026, 10, 31),
    )
    assert decision is not None
    assert decision.kind == "tool"
    assert decision.tool_name == "get_sales_summary"
    assert decision.arguments == {
        "start_date": "2026-09-01",
        "end_date": "2026-09-30",
    }


def test_route_greeting_and_unsupported() -> None:
    hi = route_message("Hi there!")
    assert hi is not None and hi.kind == "greeting"

    weather = route_message("What's the weather in Cape Town tomorrow?")
    assert weather is not None and weather.kind == "unsupported"


def test_router_answers_without_llm(router_settings: Settings) -> None:
    class BoomLlm:
        model_name = "should-not-be-called"

        def complete(self, messages, tools):  # noqa: ANN001
            raise AssertionError("LLM should not be called for routed prompts")

    result = AgentOrchestrator(settings=router_settings, llm=BoomLlm()).run(
        "What were our total sales last month?"
    )
    assert result.llm_calls == 0
    assert result.answer_source == "router"
    assert result.tool_activity[0].tool_name == "get_sales_summary"
    assert "125,000.00" in result.answer or "125000.00" in result.answer.replace(",", "")


def test_template_sales_summary_empty() -> None:
    answer = render_tool_answer(
        "get_sales_summary",
        {
            "start_date": "2019-01-01",
            "end_date": "2019-01-31",
            "has_data": False,
            "total_revenue": "0.00",
        },
    )
    assert answer is not None
    assert "no completed sales" in answer.lower()
    assert "125000" not in answer
