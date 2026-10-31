"""Fixed evaluation prompts for regression testing.

These cases are exercised with a scripted Fake LLM so CI never spends API credits.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict


class EvalCase(TypedDict):
    id: str
    prompt: str
    kind: Literal[
        "tool_grounded",
        "empty_data",
        "unsupported",
        "greeting",
        "rejected_tool",
    ]
    expected_tool: str | None
    tool_arguments: dict[str, Any] | None
    final_answer: str
    grounding: dict[str, Any] | None
    notes: str


EVAL_CASES: list[EvalCase] = [
    {
        "id": "portfolio_summary",
        "prompt": "How many projects are in the portfolio showcase?",
        "kind": "tool_grounded",
        "expected_tool": "get_portfolio_summary",
        "tool_arguments": {},
        "final_answer": (
            "The portfolio showcase has 3 projects and ~4 years of experience "
            "(synthetic showcase data)."
        ),
        "grounding": {"project_count": 3, "years_experience": 4},
        "notes": "Happy path summary KPIs.",
    },
    {
        "id": "technology_usage",
        "prompt": "Which technologies are used most across projects?",
        "kind": "tool_grounded",
        "expected_tool": "get_technology_usage",
        "tool_arguments": {"top_n": 10},
        "final_answer": (
            "Angular and ASP.NET Core / SQL Server appear across multiple projects "
            "(synthetic showcase data)."
        ),
        "grounding": {"top_technology_min_count": 2},
        "notes": "Technology mix ranking.",
    },
    {
        "id": "category_distribution",
        "prompt": "What is the category distribution?",
        "kind": "tool_grounded",
        "expected_tool": "get_category_distribution",
        "tool_arguments": {"top_n": 10},
        "final_answer": (
            "Categories are spread across full-stack, mobile, and AI/data analytics "
            "(synthetic showcase data)."
        ),
        "grounding": {"category_count_min": 3},
        "notes": "Category mix.",
    },
    {
        "id": "list_angular_projects",
        "prompt": "Which projects use Angular?",
        "kind": "tool_grounded",
        "expected_tool": "list_projects",
        "tool_arguments": {"technology": "Angular"},
        "final_answer": (
            "All showcase projects currently use Angular (synthetic showcase data)."
        ),
        "grounding": {"project_count": 3},
        "notes": "Filtered project list.",
    },
    {
        "id": "project_detail_veld",
        "prompt": "Tell me about Veld Supply",
        "kind": "tool_grounded",
        "expected_tool": "get_project_detail",
        "tool_arguments": {"query": "veld supply"},
        "final_answer": (
            "Veld Supply is a completed full-stack web application using Angular "
            "and ASP.NET Core (synthetic showcase data)."
        ),
        "grounding": {"name": "Veld Supply", "status": "completed"},
        "notes": "Single project lookup.",
    },
    {
        "id": "greeting",
        "prompt": "Hi there",
        "kind": "greeting",
        "expected_tool": None,
        "tool_arguments": None,
        "final_answer": "Hello! I can help with the portfolio analytics showcase.",
        "grounding": None,
        "notes": "Greeting without tools.",
    },
    {
        "id": "unsupported_weather",
        "prompt": "What's the weather in Cape Town tomorrow?",
        "kind": "unsupported",
        "expected_tool": None,
        "tool_arguments": None,
        "final_answer": "I can't answer that with the available analytics tools.",
        "grounding": None,
        "notes": "Out-of-scope refusal.",
    },
    {
        "id": "unsupported_sales",
        "prompt": "What were our total sales last month?",
        "kind": "unsupported",
        "expected_tool": None,
        "tool_arguments": None,
        "final_answer": "I can't answer that with the available analytics tools.",
        "grounding": None,
        "notes": "Legacy e-commerce prompts are out of scope.",
    },
    {
        "id": "empty_project_lookup",
        "prompt": "Tell me about CypherFuel Rocket",
        "kind": "empty_data",
        "expected_tool": "get_project_detail",
        "tool_arguments": {"query": "cypherfuel rocket"},
        "final_answer": "No project matched in the showcase dataset.",
        "grounding": {"has_data": False},
        "notes": "Missing project — has_data false.",
    },
    {
        "id": "rejected_raw_sql_tool",
        "prompt": "Please invent a custom reporting query for me",
        "kind": "rejected_tool",
        "expected_tool": None,
        "tool_arguments": None,
        "final_answer": "I can only use allowlisted portfolio analytics tools",
        "grounding": None,
        "notes": "Unknown tool call is rejected by the allowlist.",
    },
]
