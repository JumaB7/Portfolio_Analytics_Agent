from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.schemas.tools import (
    CompareSalesPeriodsInput,
    CompareSalesPeriodsOutput,
    ProductPerformanceInput,
    ProductPerformanceOutput,
    RevenueByCategoryInput,
    RevenueByCategoryOutput,
    SalesSummaryInput,
    SalesSummaryOutput,
)
from app.tools.categories import get_revenue_by_category_tool
from app.tools.comparisons import compare_sales_periods_tool
from app.tools.products import get_product_performance_tool
from app.tools.sales import get_sales_summary_tool

router = APIRouter(prefix="/tools", tags=["tools"])


def _validate_or_422(model: type, payload: dict):  # noqa: ANN001
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc


@router.get("/sales-summary", response_model=SalesSummaryOutput)
def sales_summary(start_date: str, end_date: str) -> SalesSummaryOutput:
    """Direct tool endpoint (no LLM)."""
    params = _validate_or_422(
        SalesSummaryInput, {"start_date": start_date, "end_date": end_date}
    )
    return get_sales_summary_tool(params)


@router.get("/revenue-by-category", response_model=RevenueByCategoryOutput)
def revenue_by_category(
    start_date: str, end_date: str, top_n: int = 5
) -> RevenueByCategoryOutput:
    params = _validate_or_422(
        RevenueByCategoryInput,
        {"start_date": start_date, "end_date": end_date, "top_n": top_n},
    )
    return get_revenue_by_category_tool(params)


@router.get("/compare-sales-periods", response_model=CompareSalesPeriodsOutput)
def compare_sales_periods(
    current_start_date: str,
    current_end_date: str,
    previous_start_date: str,
    previous_end_date: str,
) -> CompareSalesPeriodsOutput:
    params = _validate_or_422(
        CompareSalesPeriodsInput,
        {
            "current_start_date": current_start_date,
            "current_end_date": current_end_date,
            "previous_start_date": previous_start_date,
            "previous_end_date": previous_end_date,
        },
    )
    return compare_sales_periods_tool(params)


@router.get("/product-performance", response_model=ProductPerformanceOutput)
def product_performance(
    start_date: str,
    end_date: str,
    sort: str = "highest",
    top_n: int = 5,
) -> ProductPerformanceOutput:
    params = _validate_or_422(
        ProductPerformanceInput,
        {
            "start_date": start_date,
            "end_date": end_date,
            "sort": sort,
            "top_n": top_n,
        },
    )
    return get_product_performance_tool(params)
