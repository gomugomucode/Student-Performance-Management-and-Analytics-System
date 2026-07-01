from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

from dotenv import load_dotenv


import psycopg

from services.error_handling import log_exception
from services.logging_config import configure_logging
from services.validation import DatabaseConnectionError

# BASE_DIR = Path(__file__).resolve().parent.parent
# DOTENV_PATH = BASE_DIR / ".env"

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


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



def get_database_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "dbname": os.getenv("DB_NAME", "student_performance"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD"),
    }

print(get_database_config())

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
        print(f"\nDATABASE CONNECTION ERROR:\n{error}\n")
        log_exception(error, "database connection")
        return None


def release_connection(connection: Optional[Any]) -> None:
    """Return a connection to the pool or close it if the pool is full."""
    _pool.release(connection)


def fetch_all_rows(query: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
    """Execute a query and return the result rows as dictionaries."""
    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Unable to connect to the database.")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            columns = [description[0] for description in cursor.description or []]
            rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        release_connection(conn)


def execute_statement(query: str, params: Sequence[Any] = ()) -> int:
    """Execute a statement and return the affected row count."""
    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Unable to connect to the database.")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.rowcount
    finally:
        release_connection(conn)


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
