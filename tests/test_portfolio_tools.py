from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app
from app.schemas.tools import (
    CategoryDistributionInput,
    OwnerProfileInput,
    PortfolioSummaryInput,
    ProjectDetailInput,
    ProjectListInput,
    TechnologyUsageInput,
)
from app.tools.portfolio import (
    get_category_distribution_tool,
    get_owner_profile_tool,
    get_portfolio_summary_tool,
    get_project_detail_tool,
    get_technology_usage_tool,
    list_projects_tool,
)

client = TestClient(app)


def setup_module() -> None:
    get_settings.cache_clear()
    # Force local seed so tests do not require PortfolioAPI to be running.
    get_settings()
    # Re-bind with empty API URL via monkeypatch-style Settings usage in fixtures below.


def test_owner_profile_seed(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    result = get_owner_profile_tool(OwnerProfileInput())
    assert result.has_data is True
    assert result.name == "Jumari Blignaut"
    assert "Software Engineer" in result.role
    assert result.project_count == 3


def test_portfolio_summary_seed(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    result = get_portfolio_summary_tool(PortfolioSummaryInput())
    assert result.has_data is True
    assert result.project_count == 3
    assert result.years_experience == 4
    assert result.technology_count >= 4
    assert result.category_count == 3


def test_list_projects_angular(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    result = list_projects_tool(ProjectListInput(technology="Angular"))
    assert result.has_data is True
    assert result.project_count == 3


def test_technology_usage(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    result = get_technology_usage_tool(TechnologyUsageInput(top_n=5))
    assert result.has_data is True
    assert result.technologies[0].project_count >= 2


def test_category_distribution(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    result = get_category_distribution_tool(CategoryDistributionInput())
    assert result.has_data is True
    assert len(result.categories) == 3


def test_project_detail_veld(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    result = get_project_detail_tool(ProjectDetailInput(query="Veld Supply"))
    assert result.has_data is True
    assert result.project is not None
    assert result.project.id == "veld-supply"
    assert result.project.status == "completed"


def test_tools_list_endpoint(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("PORTFOLIO_API_BASE_URL", "")
    get_settings.cache_clear()
    response = client.get("/api/tools")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()["tools"]}
    assert "get_portfolio_summary" in names
    assert "get_sales_summary" not in names
