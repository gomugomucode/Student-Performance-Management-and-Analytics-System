from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

import psycopg

from services.error_handling import log_exception
from services.logging_config import configure_logging
from services.validation import DatabaseConnectionError

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = BASE_DIR / ".env"


class ConnectionPool:
    """A lightweight connection pool for PostgreSQL connections."""

    def __init__(self, max_connections: int = 5) -> None:
        self._max_connections = max_connections
        self._available_connections: list[Any] = []
        self._lock = threading.Lock()

    def _build_connection(self) -> Any:
        connection = psycopg.connect(
            conninfo=get_connection_string(),
            autocommit=False,
            connect_timeout=10,
        )
        connection.execute("SET search_path TO public;")
        return connection

    def get_connection(self) -> Any:
        with self._lock:
            if self._available_connections:
                return self._available_connections.pop()

        return self._build_connection()

    def release(self, connection: Optional[Any]) -> None:
        if connection is None:
            return

        if getattr(connection, "closed", False):
            return

        try:
            connection.rollback()
        except Exception:
            pass

        with self._lock:
            if len(self._available_connections) < self._max_connections:
                self._available_connections.append(connection)
                return

        connection.close()


_pool = ConnectionPool()


def _load_env_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")

    return values


def get_database_config() -> Dict[str, Any]:
    """Load PostgreSQL configuration from environment variables or a .env file."""
    env_values = _load_env_file(DOTENV_PATH)
    merged = {**os.environ, **env_values}

    return {
        "host": merged.get("DB_HOST", "localhost"),
        "port": int(merged.get("DB_PORT", "5432")),
        "dbname": merged.get("DB_NAME", "student_performance"),
        "user": merged.get("DB_USER", "postgres"),
        "password": merged.get("DB_PASSWORD", "postgres"),
    }


def get_connection_string() -> str:
    """Build a PostgreSQL connection string from configuration values."""
    config = get_database_config()
    return (
        f"postgresql://{config['user']}:{config['password']}@"
        f"{config['host']}:{config['port']}/{config['dbname']}"
    )


def get_connection() -> Optional[Any]:
    """Return a pooled PostgreSQL connection or None if the connection cannot be created."""
    configure_logging()
    try:
        return _pool.get_connection()
    except Exception as error:
        log_exception(error, "database connection")
        return None


def release_connection(connection: Optional[Any]) -> None:
    """Return a connection to the pool or close it if the pool is full."""
    _pool.release(connection)


@contextmanager
def transaction() -> Iterator[Any]:
    """Provide a transaction context for database operations."""
    connection = get_connection()
    if connection is None:
        raise DatabaseConnectionError("Unable to connect to the PostgreSQL database.")

    try:
        with connection:
            yield connection
    except Exception as error:
        try:
            connection.rollback()
        except Exception as rollback_error:
            log_exception(rollback_error, "transaction rollback")
        raise error
    finally:
        release_connection(connection)
