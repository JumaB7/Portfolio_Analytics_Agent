"""Create LocalDB AnalyticsDemo and load synthetic seed data.

Usage (from repo root, venv active):
    python -m scripts.init_demo_db
"""

from app.db.seed import DEMO_DATABASE_NAME, initialize_demo_database


def main() -> None:
    initialize_demo_database()
    print(f"Seeded synthetic demo database: {DEMO_DATABASE_NAME}")
    print("Label: SYNTHETIC DEMO DATA — fictional e-commerce store for portfolio demos")


if __name__ == "__main__":
    main()
