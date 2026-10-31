"""Read-only analytics over the shared portfolio showcase dataset."""

from __future__ import annotations

from typing import Any

from app.schemas.tools import (
    CategoryDistributionInput,
    CategoryDistributionOutput,
    CategoryCountRow,
    ContactInput,
    ContactOutput,
    ExperienceInput,
    ExperienceOutput,
    ExperienceRow,
    OwnerHighlight,
    OwnerProfileInput,
    OwnerProfileOutput,
    PortfolioSummaryInput,
    PortfolioSummaryOutput,
    ProjectDetailInput,
    ProjectDetailOutput,
    ProjectListInput,
    ProjectListOutput,
    ProjectRow,
    SkillGroupRow,
    SkillsInput,
    SkillsOutput,
    TechnologyUsageInput,
    TechnologyUsageOutput,
    TechnologyCountRow,
)
from app.services.portfolio_client import load_portfolio_dataset


def _projects(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("projects") or []
    return [p for p in raw if isinstance(p, dict)]


def _label(data: dict[str, Any]) -> str:
    return str(
        data.get("sourceLabel")
        or "Synthetic showcase data derived from portfolio projects"
    )


def _is_demo(data: dict[str, Any]) -> bool:
    value = data.get("isDemoDataset")
    if isinstance(value, bool):
        return value
    return True


def _to_row(project: dict[str, Any]) -> ProjectRow:
    techs = project.get("technologies") or []
    return ProjectRow(
        id=str(project.get("id") or ""),
        name=str(project.get("name") or ""),
        category=str(project.get("category") or ""),
        technologies=[str(t) for t in techs],
        status=project.get("status"),
        description=project.get("description"),
    )


def get_portfolio_summary(_params: PortfolioSummaryInput) -> PortfolioSummaryOutput:
    data = load_portfolio_dataset()
    projects = _projects(data)
    techs = {t for p in projects for t in (p.get("technologies") or [])}
    categories = {str(p.get("category") or "") for p in projects if p.get("category")}
    statuses: dict[str, int] = {}
    for project in projects:
        status = str(project.get("status") or "unknown")
        statuses[status] = statuses.get(status, 0) + 1

    return PortfolioSummaryOutput(
        project_count=len(projects),
        years_experience=int(data.get("yearsExperience") or 0),
        technology_count=len(techs),
        category_count=len(categories),
        status_counts=statuses,
        has_data=len(projects) > 0,
        is_demo_dataset=_is_demo(data),
        dataset_label=_label(data),
        message=None if projects else "No portfolio projects in the showcase dataset.",
    )


def list_projects(params: ProjectListInput) -> ProjectListOutput:
    data = load_portfolio_dataset()
    projects = _projects(data)

    filtered: list[dict[str, Any]] = []
    for project in projects:
        if params.category and str(project.get("category") or "") != params.category:
            continue
        if params.status and str(project.get("status") or "") != params.status:
            continue
        if params.technology:
            techs = [str(t) for t in (project.get("technologies") or [])]
            if params.technology not in techs:
                continue
        filtered.append(project)

    rows = [_to_row(p) for p in filtered]
    return ProjectListOutput(
        filters={
            "category": params.category,
            "technology": params.technology,
            "status": params.status,
        },
        project_count=len(rows),
        projects=rows,
        has_data=len(rows) > 0,
        is_demo_dataset=_is_demo(data),
        dataset_label=_label(data),
        message=None if rows else "No projects matched those filters in the showcase dataset.",
    )


def get_technology_usage(params: TechnologyUsageInput) -> TechnologyUsageOutput:
    data = load_portfolio_dataset()
    projects = _projects(data)
    counts: dict[str, int] = {}
    for project in projects:
        for tech in project.get("technologies") or []:
            name = str(tech)
            counts[name] = counts.get(name, 0) + 1

    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[: params.top_n]
    rows = [
        TechnologyCountRow(rank=index, technology=name, project_count=count)
        for index, (name, count) in enumerate(ranked, start=1)
    ]
    return TechnologyUsageOutput(
        top_n=params.top_n,
        technologies=rows,
        has_data=len(rows) > 0,
        is_demo_dataset=_is_demo(data),
        dataset_label=_label(data),
        message=None if rows else "No technologies found in the showcase dataset.",
    )


def get_category_distribution(
    params: CategoryDistributionInput,
) -> CategoryDistributionOutput:
    data = load_portfolio_dataset()
    projects = _projects(data)
    counts: dict[str, int] = {}
    for project in projects:
        name = str(project.get("category") or "Other")
        counts[name] = counts.get(name, 0) + 1

    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[: params.top_n]
    rows = [
        CategoryCountRow(rank=index, category=name, project_count=count)
        for index, (name, count) in enumerate(ranked, start=1)
    ]
    return CategoryDistributionOutput(
        top_n=params.top_n,
        categories=rows,
        has_data=len(rows) > 0,
        is_demo_dataset=_is_demo(data),
        dataset_label=_label(data),
        message=None if rows else "No categories found in the showcase dataset.",
    )


def get_skills(params: SkillsInput) -> SkillsOutput:
    data = load_portfolio_dataset()
    raw = data.get("skillGroups") or []
    groups: list[SkillGroupRow] = []
    needle = (params.group or "").strip().lower()
    for item in raw:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "")
        if needle and needle not in title.lower():
            continue
        skills = [str(s) for s in (item.get("skills") or [])]
        groups.append(SkillGroupRow(title=title, skills=skills))
    return SkillsOutput(
        groups=groups,
        has_data=len(groups) > 0,
        is_demo_dataset=_is_demo(data),
        dataset_label=_label(data),
        message=None if groups else "No skill groups matched in the portfolio content.",
    )


