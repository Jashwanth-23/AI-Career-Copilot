"""
Database Connection & Session Management Module

This module sets up the SQLAlchemy 2.0 engine, database session factory (SessionLocal),
Declarative Base for ORM models, and the `get_db` dependency generator for FastAPI routes.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings

# ------------------------------------------------------------------
# SQLAlchemy Engine Creation
# ------------------------------------------------------------------
# Configure engine with pool pre-ping, connection recycling for Neon PostgreSQL,
# and TCP keepalives to prevent idle SSL socket timeouts.
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
    "pool_size": 10,
    "max_overflow": 20,
}

# Add database driver-specific arguments
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
elif settings.DATABASE_URL.startswith("postgres"):
    engine_kwargs["connect_args"] = {
        "connect_timeout": 5,
        "options": "-c statement_timeout=10000",
        "keepalives": 1,
        "keepalives_idle": 15,
        "keepalives_interval": 5,
        "keepalives_count": 3,
    }

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# ------------------------------------------------------------------
# Session Factory
# ------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ------------------------------------------------------------------
# Declarative Base (SQLAlchemy 2.0 Style)
# ------------------------------------------------------------------
class Base(DeclarativeBase):
    """
    Base class for all database ORM models.
    """
    pass


# ------------------------------------------------------------------
# Database Session Dependency Generator
# ------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
