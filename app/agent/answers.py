"""Deterministic answer templates from allowlisted tool results.

Used to skip a second LLM round-trip after tools succeed.
"""

from __future__ import annotations

from typing import Any


def _first_sentence(text: str) -> str:
    cleaned = " ".join((text or "").split()).strip()
    if not cleaned:
        return ""
    # Keep a short spoken bio — full resume dumps feel copy-pasted.
    parts = cleaned.split(". ")
    first = parts[0].rstrip(".")
    return f"{first}."


def _render_owner_profile(result: dict[str, Any], label: str) -> str:
    name = str(result.get("name") or "The portfolio owner").strip()
    role = str(result.get("role") or "software engineer").strip()
    location = str(result.get("location") or "").strip()
    summary = _first_sentence(str(result.get("summary") or ""))
    projects = result.get("project_count", 0)

    # Drop a leading role echo so we don't say "X is a Full-Stack… Full-Stack…"
    if summary.lower().startswith(role.lower()):
        remainder = summary[len(role) :].lstrip(" ,.")
        summary = remainder[:1].upper() + remainder[1:] if remainder else ""

    where = f" based in {location}" if location else ""
    lead = f"{name} is a {role}{where}."
    mid = f" {summary}" if summary else ""
    close = f" This showcase covers {projects} of their projects."
    return f"{lead}{mid}{close} (Showcase data: {label}.)"


def render_tool_answer(tool_name: str, result: dict[str, Any]) -> str | None:
    """Return a grounded template answer, or None if this tool has no template."""
    label = result.get("dataset_label") or "showcase portfolio data"

    if tool_name == "get_owner_profile":
        if not result.get("has_data"):
            return "The showcase dataset has no owner profile to share."
        return _render_owner_profile(result, label)

    if tool_name == "get_skills":
        groups = result.get("groups") or []
        if not result.get("has_data") or not groups:
            return f"No matching skills found in the portfolio content ({label})."
        bits = []
        for group in groups:
            skills = ", ".join(group.get("skills") or [])
            bits.append(f"{group.get('title')}: {skills}")
        return f"Skills on the portfolio — {'; '.join(bits)}."

    if tool_name == "get_experience":
        entries = result.get("entries") or []
        if not result.get("has_data") or not entries:
            return f"No experience entries found in the portfolio content ({label})."
        bits = []
        for entry in entries:
            bits.append(
                f"{entry.get('title')} at {entry.get('organization')} "
                f"({entry.get('dates')}) — {entry.get('description')}"
            )
        return " ".join(bits)

    if tool_name == "get_contact":
        if not result.get("has_data"):
            return f"No public contact email is listed in the portfolio content ({label})."
        return f"You can reach Jumari at {result.get('email')}."

    if tool_name == "get_portfolio_summary":
        if not result.get("has_data"):
            return "The showcase dataset has no portfolio projects to summarise."
        statuses = result.get("status_counts") or {}
        status_bits = ", ".join(f"{k}: {v}" for k, v in statuses.items()) or "n/a"
        return (
            "This portfolio currently showcases "
            f"{result.get('project_count', 0)} projects, "
            f"~{result.get('years_experience', 0)} years of experience, "
            f"{result.get('technology_count', 0)} distinct project technologies, and "
            f"{result.get('category_count', 0)} categories "
            f"(status mix — {status_bits})."
        )

    if tool_name == "list_projects":
        projects = result.get("projects") or []
        if not result.get("has_data") or not projects:
            return f"No projects matched those filters in the showcase dataset ({label})."
        names = ", ".join(str(p.get("name")) for p in projects)
        return (
            f"Found {result.get('project_count', len(projects))} project(s): {names}. "
            f"Source: {label}."
        )

    if tool_name == "get_technology_usage":
        rows = result.get("technologies") or []
        if not result.get("has_data") or not rows:
            return f"No technology usage data in the showcase dataset ({label})."
        top = rows[0]
        return (
            f"The most-used technology is {top.get('technology')} "
            f"({top.get('project_count')} projects). Source: {label}."
        )

    if tool_name == "get_category_distribution":
        rows = result.get("categories") or []
        if not result.get("has_data") or not rows:
            return f"No category distribution data in the showcase dataset ({label})."
        top = rows[0]
        return (
            f"The largest category is {top.get('category')} "
            f"({top.get('project_count')} projects). Source: {label}."
        )

    if tool_name == "get_project_detail":
        project = result.get("project")
        if not result.get("has_data") or not project:
            return result.get("message") or (
                f"No matching project in the showcase dataset ({label})."
            )
        techs = ", ".join(project.get("technologies") or []) or "n/a"
        return (
            f"{project.get('name')} is in '{project.get('category')}' "
            f"(status: {project.get('status') or 'n/a'}) and uses {techs}. "
            f"Source: {label}."
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
                "I can only use allowlisted portfolio tools, not arbitrary or raw-SQL "
                "tools. Try asking about Jumari, skills, experience, projects, or contact."
            )
        if status == "error":
            detail = getattr(item, "detail", None) or (
                item.get("detail") if isinstance(item, dict) else None  # type: ignore[union-attr]
            )
            return (
                f"I couldn't complete that tool call"
                f"{f' ({detail})' if detail else ''}. "
                "Please try a simpler portfolio question."
            )
    return None


GREETING_ANSWER = (
    "Hello! I can answer questions about this portfolio — who Jumari is, skills, "
    "experience, projects, technologies, or how to get in touch."
)

UNSUPPORTED_ANSWER = (
    "I can't answer that with the available portfolio tools. "
    "Try asking about Jumari, skills, experience, projects, technologies, or contact."
)
