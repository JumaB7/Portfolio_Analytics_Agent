from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from app.schemas.tools import (
    CategoryDistributionInput,
    CategoryDistributionOutput,
    ContactInput,
    ContactOutput,
    ExperienceInput,
    ExperienceOutput,
    OwnerProfileInput,
    OwnerProfileOutput,
    PortfolioSummaryInput,
    PortfolioSummaryOutput,
    ProjectDetailInput,
    ProjectDetailOutput,
    ProjectListInput,
    ProjectListOutput,
    SkillsInput,
    SkillsOutput,
    TechnologyUsageInput,
    TechnologyUsageOutput,
)
from app.tools.portfolio import (
    get_category_distribution_tool,
    get_contact_tool,
    get_experience_tool,
    get_owner_profile_tool,
    get_portfolio_summary_tool,
    get_project_detail_tool,
    get_skills_tool,
    get_technology_usage_tool,
    list_projects_tool,
)
from app.tools.registry import TOOL_DEFINITIONS

router = APIRouter(prefix="/tools", tags=["tools"])


class ToolListItem(BaseModel):
    name: str
    description: str


class ToolListResponse(BaseModel):
    tools: list[ToolListItem]


def _validate_or_422(model: type, payload: dict):  # noqa: ANN001
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc


@router.get("", response_model=ToolListResponse)
def list_tools() -> ToolListResponse:
    """Allowlisted tools available to the agent (no LLM)."""
    return ToolListResponse(
        tools=[
            ToolListItem(name=d["name"], description=d["description"])
            for d in TOOL_DEFINITIONS
        ]
    )


@router.get("/owner-profile", response_model=OwnerProfileOutput)
def owner_profile() -> OwnerProfileOutput:
    return get_owner_profile_tool(OwnerProfileInput())


@router.get("/skills", response_model=SkillsOutput)
def skills(group: str | None = None) -> SkillsOutput:
    return get_skills_tool(_validate_or_422(SkillsInput, {"group": group}))


@router.get("/experience", response_model=ExperienceOutput)
def experience() -> ExperienceOutput:
    return get_experience_tool(ExperienceInput())


@router.get("/contact", response_model=ContactOutput)
def contact() -> ContactOutput:
    return get_contact_tool(ContactInput())


@router.get("/portfolio-summary", response_model=PortfolioSummaryOutput)
def portfolio_summary() -> PortfolioSummaryOutput:
    return get_portfolio_summary_tool(PortfolioSummaryInput())


@router.get("/projects", response_model=ProjectListOutput)
def projects(
    category: str | None = None,
    technology: str | None = None,
    status: str | None = None,
) -> ProjectListOutput:
    params = _validate_or_422(
        ProjectListInput,
        {"category": category, "technology": technology, "status": status},
    )
    return list_projects_tool(params)


@router.get("/technology-usage", response_model=TechnologyUsageOutput)
def technology_usage(top_n: int = 10) -> TechnologyUsageOutput:
    params = _validate_or_422(TechnologyUsageInput, {"top_n": top_n})
    return get_technology_usage_tool(params)


@router.get("/category-distribution", response_model=CategoryDistributionOutput)
def category_distribution(top_n: int = 10) -> CategoryDistributionOutput:
    params = _validate_or_422(CategoryDistributionInput, {"top_n": top_n})
    return get_category_distribution_tool(params)


@router.get("/project-detail", response_model=ProjectDetailOutput)
def project_detail(query: str) -> ProjectDetailOutput:
    params = _validate_or_422(ProjectDetailInput, {"query": query})
    return get_project_detail_tool(params)
