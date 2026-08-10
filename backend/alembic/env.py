"""
Alembic Environment Configuration

This module configures the migration environment for Alembic.
It dynamically loads DATABASE_URL from `app.core.config.settings`
and binds `Base.metadata` from `app.database.database` for autogenerate support.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ------------------------------------------------------------------
# Add Backend Root Path to sys.path
# ------------------------------------------------------------------
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

# Import application settings and Base metadata
from app.core.config import settings
from app.database.database import Base

# Import all models so Alembic autogenerate can detect defined tables
import app.models.user  # noqa: F401
import app.models.resume  # noqa: F401

# Alembic Config object, providing access to values within alembic.ini
config = context.config

# Interpret the config file for Python logging if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate migration support
target_metadata = Base.metadata

# Dynamically override sqlalchemy.url from application settings
if settings.DATABASE_URL:
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine,
    skipping DBAPI connection creation.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates a SQLAlchemy Engine and associates a database connection
    with the Alembic migration context.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
