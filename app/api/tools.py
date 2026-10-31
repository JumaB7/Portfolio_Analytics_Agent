from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.schemas.tools import SalesSummaryInput, SalesSummaryOutput
from app.tools.sales import get_sales_summary_tool

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/sales-summary", response_model=SalesSummaryOutput)
def sales_summary(start_date: str, end_date: str) -> SalesSummaryOutput:
    """Direct tool endpoint for step-2 verification (no LLM)."""
    try:
        params = SalesSummaryInput.model_validate(
            {"start_date": start_date, "end_date": end_date}
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    return get_sales_summary_tool(params)
