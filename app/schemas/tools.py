from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


def _validate_inclusive_range(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")
    if (end_date - start_date).days > 366:
        raise ValueError("date range cannot exceed 366 days")


class SalesSummaryInput(BaseModel):
    """Validated arguments for get_sales_summary."""

    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_range(self) -> "SalesSummaryInput":
        _validate_inclusive_range(self.start_date, self.end_date)
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


class RevenueByCategoryInput(BaseModel):
    start_date: date
    end_date: date
    top_n: int = Field(default=5, ge=1, le=50)

    @model_validator(mode="after")
    def validate_range(self) -> "RevenueByCategoryInput":
        _validate_inclusive_range(self.start_date, self.end_date)
        return self


class CategoryRevenueRow(BaseModel):
    rank: int
    category: str
    revenue: Decimal
    order_count: int
    units_sold: int

    @field_validator("revenue")
    @classmethod
    def two_decimals(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class RevenueByCategoryOutput(BaseModel):
    start_date: date
    end_date: date
    currency: str = "ZAR"
    top_n: int
    categories: list[CategoryRevenueRow]
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None


class CompareSalesPeriodsInput(BaseModel):
    current_start_date: date
    current_end_date: date
    previous_start_date: date
    previous_end_date: date

    @model_validator(mode="after")
    def validate_ranges(self) -> "CompareSalesPeriodsInput":
        _validate_inclusive_range(self.current_start_date, self.current_end_date)
        _validate_inclusive_range(self.previous_start_date, self.previous_end_date)
        return self


class PeriodSnapshot(BaseModel):
    start_date: date
    end_date: date
    total_revenue: Decimal
    order_count: int
    units_sold: int
    has_data: bool

    @field_validator("total_revenue")
    @classmethod
    def two_decimals(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class CompareSalesPeriodsOutput(BaseModel):
    currency: str = "ZAR"
    current_period: PeriodSnapshot
    previous_period: PeriodSnapshot
    revenue_change: Decimal
    revenue_change_pct: Decimal | None = Field(
        default=None,
        description="Percent change vs previous revenue; null if previous revenue is 0",
    )
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None

    @field_validator("revenue_change")
    @classmethod
    def two_decimals_change(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class ProductPerformanceInput(BaseModel):
    start_date: date
    end_date: date
    sort: Literal["highest", "lowest"] = "highest"
    top_n: int = Field(default=5, ge=1, le=50)

    @model_validator(mode="after")
    def validate_range(self) -> "ProductPerformanceInput":
        _validate_inclusive_range(self.start_date, self.end_date)
        return self


class ProductPerformanceRow(BaseModel):
    rank: int
    product_name: str
    sku: str
    category: str
    revenue: Decimal
    units_sold: int
    order_count: int

    @field_validator("revenue")
    @classmethod
    def two_decimals(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class ProductPerformanceOutput(BaseModel):
    start_date: date
    end_date: date
    currency: str = "ZAR"
    sort: Literal["highest", "lowest"]
    top_n: int
    products: list[ProductPerformanceRow]
    has_data: bool
    is_demo_dataset: bool = True
    dataset_label: str
    message: str | None = None
