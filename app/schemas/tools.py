from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator


class SalesSummaryInput(BaseModel):
    """Validated arguments for get_sales_summary."""

    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_range(self) -> "SalesSummaryInput":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if (self.end_date - self.start_date).days > 366:
            raise ValueError("date range cannot exceed 366 days")
        return self


class SalesSummaryOutput(BaseModel):
    """Structured tool result — numbers come from the database only."""

    start_date: date
    end_date: date
    currency: str = "ZAR"
    total_revenue: Decimal = Field(description="Sum of completed order line totals")
    order_count: int
    units_sold: int
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None

    @field_validator("total_revenue")
    @classmethod
    def two_decimals(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))
