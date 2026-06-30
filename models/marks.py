from __future__ import annotations

import sqlite3
from sqlite3 import IntegrityError
from typing import Any, Dict, List, Optional

from database.connection import get_connection
from models.student import student_id_exists
from services.validation import (
    DatabaseConnectionError,
    DuplicateIDError,
    MissingRecordError,
    ValidationError,
    validate_marks,
    validate_student_id,
    validate_subject_name,
)

MarkRecord = Dict[str, Any]


def _fetch_rows(query: str, params: tuple = ()) -> List[MarkRecord]:
    """Execute a query and return result rows as dictionaries."""
    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Unable to connect to the database.")

    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def _subject_exists(student_id: int, subject: str, exclude_mark_id: Optional[int] = None) -> bool:
    """Return True if the student already has a marks entry for the given subject."""
    query = "SELECT 1 FROM marks WHERE student_id = ? AND LOWER(subject) = LOWER(?)"
    params: List[Any] = [student_id, subject]

    if exclude_mark_id is not None:
        query += " AND mark_id != ?"
        params.append(exclude_mark_id)

    query += " LIMIT 1;"

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Unable to connect to the database.")

    try:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def add_marks(student_id: int, subject: Any, marks: Any) -> bool:
    """Add a marks record for a student."""
    student_id = validate_student_id(student_id)
    subject_text = validate_subject_name(subject)
    marks_value = validate_marks(marks)

    if not student_id_exists(student_id):
        raise MissingRecordError(f"Student with ID {student_id} does not exist.")

    if _subject_exists(student_id, subject_text):
        raise DuplicateIDError(f"Student {student_id} already has marks for subject '{subject_text}'.")

    query = "INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?);"
    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while adding marks.")

    try:
        with conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute(query, (student_id, subject_text, marks_value))
        return True
    except IntegrityError as error:
        raise DuplicateIDError(f"Marks for subject '{subject_text}' already exist for student {student_id}.") from error
    finally:
        conn.close()


def get_marks(student_id: int) -> List[MarkRecord]:
    """Retrieve marks for a specific student."""
    student_id = validate_student_id(student_id)
    query = "SELECT mark_id, student_id, subject, marks FROM marks WHERE student_id = ? ORDER BY subject;"
    return _fetch_rows(query, (student_id,))


def get_mark(mark_id: int) -> Optional[MarkRecord]:
    """Return a single marks record by its record ID."""
    mark_id = validate_student_id(mark_id)
    query = "SELECT mark_id, student_id, subject, marks FROM marks WHERE mark_id = ?;"
    rows = _fetch_rows(query, (mark_id,))
    return rows[0] if rows else None


def update_marks(mark_id: int, subject: Any = None, marks: Any = None) -> bool:
    """Update a marks record while validating subject and marks."""
    mark_id = validate_student_id(mark_id)
    if subject is None and marks is None:
        raise ValidationError("No values were provided to update.")

    record = get_mark(mark_id)
    if not record:
        raise MissingRecordError(f"No marks record found with ID {mark_id}.")

    update_fields: List[str] = []
    params: List[Any] = []

    if subject is not None:
        subject_text = validate_subject_name(subject)
        if _subject_exists(record["student_id"], subject_text, exclude_mark_id=mark_id):
            raise DuplicateIDError(f"Student {record['student_id']} already has marks for subject '{subject_text}'.")
        update_fields.append("subject = ?")
        params.append(subject_text)

    if marks is not None:
        marks_value = validate_marks(marks)
        update_fields.append("marks = ?")
        params.append(marks_value)

    query = f"UPDATE marks SET {', '.join(update_fields)} WHERE mark_id = ?;"
    params.append(mark_id)

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while updating marks.")

    try:
        with conn:
            cursor = conn.execute(query, tuple(params))
            if cursor.rowcount == 0:
                raise MissingRecordError(f"No marks record found with ID {mark_id}.")
        return True
    except IntegrityError as error:
        raise DuplicateIDError("A duplicate subject entry exists for this student.") from error
    finally:
        conn.close()


def delete_marks(mark_id: int) -> bool:
    """Delete a marks record from the database."""
    mark_id = validate_student_id(mark_id)
    query = "DELETE FROM marks WHERE mark_id = ?;"

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while deleting marks.")

    try:
        with conn:
            cursor = conn.execute(query, (mark_id,))
            if cursor.rowcount == 0:
                raise MissingRecordError(f"No record found with mark_id: {mark_id}")
        return True
    finally:
        conn.close()
