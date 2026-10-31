from typing import Any, Literal

from pydantic import BaseModel, Field


class PortfolioSummaryInput(BaseModel):
    """No arguments — returns dashboard-level KPIs."""


class PortfolioSummaryOutput(BaseModel):
    project_count: int
    years_experience: int
    technology_count: int
    category_count: int
    status_counts: dict[str, int] = Field(default_factory=dict)
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None


class ProjectListInput(BaseModel):
    category: str | None = Field(
        default=None,
        description="Optional exact category filter, e.g. 'AI/data analytics'.",
    )
    technology: str | None = Field(
        default=None,
        description="Optional technology filter, e.g. 'Angular'.",
    )
    status: Literal["completed", "in-progress"] | None = Field(
        default=None,
        description="Optional status filter.",
    )


class ProjectRow(BaseModel):
    id: str
    name: str
    category: str
    technologies: list[str]
    status: str | None = None
    description: str | None = None


class ProjectListOutput(BaseModel):
    filters: dict[str, Any]
    project_count: int
    projects: list[ProjectRow]
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None


class TechnologyUsageInput(BaseModel):
    top_n: int = Field(default=10, ge=1, le=50)


class TechnologyCountRow(BaseModel):
    rank: int
    technology: str
    project_count: int


class TechnologyUsageOutput(BaseModel):
    top_n: int
    technologies: list[TechnologyCountRow]
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None


class CategoryDistributionInput(BaseModel):
    top_n: int = Field(default=10, ge=1, le=50)


class CategoryCountRow(BaseModel):
    rank: int
    category: str
    project_count: int


class CategoryDistributionOutput(BaseModel):
    top_n: int
    categories: list[CategoryCountRow]
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None


class ProjectDetailInput(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=120,
        description="Project id or name to look up (e.g. 'Veld Supply' or 'veld-supply').",
    )


class ProjectDetailOutput(BaseModel):
    query: str
    project: ProjectRow | None = None
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None


class OwnerProfileInput(BaseModel):
    """No arguments — returns the portfolio owner profile from the shared dataset."""


class OwnerHighlight(BaseModel):
    label: str
    value: str


class OwnerProfileOutput(BaseModel):
    name: str
    role: str
    location: str
    summary: str
    highlights: list[OwnerHighlight] = Field(default_factory=list)
    project_count: int = 0
    years_experience: int = 0
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None


class SkillsInput(BaseModel):
    """Optional group filter, e.g. Frontend / Backend."""

    group: str | None = Field(
        default=None,
        description="Optional skill group title filter (e.g. 'Frontend').",
    )


class SkillGroupRow(BaseModel):
    title: str
    skills: list[str]


class SkillsOutput(BaseModel):
    groups: list[SkillGroupRow]
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None


class ExperienceInput(BaseModel):
    """No arguments — returns work / education experience entries."""


class ExperienceRow(BaseModel):
    title: str
    organization: str
    dates: str
    location: str
    description: str
    technologies: list[str] = Field(default_factory=list)


class ExperienceOutput(BaseModel):
    entries: list[ExperienceRow]
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None


class ContactInput(BaseModel):
    """No arguments — returns public contact details from the portfolio."""


class ContactOutput(BaseModel):
    email: str
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None
