from __future__ import annotations

import logging
from typing import Any

import psycopg

from services.validation import (
    DatabaseConnectionError,
    DuplicateIDError,
    MissingRecordError,
    ValidationError,
)

logger = logging.getLogger("student_system")


def get_user_message(error: Exception) -> str:
    """Return a friendly, non-sensitive message for end users."""
    if isinstance(error, ValidationError):
        if isinstance(error, DuplicateIDError):
            return "That value already exists. Please choose a different one."
        if isinstance(error, MissingRecordError):
            return "The requested record could not be found."
        return str(error)

    if isinstance(error, DatabaseConnectionError):
        return "The service is temporarily unavailable. Please try again shortly."

    if isinstance(error, psycopg.Error):
        return "The service is temporarily unavailable. Please try again shortly."

    if isinstance(error, (ConnectionError, TimeoutError)):
        return "The service is temporarily unavailable. Please try again shortly."

    return "An unexpected error occurred. Please try again."


def log_exception(error: Exception, context: str = "application") -> None:
    """Log a detailed internal exception without exposing it to users."""
    logger.exception("%s failed", context)


def normalize_exception(error: Exception, context: str = "application") -> Exception:
    """Normalize known database and validation issues while letting unexpected exceptions pass through."""
    if isinstance(error, ValidationError):
        return error

    if isinstance(error, DatabaseConnectionError):
        return error

    if isinstance(error, psycopg.Error):
        log_exception(error, context)
        return DatabaseConnectionError("A database error occurred.")

    if isinstance(error, (ConnectionError, TimeoutError)):
        log_exception(error, context)
        return DatabaseConnectionError("A database connection error occurred.")

    log_exception(error, context)
    raise error
