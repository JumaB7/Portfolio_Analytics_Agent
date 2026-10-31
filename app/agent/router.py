"""Rule-based intent router for common portfolio analytics prompts.

Skips the LLM entirely when the question matches a known safe pattern.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from app.agent.answers import GREETING_ANSWER, UNSUPPORTED_ANSWER


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


def _has_word(text: str, word: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", text) is not None


def _is_dashboard_overview(text: str) -> bool:
    """True for meta questions about the showcase dashboard itself (not a project)."""
    if re.search(
        r"\b(what('?s| is)|explain|describe|about)\b.*\b(this|the)\s+dashboard\b",
        text,
    ):
        return True
    if re.search(r"\b(this|the)\s+dashboard\b.*\b(about|show|for|mean|do)\b", text):
        return True
    if re.search(r"\bwhat does (this|the) dashboard\b", text):
        return True
    return False


def _is_generic_project_query(query: str) -> bool:
    """Reject pronoun / meta phrases that are not project names."""
    q = query.strip().lower()
    if not q or q in {"this", "that", "it", "the dashboard", "this dashboard"}:
        return True
    if re.match(r"^(this|the|a|an|your|my)\s+", q) and "dashboard" in q:
        return True
    if q.endswith(" about") or " dashboard about" in f" {q} ":
        return True
    return False


def route_message(message: str) -> RouteDecision | None:
    """Return a route when confident; otherwise None (fall through to LLM)."""
    text = _normalize(message)

    if text in {"hi", "hello", "hey", "hi there"} or re.fullmatch(
        r"(hi|hello|hey)( there)?", text
    ):
        return RouteDecision(kind="greeting", answer=GREETING_ANSWER)

    if any(
        _has_word(text, needle)
        for needle in ("weather", "employee", "overtime", "sales", "revenue", "sku")
    ) or "select *" in text or "run sql" in text or re.search(r"\bhr\b", text):
        return RouteDecision(kind="unsupported", answer=UNSUPPORTED_ANSWER)

    if (
        re.search(r"\bwho is jumari\b", text)
        or re.search(r"\bwho'?s jumari\b", text)
        or re.search(r"\babout jumari\b", text)
        or text in {"who are you", "who built this", "who owns this portfolio"}
        or (
            _has_word(text, "jumari")
            and any(_has_word(text, w) for w in ("who", "about", "bio", "background"))
        )
    ):
        return RouteDecision(kind="tool", tool_name="get_owner_profile", arguments={})

    if (
        _has_word(text, "skill")
        or _has_word(text, "skills")
        or "tech stack" in text
        or "what can jumari" in text
    ):
        args: dict[str, Any] = {}
        for group in ("frontend", "backend", "databases", "tools"):
            if group in text:
                title = {
                    "frontend": "Frontend",
                    "backend": "Backend",
                    "databases": "Databases",
                    "tools": "Tools & Platforms",
                }[group]
                args["group"] = title
                break
        return RouteDecision(kind="tool", tool_name="get_skills", arguments=args)

    if (
        _has_word(text, "experience")
        or _has_word(text, "employer")
        or re.search(r"\bwork(ed|ing|s)?\b", text)
        or "where has" in text
        or "where did" in text
        or "matogen" in text
        or "education" in text
        or "degree" in text
        or "university" in text
    ):
        # "years of experience" is a KPI question, not the Experience section.
        if "years of experience" in text or "years experience" in text:
            pass
        else:
            return RouteDecision(kind="tool", tool_name="get_experience", arguments={})

    if (
        _has_word(text, "email")
        or _has_word(text, "contact")
        or "how can i reach" in text
        or "get in touch" in text
    ):
        return RouteDecision(kind="tool", tool_name="get_contact", arguments={})

    if _is_dashboard_overview(text) or any(
        phrase in text
        for phrase in (
            "how many projects",
            "project count",
            "portfolio summary",
            "overview of the portfolio",
            "dashboard summary",
            "years of experience",
            "years experience",
        )
    ) or (
        _has_word(text, "summary")
        and (_has_word(text, "portfolio") or _has_word(text, "dashboard"))
    ):
        return RouteDecision(kind="tool", tool_name="get_portfolio_summary", arguments={})

    if "technolog" in text and (
        "most" in text
        or "usage" in text
        or "used" in text
        or "mix" in text
        or re.search(r"\btop\b", text)
    ):
        return RouteDecision(
            kind="tool",
            tool_name="get_technology_usage",
            arguments={"top_n": 10},
        )

    if "categor" in text and (
        "distribution" in text
        or "mix" in text
        or "most" in text
        or re.search(r"\btop\b", text)
    ):
        return RouteDecision(
            kind="tool",
            tool_name="get_category_distribution",
            arguments={"top_n": 10},
        )

    detail = re.search(
        r"(?:tell me about|describe|details (?:on|for)|what is)\s+(.+)$",
        text,
    )
    if detail:
        query = detail.group(1).strip(" ?!.")
        if query and not _is_generic_project_query(query):
            return RouteDecision(
                kind="tool",
                tool_name="get_project_detail",
                arguments={"query": query},
            )

    for known in ("veld supply", "accountant app", "portfolio dashboard"):
        if known in text and (
            "about" in text or "detail" in text or "technologies" in text or "tech" in text
        ):
            return RouteDecision(
                kind="tool",
                tool_name="get_project_detail",
                arguments={"query": known},
            )

    if "angular" in text and ("project" in text or "which" in text or "use" in text):
        return RouteDecision(
            kind="tool",
            tool_name="list_projects",
            arguments={"technology": "Angular"},
        )

    if "list" in text and "project" in text:
        args: dict[str, Any] = {}
        if "completed" in text:
            args["status"] = "completed"
        elif "in progress" in text or "in-progress" in text:
            args["status"] = "in-progress"
        return RouteDecision(kind="tool", tool_name="list_projects", arguments=args)

    if text in {"how many projects are there", "how many projects do you have"}:
        return RouteDecision(kind="tool", tool_name="get_portfolio_summary", arguments={})

    return None
