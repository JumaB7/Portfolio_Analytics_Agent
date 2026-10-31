from app.agent.answers import render_tool_answer
from app.agent.orchestrator import AgentOrchestrator
from app.agent.router import route_message
from app.config import Settings, get_settings


def test_route_portfolio_summary(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    decision = route_message("How many projects are in the portfolio showcase?")
    assert decision is not None
    assert decision.kind == "tool"
    assert decision.tool_name == "get_portfolio_summary"
    assert decision.arguments == {}


def test_route_greeting_and_unsupported() -> None:
    hi = route_message("Hi there!")
    assert hi is not None and hi.kind == "greeting"

    weather = route_message("What's the weather in Cape Town tomorrow?")
    assert weather is not None and weather.kind == "unsupported"

    sales = route_message("What were our total sales last month?")
    assert sales is not None and sales.kind == "unsupported"

    # "whether" must not match unsupported "weather" substring.
    whether = route_message(
        "Can you tell me whether Angular is used across projects?"
    )
    assert whether is None or whether.kind == "tool"


def test_route_technology_usage() -> None:
    decision = route_message("Which technologies are used most?")
    assert decision is not None
    assert decision.kind == "tool"
    assert decision.tool_name == "get_technology_usage"


def test_route_what_is_this_dashboard_about() -> None:
    decision = route_message("What is this dashboard about?")
    assert decision is not None
    assert decision.kind == "tool"
    assert decision.tool_name == "get_portfolio_summary"
    assert decision.arguments == {}


def test_route_who_is_jumari() -> None:
    decision = route_message("Who is Jumari?")
    assert decision is not None
    assert decision.kind == "tool"
    assert decision.tool_name == "get_owner_profile"
    assert decision.arguments == {}


def test_route_skills_and_experience() -> None:
    skills = route_message("What are the skills?")
    assert skills is not None
    assert skills.tool_name == "get_skills"

    experience = route_message("Where has Jumari worked?")
    assert experience is not None
    assert experience.tool_name == "get_experience"

    contact = route_message("What is the contact email?")
    assert contact is not None
    assert contact.tool_name == "get_contact"


def test_route_what_is_still_resolves_named_project() -> None:
    decision = route_message("What is Veld Supply?")
    assert decision is not None
    assert decision.kind == "tool"
    assert decision.tool_name == "get_project_detail"
    assert decision.arguments == {"query": "veld supply"}


def test_router_answers_without_llm(monkeypatch, router_settings: Settings) -> None:  # noqa: ANN001
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()

    class BoomLlm:
        model_name = "should-not-be-called"

        def complete(self, messages, tools):  # noqa: ANN001
            raise AssertionError("LLM should not be called for routed prompts")

    result = AgentOrchestrator(settings=router_settings, llm=BoomLlm()).run(
        "How many projects are there?"
    )
    assert result.llm_calls == 0
    assert result.answer_source == "router"
    assert result.tool_activity[0].tool_name == "get_portfolio_summary"
    assert "3 projects" in result.answer


def test_owner_profile_template_reads_naturally() -> None:
    answer = render_tool_answer(
        "get_owner_profile",
        {
            "has_data": True,
            "name": "Jumari Blignaut",
            "role": "Full-Stack Software Engineer",
            "location": "Potchefstroom, South Africa",
            "summary": (
                "Full-Stack Software Engineer with nearly four years of professional "
                "experience developing and maintaining web applications across financial "
                "technology, higher education and fleet telematics. Experienced in frontend "
                "and backend development."
            ),
            "project_count": 3,
            "years_experience": 4,
            "highlights": [
                {"label": "Based in", "value": "Potchefstroom, South Africa"},
            ],
            "dataset_label": "showcase",
        },
    )
    assert answer is not None
    assert answer.startswith(
        "Jumari Blignaut is a Full-Stack Software Engineer based in Potchefstroom, South Africa."
    )
    assert "Full-Stack Software Engineer with nearly" not in answer
    assert "Highlights —" not in answer
    assert "3 of their projects" in answer


def test_template_portfolio_summary_empty() -> None:
    answer = render_tool_answer(
        "get_portfolio_summary",
        {
            "has_data": False,
            "project_count": 0,
            "years_experience": 0,
            "technology_count": 0,
            "category_count": 0,
            "status_counts": {},
            "dataset_label": "empty",
        },
    )
    assert answer is not None
    assert "no portfolio projects" in answer.lower()
