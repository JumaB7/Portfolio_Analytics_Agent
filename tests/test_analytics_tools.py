from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.db.seed import (
    EXPECTED_SEPTEMBER_2026,
    EXPECTED_SEPTEMBER_2026_LOWEST_PRODUCT,
    EXPECTED_SEPTEMBER_2026_TOP_CATEGORY,
    EXPECTED_SEPTEMBER_2026_TOP_PRODUCT,
    initialize_demo_database,
)
from app.main import app
from app.schemas.tools import (
    CompareSalesPeriodsInput,
    ProductPerformanceInput,
    RevenueByCategoryInput,
    SalesSummaryInput,
)
from app.tools.categories import get_revenue_by_category_tool
from app.tools.comparisons import compare_sales_periods_tool
from app.tools.products import get_product_performance_tool
from app.tools.sales import get_sales_summary_tool

client = TestClient(app)


def setup_module() -> None:
    initialize_demo_database()


def test_revenue_by_category_september() -> None:
    result = get_revenue_by_category_tool(
        RevenueByCategoryInput(
            start_date=EXPECTED_SEPTEMBER_2026["start_date"],
            end_date=EXPECTED_SEPTEMBER_2026["end_date"],
            top_n=5,
        )
    )
    assert result.has_data is True
    assert result.categories[0].category == EXPECTED_SEPTEMBER_2026_TOP_CATEGORY["category"]
    assert result.categories[0].revenue == EXPECTED_SEPTEMBER_2026_TOP_CATEGORY["revenue"]
    assert result.categories[0].order_count == EXPECTED_SEPTEMBER_2026_TOP_CATEGORY["order_count"]
    assert result.categories[0].units_sold == EXPECTED_SEPTEMBER_2026_TOP_CATEGORY["units_sold"]


def test_compare_sales_periods_sep_vs_aug() -> None:
    august = get_sales_summary_tool(
        SalesSummaryInput(start_date=date(2026, 8, 1), end_date=date(2026, 8, 31))
    )
    result = compare_sales_periods_tool(
        CompareSalesPeriodsInput(
            current_start_date=date(2026, 9, 1),
            current_end_date=date(2026, 9, 30),
            previous_start_date=date(2026, 8, 1),
            previous_end_date=date(2026, 8, 31),
        )
    )

    assert result.current_period.total_revenue == EXPECTED_SEPTEMBER_2026["total_revenue"]
    assert result.previous_period.total_revenue == august.total_revenue
    assert result.revenue_change == (
        EXPECTED_SEPTEMBER_2026["total_revenue"] - august.total_revenue
    ).quantize(Decimal("0.01"))
    assert result.revenue_change_pct is not None
    assert result.has_data is True


def test_product_performance_highest_and_lowest() -> None:
    highest = get_product_performance_tool(
        ProductPerformanceInput(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            sort="highest",
            top_n=5,
        )
    )
    lowest = get_product_performance_tool(
        ProductPerformanceInput(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            sort="lowest",
            top_n=5,
        )
    )

    assert highest.products[0].product_name == EXPECTED_SEPTEMBER_2026_TOP_PRODUCT["product_name"]
    assert highest.products[0].revenue == EXPECTED_SEPTEMBER_2026_TOP_PRODUCT["revenue"]
    assert lowest.products[0].product_name == EXPECTED_SEPTEMBER_2026_LOWEST_PRODUCT["product_name"]
    assert lowest.products[0].revenue == EXPECTED_SEPTEMBER_2026_LOWEST_PRODUCT["revenue"]


def test_new_tool_http_endpoints() -> None:
    category = client.get(
        "/api/tools/revenue-by-category",
        params={"start_date": "2026-09-01", "end_date": "2026-09-30"},
    )
    assert category.status_code == 200
    assert category.json()["categories"][0]["category"] == "Electronics"

    compare = client.get(
        "/api/tools/compare-sales-periods",
        params={
            "current_start_date": "2026-09-01",
            "current_end_date": "2026-09-30",
            "previous_start_date": "2026-08-01",
            "previous_end_date": "2026-08-31",
        },
    )
    assert compare.status_code == 200
    assert compare.json()["current_period"]["total_revenue"] == "125000.00"

    products = client.get(
        "/api/tools/product-performance",
        params={
            "start_date": "2026-09-01",
            "end_date": "2026-09-30",
            "sort": "lowest",
            "top_n": 3,
        },
    )
    assert products.status_code == 200
    assert products.json()["products"][0]["sku"] == "EL-PB-002"


def test_empty_category_range() -> None:
    result = get_revenue_by_category_tool(
        RevenueByCategoryInput(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 31),
        )
    )
    assert result.has_data is False
    assert result.categories == []
    assert result.message is not None