def get_experience(_params: ExperienceInput) -> ExperienceOutput:
    data = load_portfolio_dataset()
    raw = data.get("experience") or []
    entries: list[ExperienceRow] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        entries.append(
            ExperienceRow(
                title=str(item.get("title") or ""),
                organization=str(item.get("organization") or ""),
                dates=str(item.get("dates") or ""),
                location=str(item.get("location") or ""),
                description=str(item.get("description") or ""),
                technologies=[str(t) for t in (item.get("technologies") or [])],
            )
        )
    return ExperienceOutput(
        entries=entries,
        has_data=len(entries) > 0,
        is_demo_dataset=_is_demo(data),
        dataset_label=_label(data),
        message=None if entries else "No experience entries in the portfolio content.",
    )


def get_contact(_params: ContactInput) -> ContactOutput:
    data = load_portfolio_dataset()
    contact = data.get("contact") if isinstance(data.get("contact"), dict) else {}
    email = str((contact or {}).get("email") or "").strip()
    return ContactOutput(
        email=email,
        has_data=bool(email),
        is_demo_dataset=_is_demo(data),
        dataset_label=_label(data),
        message=None if email else "No public contact email in the portfolio content.",
    )


def get_owner_profile(_params: OwnerProfileInput) -> OwnerProfileOutput:
    data = load_portfolio_dataset()
    owner = data.get("owner")
    projects = _projects(data)
    if not isinstance(owner, dict) or not owner.get("name"):
        return OwnerProfileOutput(
            name="",
            role="",
            location="",
            summary="",
            highlights=[],
            project_count=len(projects),
            years_experience=int(data.get("yearsExperience") or 0),
            has_data=False,
            is_demo_dataset=_is_demo(data),
            dataset_label=_label(data),
            message="No owner profile is present in the showcase dataset.",
        )

    raw_highlights = owner.get("highlights") or []
    highlights = [
        OwnerHighlight(label=str(h.get("label") or ""), value=str(h.get("value") or ""))
        for h in raw_highlights
        if isinstance(h, dict)
    ]
    return OwnerProfileOutput(
        name=str(owner.get("name") or ""),
        role=str(owner.get("role") or ""),
        location=str(owner.get("location") or ""),
        summary=str(owner.get("summary") or ""),
        highlights=highlights,
        project_count=len(projects),
        years_experience=int(data.get("yearsExperience") or 0),
        has_data=True,
        is_demo_dataset=_is_demo(data),
        dataset_label=_label(data),
        message=None,
    )


def get_project_detail(params: ProjectDetailInput) -> ProjectDetailOutput:
    data = load_portfolio_dataset()
    projects = _projects(data)
    needle = params.query.strip().lower()
    match: dict[str, Any] | None = None
    for project in projects:
        pid = str(project.get("id") or "").lower()
        name = str(project.get("name") or "").lower()
        if needle == pid or needle == name or needle in name:
            match = project
            break

    if match is None:
        return ProjectDetailOutput(
            query=params.query,
            project=None,
            has_data=False,
            is_demo_dataset=_is_demo(data),
            dataset_label=_label(data),
            message=f"No project matched '{params.query}' in the showcase dataset.",
        )

    return ProjectDetailOutput(
        query=params.query,
        project=_to_row(match),
        has_data=True,
        is_demo_dataset=_is_demo(data),
        dataset_label=_label(data),
        message=None,
    )
