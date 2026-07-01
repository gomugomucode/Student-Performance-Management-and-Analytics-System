from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from psycopg.errors import IntegrityError

from database.connection import get_connection, release_connection, transaction
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

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description or []]
            rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        release_connection(conn)


def _subject_exists(student_id: int, subject: str, exclude_mark_id: Optional[int] = None) -> bool:
    """Return True if the student already has a marks entry for the given subject."""
    query = "SELECT 1 FROM marks WHERE student_id = %s AND LOWER(subject) = LOWER(%s)"
    params: List[Any] = [student_id, subject]

    if exclude_mark_id is not None:
        query += " AND mark_id != %s"
        params.append(exclude_mark_id)

    query += " LIMIT 1;"

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Unable to connect to the database.")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchone() is not None
    finally:
        release_connection(conn)


def _subject_exists_for_connection(conn: Any, student_id: int, subject: str, exclude_mark_id: Optional[int] = None) -> bool:
    """Check whether a marks entry already exists for the supplied connection."""
    query = "SELECT 1 FROM marks WHERE student_id = %s AND LOWER(subject) = LOWER(%s)"
    params: List[Any] = [student_id, subject]

    if exclude_mark_id is not None:
        query += " AND mark_id != %s"
        params.append(exclude_mark_id)

    query += " LIMIT 1;"

    with conn.cursor() as cursor:
        cursor.execute(query, tuple(params))
        return cursor.fetchone() is not None


def add_marks_batch(student_id: int, entries: List[Tuple[Any, Any]]) -> bool:
    """Insert multiple marks records for a student in a single PostgreSQL transaction."""
    student_id = validate_student_id(student_id)
    if not student_id_exists(student_id):
        raise MissingRecordError(f"Student with ID {student_id} does not exist.")

    if not entries:
        raise ValidationError("At least one subject is required.")

    validated_entries: List[Tuple[str, int]] = []
    seen_subjects = set()

    for subject, marks in entries:
        subject_text = validate_subject_name(subject)
        marks_value = validate_marks(marks)
        normalized_subject = subject_text.lower()
        if normalized_subject in seen_subjects:
            raise DuplicateIDError(f"Student {student_id} already has marks for subject '{subject_text}'.")
        seen_subjects.add(normalized_subject)
        validated_entries.append((subject_text, marks_value))

    try:
        with transaction() as conn:
            for subject_text, marks_value in validated_entries:
                if _subject_exists_for_connection(conn, student_id, subject_text):
                    raise DuplicateIDError(f"Student {student_id} already has marks for subject '{subject_text}'.")

                query = "INSERT INTO marks (student_id, subject, marks) VALUES (%s, %s, %s);"
                with conn.cursor() as cursor:
                    cursor.execute(query, (student_id, subject_text, marks_value))
        return True
    except IntegrityError as error:
        raise DuplicateIDError("A duplicate subject entry exists for this student.") from error


def add_marks(student_id: int, subject: Any, marks: Any) -> bool:
    """Add a marks record for a student."""
    return add_marks_batch(student_id, [(subject, marks)])


def get_marks(student_id: int) -> List[MarkRecord]:
    """Retrieve marks for a specific student."""
    student_id = validate_student_id(student_id)
    query = "SELECT mark_id, student_id, subject, marks FROM marks WHERE student_id = %s ORDER BY subject;"
    return _fetch_rows(query, (student_id,))


def get_mark(mark_id: int) -> Optional[MarkRecord]:
    """Return a single marks record by its record ID."""
    mark_id = validate_student_id(mark_id)
    query = "SELECT mark_id, student_id, subject, marks FROM marks WHERE mark_id = %s;"
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
        update_fields.append("subject = %s")
        params.append(subject_text)

    if marks is not None:
        marks_value = validate_marks(marks)
        update_fields.append("marks = %s")
        params.append(marks_value)

    query = f"UPDATE marks SET {', '.join(update_fields)} WHERE mark_id = %s;"
    params.append(mark_id)

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while updating marks.")

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(query, tuple(params))
                if cursor.rowcount == 0:
                    raise MissingRecordError(f"No marks record found with ID {mark_id}.")
        return True
    except IntegrityError as error:
        raise DuplicateIDError("A duplicate subject entry exists for this student.") from error
    finally:
        release_connection(conn)


def delete_marks(mark_id: int) -> bool:
    """Delete a marks record from the database."""
    mark_id = validate_student_id(mark_id)
    query = "DELETE FROM marks WHERE mark_id = %s;"

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while deleting marks.")

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (mark_id,))
                if cursor.rowcount == 0:
                    raise MissingRecordError(f"No record found with mark_id: {mark_id}")
        return True
    finally:
        release_connection(conn)
