from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import DemoMeta, Order, OrderItem
from app.schemas.tools import SalesSummaryInput, SalesSummaryOutput


def _demo_label(session: Session) -> tuple[bool, str]:
    rows = {
        row.key: row.value
        for row in session.scalars(select(DemoMeta)).all()
    }
    is_demo = rows.get("is_demo_dataset", "false").lower() == "true"
    label = rows.get(
        "dataset_label",
        "SYNTHETIC DEMO DATA — fictional e-commerce store for portfolio demos",
    )
    return is_demo, label


def get_sales_summary(session: Session, params: SalesSummaryInput) -> SalesSummaryOutput:
    """Aggregate completed sales for an inclusive calendar date range.

    Read-only SELECT over allowlisted metrics. No dynamic SQL from callers.
    """
    is_demo, label = _demo_label(session)

    revenue_stmt = (
        select(
            func.coalesce(func.sum(OrderItem.line_total), 0),
            func.coalesce(func.sum(OrderItem.quantity), 0),
            func.count(func.distinct(Order.order_id)),
        )
        .select_from(OrderItem)
        .join(Order, Order.order_id == OrderItem.order_id)
        .where(
            Order.status == "completed",
            Order.order_date >= params.start_date,
            Order.order_date <= params.end_date,
        )
    )
    total_revenue, units_sold, order_count = session.execute(revenue_stmt).one()
    total_revenue = Decimal(total_revenue).quantize(Decimal("0.01"))
    units_sold = int(units_sold)
    order_count = int(order_count)
    has_data = order_count > 0

    message = None
    if not has_data:
        message = (
            f"No completed sales found between {params.start_date.isoformat()} "
            f"and {params.end_date.isoformat()} in the demo dataset."
        )

    return SalesSummaryOutput(
        start_date=params.start_date,
        end_date=params.end_date,
        currency="ZAR",
        total_revenue=total_revenue,
        order_count=order_count,
        units_sold=units_sold,
        has_data=has_data,
        is_demo_dataset=is_demo,
        dataset_label=label,
        message=message,
    )


def resolve_calendar_month(year: int, month: int) -> tuple[date, date]:
    """Inclusive start/end dates for a calendar month."""
    from calendar import monthrange

    if month < 1 or month > 12:
        raise ValueError("month must be 1–12")
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end
