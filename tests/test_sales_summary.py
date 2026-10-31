from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.db.seed import EXPECTED_SEPTEMBER_2026, initialize_demo_database
from app.main import app
from app.schemas.tools import SalesSummaryInput
from app.tools.sales import get_sales_summary_tool

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def _seed_demo_db() -> None:
    initialize_demo_database()


def test_sales_summary_september_2026_matches_seed() -> None:
    params = SalesSummaryInput(
        start_date=EXPECTED_SEPTEMBER_2026["start_date"],
        end_date=EXPECTED_SEPTEMBER_2026["end_date"],
    )
    result = get_sales_summary_tool(params)

    assert result.has_data is True
    assert result.is_demo_dataset is True
    assert "DEMO" in result.dataset_label.upper()
    assert result.currency == "ZAR"
    assert result.total_revenue == EXPECTED_SEPTEMBER_2026["total_revenue"]
    assert result.order_count == EXPECTED_SEPTEMBER_2026["order_count"]
    assert result.units_sold == EXPECTED_SEPTEMBER_2026["units_sold"]
    assert result.message is None


def test_sales_summary_empty_range() -> None:
    params = SalesSummaryInput(
        start_date=date(2019, 1, 1),
        end_date=date(2019, 1, 31),
    )
    result = get_sales_summary_tool(params)

    assert result.has_data is False
    assert result.total_revenue == Decimal("0.00")
    assert result.order_count == 0
    assert result.units_sold == 0
    assert result.message is not None


def test_sales_summary_rejects_inverted_range() -> None:
    with pytest.raises(ValidationError):
        SalesSummaryInput(start_date=date(2026, 9, 30), end_date=date(2026, 9, 1))


def test_sales_summary_http_endpoint() -> None:
    response = client.get(
        "/api/tools/sales-summary",
        params={"start_date": "2026-09-01", "end_date": "2026-09-30"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_revenue"] == "125000.00"
    assert body["order_count"] == 30
    assert body["is_demo_dataset"] is True
