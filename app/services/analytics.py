from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Category, DemoMeta, Order, OrderItem, Product
from app.schemas.tools import (
    CategoryRevenueRow,
    CompareSalesPeriodsInput,
    CompareSalesPeriodsOutput,
    PeriodSnapshot,
    ProductPerformanceInput,
    ProductPerformanceOutput,
    ProductPerformanceRow,
    RevenueByCategoryInput,
    RevenueByCategoryOutput,
    SalesSummaryInput,
    SalesSummaryOutput,
)


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


def _period_totals(
    session: Session, start_date: date, end_date: date
) -> tuple[Decimal, int, int]:
    stmt = (
        select(
            func.coalesce(func.sum(OrderItem.line_total), 0),
            func.coalesce(func.sum(OrderItem.quantity), 0),
            func.count(func.distinct(Order.order_id)),
        )
        .select_from(OrderItem)
        .join(Order, Order.order_id == OrderItem.order_id)
        .where(
            Order.status == "completed",
            Order.order_date >= start_date,
            Order.order_date <= end_date,
        )
    )
    total_revenue, units_sold, order_count = session.execute(stmt).one()
    return (
        Decimal(total_revenue).quantize(Decimal("0.01")),
        int(units_sold),
        int(order_count),
    )


def get_sales_summary(session: Session, params: SalesSummaryInput) -> SalesSummaryOutput:
    """Aggregate completed sales for an inclusive calendar date range."""
    is_demo, label = _demo_label(session)
    total_revenue, units_sold, order_count = _period_totals(
        session, params.start_date, params.end_date
    )
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


def get_revenue_by_category(
    session: Session, params: RevenueByCategoryInput
) -> RevenueByCategoryOutput:
    """Rank categories by revenue for an inclusive date range."""
    is_demo, label = _demo_label(session)

    stmt = (
        select(
            Category.name,
            func.coalesce(func.sum(OrderItem.line_total), 0).label("revenue"),
            func.count(func.distinct(Order.order_id)).label("order_count"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold"),
        )
        .select_from(OrderItem)
        .join(Order, Order.order_id == OrderItem.order_id)
        .join(Product, Product.product_id == OrderItem.product_id)
        .join(Category, Category.category_id == Product.category_id)
        .where(
            Order.status == "completed",
            Order.order_date >= params.start_date,
            Order.order_date <= params.end_date,
        )
        .group_by(Category.name)
        .order_by(func.sum(OrderItem.line_total).desc(), Category.name.asc())
        .limit(params.top_n)
    )
    rows = session.execute(stmt).all()
    categories = [
        CategoryRevenueRow(
            rank=index,
            category=name,
            revenue=Decimal(revenue),
            order_count=int(order_count),
            units_sold=int(units_sold),
        )
        for index, (name, revenue, order_count, units_sold) in enumerate(rows, start=1)
    ]
    has_data = len(categories) > 0
    message = None
    if not has_data:
        message = (
            f"No category sales found between {params.start_date.isoformat()} "
            f"and {params.end_date.isoformat()} in the demo dataset."
        )

    return RevenueByCategoryOutput(
        start_date=params.start_date,
        end_date=params.end_date,
        currency="ZAR",
        top_n=params.top_n,
        categories=categories,
        has_data=has_data,
        is_demo_dataset=is_demo,
        dataset_label=label,
        message=message,
    )


def compare_sales_periods(
    session: Session, params: CompareSalesPeriodsInput
) -> CompareSalesPeriodsOutput:
    """Compare two inclusive periods for revenue / orders / units."""
    is_demo, label = _demo_label(session)

    current_revenue, current_units, current_orders = _period_totals(
        session, params.current_start_date, params.current_end_date
    )
    previous_revenue, previous_units, previous_orders = _period_totals(
        session, params.previous_start_date, params.previous_end_date
    )

    current = PeriodSnapshot(
        start_date=params.current_start_date,
        end_date=params.current_end_date,
        total_revenue=current_revenue,
        order_count=current_orders,
        units_sold=current_units,
        has_data=current_orders > 0,
    )
    previous = PeriodSnapshot(
        start_date=params.previous_start_date,
        end_date=params.previous_end_date,
        total_revenue=previous_revenue,
        order_count=previous_orders,
        units_sold=previous_units,
        has_data=previous_orders > 0,
    )

    revenue_change = (current_revenue - previous_revenue).quantize(Decimal("0.01"))
    revenue_change_pct: Decimal | None
    if previous_revenue == 0:
        revenue_change_pct = None
    else:
        revenue_change_pct = (
            (revenue_change / previous_revenue) * Decimal("100")
        ).quantize(Decimal("0.01"))

    has_data = current.has_data or previous.has_data
    message = None
    if not has_data:
        message = "No completed sales found in either compared period in the demo dataset."
    elif previous_revenue == 0 and current.has_data:
        message = "Previous period had zero revenue; percent change is not defined."

    return CompareSalesPeriodsOutput(
        currency="ZAR",
        current_period=current,
        previous_period=previous,
        revenue_change=revenue_change,
        revenue_change_pct=revenue_change_pct,
        has_data=has_data,
        is_demo_dataset=is_demo,
        dataset_label=label,
        message=message,
    )


def get_product_performance(
    session: Session, params: ProductPerformanceInput
) -> ProductPerformanceOutput:
    """Rank products by revenue for an inclusive date range."""
    is_demo, label = _demo_label(session)

    revenue_expr = func.sum(OrderItem.line_total)
    order_by = (
        revenue_expr.asc()
        if params.sort == "lowest"
        else revenue_expr.desc()
    )

    stmt = (
        select(
            Product.name,
            Product.sku,
            Category.name,
            func.coalesce(revenue_expr, 0).label("revenue"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold"),
            func.count(func.distinct(Order.order_id)).label("order_count"),
        )
        .select_from(OrderItem)
        .join(Order, Order.order_id == OrderItem.order_id)
        .join(Product, Product.product_id == OrderItem.product_id)
        .join(Category, Category.category_id == Product.category_id)
        .where(
            Order.status == "completed",
            Order.order_date >= params.start_date,
            Order.order_date <= params.end_date,
        )
        .group_by(Product.name, Product.sku, Category.name)
        .order_by(order_by, Product.name.asc())
        .limit(params.top_n)
    )
    rows = session.execute(stmt).all()
    products = [
        ProductPerformanceRow(
            rank=index,
            product_name=name,
            sku=sku,
            category=category,
            revenue=Decimal(revenue),
            units_sold=int(units_sold),
            order_count=int(order_count),
        )
        for index, (name, sku, category, revenue, units_sold, order_count) in enumerate(
            rows, start=1
        )
    ]
    has_data = len(products) > 0
    message = None
    if not has_data:
        message = (
            f"No product sales found between {params.start_date.isoformat()} "
            f"and {params.end_date.isoformat()} in the demo dataset."
        )

    return ProductPerformanceOutput(
        start_date=params.start_date,
        end_date=params.end_date,
        currency="ZAR",
        sort=params.sort,
        top_n=params.top_n,
        products=products,
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
