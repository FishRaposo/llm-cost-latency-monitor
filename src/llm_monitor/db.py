"""Database availability probe and store selection.

Implements the migrated-service ``db_available`` pattern with a sync
``DatabaseManager``: on startup we probe the configured database; if reachable,
telemetry persists to PostgreSQL via ``DatabaseTelemetryStore`` and survives
restarts. If the database is unavailable — or its driver is not installed, which
is the offline-first default for tests and the demo — we transparently fall back
to ``InMemoryTelemetryStore`` so the service still runs with NO database.

The ``DatabaseManager`` (and thus the DB driver import) is created lazily inside
``check_db`` so merely importing this module never requires a Postgres driver.
"""

from typing import Optional

from loguru import logger
from sqlalchemy import text

from .config import AppConfig
from .storage import InMemoryTelemetryStore
from .storage_db import DatabaseTelemetryStore

config = AppConfig()

db_manager = None  # lazily constructed in check_db()
db_available: bool = False


def _get_manager():
    """Lazily build the shared DatabaseManager (imports the DB driver)."""
    global db_manager
    if db_manager is None:
        from shared_core.database import DatabaseManager

        db_manager = DatabaseManager(
            config.DATABASE_URL,
            pool_size=config.DB_POOL_SIZE,
            max_overflow=config.DB_MAX_OVERFLOW,
            pool_timeout=config.DB_POOL_TIMEOUT,
        )
    return db_manager


def check_db() -> bool:
    """Probe database connectivity and cache the result in ``db_available``.

    Returns ``False`` (and logs a warning) if the driver is missing or the
    database is unreachable, so callers fall back to the in-memory store.
    """
    global db_available
    try:
        manager = _get_manager()
        with manager.SessionLocal() as session:
            session.execute(text("SELECT 1"))
        manager.create_tables()
        db_available = True
        logger.info("Database connected — telemetry will persist to PostgreSQL.")
    except Exception as exc:
        db_available = False
        logger.warning(
            "Database unavailable — falling back to in-memory telemetry store: {}",
            exc,
        )
    return db_available


def build_store(in_memory_fallback: Optional[InMemoryTelemetryStore] = None):
    """Return the active telemetry store based on the last probe result.

    When the DB is available, returns a ``DatabaseTelemetryStore`` bound to the
    shared ``DatabaseManager`` session factory. Otherwise returns the provided
    in-memory fallback (or a fresh one).
    """
    if db_available and db_manager is not None:
        return DatabaseTelemetryStore(db_manager.get_session)
    return in_memory_fallback or InMemoryTelemetryStore()
