from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


def build_database_url(database_url: str | None) -> str:
    """Return a SQLAlchemy URL. Prefer DATABASE_URL; else LocalDB AnalyticsDemo."""
    if database_url:
        return database_url

    odbc = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=(localdb)\\MSSQLLocalDB;"
        "DATABASE=AnalyticsDemo;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc)}"


def build_master_url() -> str:
    """LocalDB connection to master — used to CREATE DATABASE."""
    odbc = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=(localdb)\\MSSQLLocalDB;"
        "DATABASE=master;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc)}"


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        build_database_url(settings.database_url),
        pool_pre_ping=True,
        future=True,
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)


def reset_engine_cache() -> None:
    """Clear cached engine/session factory after DB recreate or settings change."""
    get_session_factory.cache_clear()
    get_engine.cache_clear()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Read/write session (seed/admin). Commits on success."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def read_session_scope() -> Iterator[Session]:
    """Read-only session for analytics tools. Never commits."""
    session = get_session_factory()()
    try:
        yield session
        session.rollback()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
