"""Fixed evaluation prompts for regression testing.

These cases are exercised with a scripted Fake LLM so CI never spends API credits.
Expected tool args use September/August 2026 ranges matching the synthetic seed
when "today" is treated as October 2026 in demos.
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
        "id": "sales_summary_september",
        "prompt": "What were our total sales last month?",
        "kind": "tool_grounded",
        "expected_tool": "get_sales_summary",
        "tool_arguments": {"start_date": "2026-09-01", "end_date": "2026-09-30"},
        "final_answer": (
            "Total sales for 2026-09-01 to 2026-09-30 were ZAR 125000.00 "
            "across 30 orders (synthetic demo data)."
        ),
        "grounding": {"total_revenue": "125000.00", "order_count": 30, "units_sold": 250},
        "notes": "Happy path total sales.",
    },
    {
        "id": "revenue_by_category_september",
        "prompt": "Which product category generated the most revenue last month?",
        "kind": "tool_grounded",
        "expected_tool": "get_revenue_by_category",
        "tool_arguments": {
            "start_date": "2026-09-01",
            "end_date": "2026-09-30",
            "top_n": 5,
        },
        "final_answer": (
            "Electronics generated the most revenue last month at ZAR 125000.00 "
            "(synthetic demo data)."
        ),
        "grounding": {"top_category": "Electronics", "revenue": "125000.00"},
        "notes": "Category ranking.",
    },
    {
        "id": "compare_sep_vs_aug",
        "prompt": "How did sales change compared with the previous month?",
        "kind": "tool_grounded",
        "expected_tool": "compare_sales_periods",
        "tool_arguments": {
            "current_start_date": "2026-09-01",
            "current_end_date": "2026-09-30",
            "previous_start_date": "2026-08-01",
            "previous_end_date": "2026-08-31",
        },
        "final_answer": (
            "September 2026 revenue was ZAR 125000.00 versus August 2026 "
            "(synthetic demo data). See tool result for the exact change."
        ),
        "grounding": {"current_revenue": "125000.00"},
        "notes": "Month-over-month comparison.",
    },
    {
        "id": "lowest_products_september",
        "prompt": "Which products have the lowest sales last month?",
        "kind": "tool_grounded",
        "expected_tool": "get_product_performance",
        "tool_arguments": {
            "start_date": "2026-09-01",
            "end_date": "2026-09-30",
            "sort": "lowest",
            "top_n": 5,
        },
        "final_answer": (
            "The lowest-selling product last month was Portable Power Bank at "
            "ZAR 45000.00 (synthetic demo data)."
        ),
        "grounding": {
            "product_name": "Portable Power Bank",
            "revenue": "45000.00",
        },
        "notes": "Lowest product ranking.",
    },
    {
        "id": "highest_products_september",
        "prompt": "Which products had the highest revenue last month?",
        "kind": "tool_grounded",
        "expected_tool": "get_product_performance",
        "tool_arguments": {
            "start_date": "2026-09-01",
            "end_date": "2026-09-30",
            "sort": "highest",
            "top_n": 5,
        },
        "final_answer": (
            "Trail Headphones led last month with ZAR 80000.00 revenue "
            "(synthetic demo data)."
        ),
        "grounding": {
            "product_name": "Trail Headphones",
            "revenue": "80000.00",
        },
        "notes": "Highest product ranking.",
    },
    {
        "id": "empty_sales_period",
        "prompt": "What were total sales in January 2019?",
        "kind": "empty_data",
        "expected_tool": "get_sales_summary",
        "tool_arguments": {"start_date": "2019-01-01", "end_date": "2019-01-31"},
        "final_answer": (
            "The demo dataset has no completed sales between 2019-01-01 and "
            "2019-01-31, so I cannot report revenue figures for that period."
        ),
        "grounding": {"has_data": False, "total_revenue": "0.00"},
        "notes": "Empty range must not invent numbers.",
    },
    {
        "id": "empty_category_period",
        "prompt": "Which category sold best in January 2019?",
        "kind": "empty_data",
        "expected_tool": "get_revenue_by_category",
        "tool_arguments": {
            "start_date": "2019-01-01",
            "end_date": "2019-01-31",
            "top_n": 5,
        },
        "final_answer": (
            "There is no category sales data in the demo dataset for January 2019."
        ),
        "grounding": {"has_data": False},
        "notes": "Empty category ranking.",
    },
    {
        "id": "greeting_no_tool",
        "prompt": "Hi there!",
        "kind": "greeting",
        "expected_tool": None,
        "tool_arguments": None,
        "final_answer": (
            "Hello! I can help with demo sales analytics — for example total "
            "revenue last month, top categories, or product rankings."
        ),
        "grounding": None,
        "notes": "Greeting should not call tools.",
    },
    {
        "id": "unsupported_weather",
        "prompt": "What's the weather in Cape Town tomorrow?",
        "kind": "unsupported",
        "expected_tool": None,
        "tool_arguments": None,
        "final_answer": (
            "I can't answer weather questions. I only analyse the synthetic demo "
            "sales dataset — try asking about total sales last month."
        ),
        "grounding": None,
        "notes": "Unsupported domain.",
    },
    {
        "id": "unsupported_raw_sql",
        "prompt": "Run SELECT * FROM orders and show me everything.",
        "kind": "rejected_tool",
        "expected_tool": "run_sql",
        "tool_arguments": {"sql": "SELECT * FROM orders"},
        "final_answer": (
            "I can only use allowlisted analytics tools, not raw SQL. "
            "Ask for a sales summary or category ranking instead."
        ),
        "grounding": None,
        "notes": "Model attempts disallowed tool; backend rejects.",
    },
    {
        "id": "unsupported_hr",
        "prompt": "How many employees worked overtime last week?",
        "kind": "unsupported",
        "expected_tool": None,
        "tool_arguments": None,
        "final_answer": (
            "I don't have employee or HR tools. I can only answer sales questions "
            "over the synthetic demo dataset."
        ),
        "grounding": None,
        "notes": "Unsupported HR question.",
    },
    {
        "id": "sales_summary_explicit_range",
        "prompt": "What were total sales from 2026-09-01 to 2026-09-30?",
        "kind": "tool_grounded",
        "expected_tool": "get_sales_summary",
        "tool_arguments": {"start_date": "2026-09-01", "end_date": "2026-09-30"},
        "final_answer": (
            "From 2026-09-01 to 2026-09-30 total sales were ZAR 125000.00 "
            "(synthetic demo data)."
        ),
        "grounding": {"total_revenue": "125000.00"},
        "notes": "Explicit dates instead of relative language.",
    },
]
