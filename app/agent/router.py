"""Rule-based intent router for common demo prompts.

Skips the LLM entirely when the question matches a known safe pattern.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

from app.agent.answers import GREETING_ANSWER, UNSUPPORTED_ANSWER
from app.services.analytics import resolve_calendar_month


@dataclass(frozen=True)
class RouteDecision:
    kind: Literal["tool", "greeting", "unsupported"]
    tool_name: str | None = None
    arguments: dict[str, Any] | None = None
    answer: str | None = None


def _normalize(text: str) -> str:
    cleaned = text.strip().lower()
    cleaned = re.sub(r"[?!.,]+$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _last_month_range(today: date) -> tuple[date, date]:
    if today.month == 1:
        return resolve_calendar_month(today.year - 1, 12)
    return resolve_calendar_month(today.year, today.month - 1)


def _previous_month_range(today: date) -> tuple[date, date]:
    last_start, _ = _last_month_range(today)
    if last_start.month == 1:
        return resolve_calendar_month(last_start.year - 1, 12)
    return resolve_calendar_month(last_start.year, last_start.month - 1)


def route_message(message: str, *, today: date | None = None) -> RouteDecision | None:
    """Return a route when confident; otherwise None (fall through to LLM)."""
    today = today or date.today()
    text = _normalize(message)

    if text in {"hi", "hello", "hey", "hi there", "hello!", "hey!"} or text.startswith(
        "hi "
    ):
        return RouteDecision(kind="greeting", answer=GREETING_ANSWER)

    if any(
        needle in text
        for needle in (
            "weather",
            "select *",
            "select * from",
            "run sql",
            "employee",
            "overtime",
            "hr ",
        )
    ):
        return RouteDecision(kind="unsupported", answer=UNSUPPORTED_ANSWER)

    last_start, last_end = _last_month_range(today)
    prev_start, prev_end = _previous_month_range(today)
    last_args = {
        "start_date": last_start.isoformat(),
        "end_date": last_end.isoformat(),
    }

    # Explicit ISO range for sales summary.
    explicit = re.search(
        r"total sales from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})",
        text,
    )
    if explicit:
        return RouteDecision(
            kind="tool",
            tool_name="get_sales_summary",
            arguments={
                "start_date": explicit.group(1),
                "end_date": explicit.group(2),
            },
        )

    if "total sales" in text or "total revenue" in text or "our total sales" in text:
        if "last month" in text or "previous month" in text:
            return RouteDecision(
                kind="tool",
                tool_name="get_sales_summary",
                arguments=last_args,
            )
        # January 2019 style empty-data demos
        jan_2019 = re.search(r"january\s+2019", text)
        if jan_2019:
            return RouteDecision(
                kind="tool",
                tool_name="get_sales_summary",
                arguments={"start_date": "2019-01-01", "end_date": "2019-01-31"},
            )

    if "category" in text and (
        "most revenue" in text or "top" in text or "sold best" in text or "generated" in text
    ):
        if "2019" in text:
            return RouteDecision(
                kind="tool",
                tool_name="get_revenue_by_category",
                arguments={
                    "start_date": "2019-01-01",
                    "end_date": "2019-01-31",
                    "top_n": 5,
                },
            )
        return RouteDecision(
            kind="tool",
            tool_name="get_revenue_by_category",
            arguments={**last_args, "top_n": 5},
        )

    if (
        "compared with the previous month" in text
        or "month over month" in text
        or "month-over-month" in text
        or ("sales change" in text and "previous month" in text)
    ):
        return RouteDecision(
            kind="tool",
            tool_name="compare_sales_periods",
            arguments={
                "current_start_date": last_start.isoformat(),
                "current_end_date": last_end.isoformat(),
                "previous_start_date": prev_start.isoformat(),
                "previous_end_date": prev_end.isoformat(),
            },
        )

    if "product" in text and ("lowest" in text or "weakest" in text):
        return RouteDecision(
            kind="tool",
            tool_name="get_product_performance",
            arguments={**last_args, "sort": "lowest", "top_n": 5},
        )

    if "product" in text and ("highest" in text or "top" in text or "best" in text):
        return RouteDecision(
            kind="tool",
            tool_name="get_product_performance",
            arguments={**last_args, "sort": "highest", "top_n": 5},
        )

    return None
