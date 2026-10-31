"""Deterministic answer templates from allowlisted tool results.

Used to skip a second LLM round-trip after tools succeed.
"""

from __future__ import annotations

from typing import Any


def _zar(value: Any) -> str:
    amount = float(value or 0)
    return f"ZAR {amount:,.2f}"


def _range(start: Any, end: Any) -> str:
    return f"{start} to {end}"


def render_tool_answer(tool_name: str, result: dict[str, Any]) -> str | None:
    """Return a grounded template answer, or None if this tool has no template."""
    if tool_name == "get_sales_summary":
        start = result.get("start_date")
        end = result.get("end_date")
        if not result.get("has_data"):
            return (
                f"The demo dataset has no completed sales between {_range(start, end)}, "
                "so I cannot report revenue figures for that period."
            )
        return (
            f"Total sales for {_range(start, end)} were {_zar(result.get('total_revenue'))} "
            f"across {result.get('order_count', 0)} orders and {result.get('units_sold', 0)} units "
            "(synthetic demo data)."
        )

    if tool_name == "get_revenue_by_category":
        start = result.get("start_date")
        end = result.get("end_date")
        categories = result.get("categories") or []
        if not result.get("has_data") or not categories:
            return (
                f"There is no category sales data in the demo dataset between "
                f"{_range(start, end)}."
            )
        top = categories[0]
        return (
            f"The top category for {_range(start, end)} was {top.get('category')} "
            f"with {_zar(top.get('revenue'))} "
            f"({top.get('order_count', 0)} orders, synthetic demo data)."
        )

    if tool_name == "compare_sales_periods":
        current = result.get("current_period") or {}
        previous = result.get("previous_period") or {}
        if not result.get("has_data"):
            return "No completed sales found in either compared period in the demo dataset."
        change = result.get("revenue_change")
        pct = result.get("revenue_change_pct")
        pct_text = (
            "percent change is not defined because previous revenue was zero"
            if pct is None
            else f"a {pct}% change"
        )
        return (
            f"Current period {_range(current.get('start_date'), current.get('end_date'))} "
            f"revenue was {_zar(current.get('total_revenue'))}. "
            f"Previous period {_range(previous.get('start_date'), previous.get('end_date'))} "
            f"was {_zar(previous.get('total_revenue'))}. "
            f"Change: {_zar(change)} ({pct_text}). Synthetic demo data."
        )

    if tool_name == "get_product_performance":
        start = result.get("start_date")
        end = result.get("end_date")
        products = result.get("products") or []
        sort = result.get("sort") or "highest"
        if not result.get("has_data") or not products:
            return (
                f"There is no product sales data in the demo dataset between "
                f"{_range(start, end)}."
            )
        top = products[0]
        label = "highest-selling" if sort == "highest" else "lowest-selling"
        return (
            f"The {label} product for {_range(start, end)} was "
            f"{top.get('product_name')} ({top.get('sku')}) with "
            f"{_zar(top.get('revenue'))} and {top.get('units_sold', 0)} units "
            "(synthetic demo data)."
        )

    return None


def render_from_activity(
    activity: list[Any],
) -> str | None:
    """Template an answer from the last successful tool activity, if possible."""
    for item in reversed(activity):
        status = getattr(item, "status", None) or item.get("status")  # type: ignore[union-attr]
        result = getattr(item, "result", None) or item.get("result")  # type: ignore[union-attr]
        name = getattr(item, "tool_name", None) or item.get("tool_name")  # type: ignore[union-attr]
        if status == "ok" and isinstance(result, dict) and isinstance(name, str):
            answer = render_tool_answer(name, result)
            if answer:
                return answer
        if status == "rejected":
            return (
                "I can only use allowlisted analytics tools, not arbitrary or raw-SQL tools. "
                "Try asking about total sales, categories, period comparison, or product rankings."
            )
        if status == "error":
            detail = getattr(item, "detail", None) or (
                item.get("detail") if isinstance(item, dict) else None  # type: ignore[union-attr]
            )
            return (
                f"I couldn't complete that analytics tool call"
                f"{f' ({detail})' if detail else ''}. "
                "Please try a simpler sales question with an explicit date range."
            )
    return None


GREETING_ANSWER = (
    "Hello! I can help with demo sales analytics — for example total revenue last month, "
    "top categories, month-over-month changes, or product rankings."
)

UNSUPPORTED_ANSWER = (
    "I can't answer that with the available analytics tools. "
    "I only analyse the synthetic demo sales dataset — try total sales last month, "
    "top categories, period comparison, or product rankings."
)
