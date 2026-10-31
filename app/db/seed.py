"""Create and seed the AnalyticsDemo SQL Server database.

All rows are synthetic. DemoMeta.is_demo_dataset = true.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.db.models import Base, Category, DemoMeta, Order, OrderItem, Product
from app.db.session import build_database_url, build_master_url, reset_engine_cache

DEMO_DATABASE_NAME = "AnalyticsDemo"

# Documented expected totals for tests (inclusive calendar months, completed orders).
EXPECTED_SEPTEMBER_2026 = {
    "start_date": date(2026, 9, 1),
    "end_date": date(2026, 9, 30),
    "total_revenue": Decimal("125000.00"),
    "order_count": 30,
    "units_sold": 250,
}

# September seed is Electronics-only: headphones R80k + power banks R45k.
EXPECTED_SEPTEMBER_2026_TOP_CATEGORY = {
    "category": "Electronics",
    "revenue": Decimal("125000.00"),
    "order_count": 30,
    "units_sold": 250,
}

EXPECTED_SEPTEMBER_2026_TOP_PRODUCT = {
    "product_name": "Trail Headphones",
    "sku": "EL-HD-001",
    "category": "Electronics",
    "revenue": Decimal("80000.00"),
    "units_sold": 200,
    "order_count": 20,
}

EXPECTED_SEPTEMBER_2026_LOWEST_PRODUCT = {
    "product_name": "Portable Power Bank",
    "sku": "EL-PB-002",
    "category": "Electronics",
    "revenue": Decimal("45000.00"),
    "units_sold": 50,
    "order_count": 10,
}

CATEGORIES = [
    "Electronics",
    "Outdoor",
    "Home",
    "Apparel",
]

PRODUCTS = [
    ("Electronics", "Trail Headphones", "EL-HD-001", Decimal("899.00")),
    ("Electronics", "Portable Power Bank", "EL-PB-002", Decimal("449.00")),
    ("Outdoor", "Hiking Daypack", "OD-DP-010", Decimal("1299.00")),
    ("Outdoor", "Camp Cook Set", "OD-CK-011", Decimal("659.00")),
    ("Home", "Ceramic Mug Set", "HM-MG-020", Decimal("299.00")),
    ("Home", "Desk Lamp", "HM-LM-021", Decimal("549.00")),
    ("Apparel", "Merino Base Layer", "AP-BL-030", Decimal("799.00")),
    ("Apparel", "Softshell Jacket", "AP-JK-031", Decimal("1899.00")),
]

REGIONS = ["Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape"]


def ensure_database_exists() -> None:
    """Create AnalyticsDemo on LocalDB if it does not exist."""
    engine = create_engine(build_master_url(), isolation_level="AUTOCOMMIT", future=True)
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT database_id FROM sys.databases WHERE name = :name"),
            {"name": DEMO_DATABASE_NAME},
        ).scalar()
        if exists is None:
            conn.execute(text(f"CREATE DATABASE [{DEMO_DATABASE_NAME}]"))
    engine.dispose()


def reset_schema(session: Session) -> None:
    bind = session.get_bind()
    Base.metadata.drop_all(bind=bind)
    Base.metadata.create_all(bind=bind)


def _month_dates(year: int, month: int) -> list[date]:
    days = monthrange(year, month)[1]
    return [date(year, month, day) for day in range(1, days + 1)]


def seed_demo_data(session: Session) -> None:
    """Replace all demo rows with a deterministic synthetic dataset."""
    reset_schema(session)

    session.add_all(
        [
            DemoMeta(key="is_demo_dataset", value="true"),
            DemoMeta(
                key="dataset_label",
                value="SYNTHETIC DEMO DATA — fictional e-commerce store for portfolio demos",
            ),
            DemoMeta(key="currency", value="ZAR"),
            DemoMeta(key="seed_version", value="1"),
        ]
    )

    categories: dict[str, Category] = {}
    for name in CATEGORIES:
        category = Category(name=name)
        session.add(category)
        categories[name] = category
    session.flush()

    products: list[Product] = []
    for category_name, name, sku, unit_price in PRODUCTS:
        product = Product(
            category_id=categories[category_name].category_id,
            name=name,
            sku=sku,
            unit_price=unit_price,
        )
        session.add(product)
        products.append(product)
    session.flush()

    # Jan–Aug 2026: light background volume so trends look believable.
    for month in range(1, 9):
        for day_index, order_day in enumerate(_month_dates(2026, month)):
            if day_index % 3 != 0:
                continue
            product = products[day_index % len(products)]
            quantity = 1 + (day_index % 3)
            line_total = (product.unit_price * quantity).quantize(Decimal("0.01"))
            order = Order(
                order_date=order_day,
                region=REGIONS[day_index % len(REGIONS)],
                status="completed",
                created_at=datetime.combine(order_day, datetime.min.time()) + timedelta(hours=10),
            )
            session.add(order)
            session.flush()
            session.add(
                OrderItem(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_price=product.unit_price,
                    line_total=line_total,
                )
            )

    # September 2026: fixed totals for tests (R 125,000 / 30 orders / 250 units).
    # 20 x R4,000 + 10 x R4,500 = R125,000; units 200 + 50 = 250.
    sep_product = products[0]
    for i in range(20):
        order_day = date(2026, 9, 1 + (i % 30))
        order = Order(
            order_date=order_day,
            region=REGIONS[i % len(REGIONS)],
            status="completed",
            created_at=datetime.combine(order_day, datetime.min.time()) + timedelta(hours=12),
        )
        session.add(order)
        session.flush()
        session.add(
            OrderItem(
                order_id=order.order_id,
                product_id=sep_product.product_id,
                quantity=10,
                unit_price=Decimal("400.00"),
                line_total=Decimal("4000.00"),
            )
        )
    for i in range(10):
        order_day = date(2026, 9, 1 + (i % 30))
        order = Order(
            order_date=order_day,
            region=REGIONS[i % len(REGIONS)],
            status="completed",
            created_at=datetime.combine(order_day, datetime.min.time()) + timedelta(hours=15),
        )
        session.add(order)
        session.flush()
        session.add(
            OrderItem(
                order_id=order.order_id,
                product_id=products[1].product_id,
                quantity=5,
                unit_price=Decimal("900.00"),
                line_total=Decimal("4500.00"),
            )
        )

    # October 2026: smaller month so MoM comparisons have a drop.
    for i in range(10):
        order_day = date(2026, 10, 1 + i)
        product = products[i % len(products)]
        quantity = 2
        line_total = (product.unit_price * quantity).quantize(Decimal("0.01"))
        order = Order(
            order_date=order_day,
            region=REGIONS[i % len(REGIONS)],
            status="completed",
            created_at=datetime.combine(order_day, datetime.min.time()) + timedelta(hours=11),
        )
        session.add(order)
        session.flush()
        session.add(
            OrderItem(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=quantity,
                unit_price=product.unit_price,
                line_total=line_total,
            )
        )

    session.flush()


def initialize_demo_database(database_url: str | None = None) -> None:
    """Create DB (LocalDB default), reset schema, and seed synthetic rows."""
    ensure_database_exists()
    reset_engine_cache()
    url = build_database_url(database_url)
    engine = create_engine(url, future=True)
    with Session(engine) as session:
        seed_demo_data(session)
        session.commit()
    engine.dispose()
    reset_engine_cache()
