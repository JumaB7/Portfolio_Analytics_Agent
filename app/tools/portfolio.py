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
from app.services import portfolio_analytics as analytics

TOOL_DEFINITIONS = [
    {
        "name": "get_owner_profile",
        "description": (
            "Return who the portfolio belongs to (name, role, location, summary). "
            "Use for 'who is Jumari', 'who are you', or about-the-person questions."
        ),
        "parameters_model": OwnerProfileInput,
        "result_model": OwnerProfileOutput,
    },
    {
        "name": "get_skills",
        "description": (
            "Return skill groups from the portfolio Skills section "
            "(Frontend, Backend, Databases, Tools). Optional group filter."
        ),
        "parameters_model": SkillsInput,
        "result_model": SkillsOutput,
    },
    {
        "name": "get_experience",
        "description": (
            "Return work and education experience entries from the portfolio "
            "(employer, dates, description, technologies)."
        ),
        "parameters_model": ExperienceInput,
        "result_model": ExperienceOutput,
    },
    {
        "name": "get_contact",
        "description": "Return the public contact email from the portfolio Contact section.",
        "parameters_model": ContactInput,
        "result_model": ContactOutput,
    },
    {
        "name": "get_portfolio_summary",
        "description": (
            "Return showcase KPIs matching the dashboard: project count, years of "
            "experience, distinct technologies, categories, and status counts. "
            "Use for overview / how many projects questions."
        ),
        "parameters_model": PortfolioSummaryInput,
        "result_model": PortfolioSummaryOutput,
    },
    {
        "name": "list_projects",
        "description": (
            "List portfolio projects, optionally filtered by category, technology, "
            "or status. Use when the user asks which projects use a stack or sit "
            "in a category."
        ),
        "parameters_model": ProjectListInput,
        "result_model": ProjectListOutput,
    },
    {
        "name": "get_technology_usage",
        "description": (
            "Rank technologies by how many showcase projects use them "
            "(dashboard technology mix). Use for most-used / tech stack questions."
        ),
        "parameters_model": TechnologyUsageInput,
        "result_model": TechnologyUsageOutput,
    },
    {
        "name": "get_category_distribution",
        "description": (
            "Rank project categories by count (dashboard category distribution). "
            "Use for category mix questions."
        ),
        "parameters_model": CategoryDistributionInput,
        "result_model": CategoryDistributionOutput,
    },
    {
        "name": "get_project_detail",
        "description": (
            "Look up one portfolio project by id or name and return its category, "
            "technologies, status, and description."
        ),
        "parameters_model": ProjectDetailInput,
        "result_model": ProjectDetailOutput,
    },
]


def get_owner_profile_tool(params: OwnerProfileInput) -> OwnerProfileOutput:
    return analytics.get_owner_profile(params)


def get_skills_tool(params: SkillsInput) -> SkillsOutput:
    return analytics.get_skills(params)


def get_experience_tool(params: ExperienceInput) -> ExperienceOutput:
    return analytics.get_experience(params)


def get_contact_tool(params: ContactInput) -> ContactOutput:
    return analytics.get_contact(params)


def get_portfolio_summary_tool(params: PortfolioSummaryInput) -> PortfolioSummaryOutput:
    return analytics.get_portfolio_summary(params)


def list_projects_tool(params: ProjectListInput) -> ProjectListOutput:
    return analytics.list_projects(params)


def get_technology_usage_tool(params: TechnologyUsageInput) -> TechnologyUsageOutput:
    return analytics.get_technology_usage(params)


def get_category_distribution_tool(
    params: CategoryDistributionInput,
) -> CategoryDistributionOutput:
    return analytics.get_category_distribution(params)


def get_project_detail_tool(params: ProjectDetailInput) -> ProjectDetailOutput:
    return analytics.get_project_detail(params)
