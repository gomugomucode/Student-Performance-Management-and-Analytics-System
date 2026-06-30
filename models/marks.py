from __future__ import annotations

import sqlite3
from sqlite3 import IntegrityError
from typing import Any, Dict, List, Optional

from database.connection import get_connection
from models.student import student_id_exists

MarkRecord = Dict[str, Any]


def _fetch_rows(query: str, params: tuple = ()) -> List[MarkRecord]:
    """Execute a query and return result rows as dictionaries."""
    conn = get_connection()
    if conn is None:
        print("Database connection failed while retrieving marks.")
        return []

    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error retrieving marks: {e}")
        return []
    finally:
        conn.close()


def _normalize_subject(subject: Any) -> Optional[str]:
    """Clean and validate subject text."""
    if subject is None:
        return None
    normalized = str(subject).strip()
    return normalized if normalized else None


def _normalize_marks(value: Any) -> Optional[int]:
    """Convert marks input to an integer in the range 0-100."""
    if isinstance(value, bool):
        return None
    try:
        marks_value = int(str(value).strip())
    except (ValueError, TypeError):
        return None

    if 0 <= marks_value <= 100:
        return marks_value

    return None


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
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking duplicate subject: {e}")
        return False
    finally:
        conn.close()


def add_marks(student_id: int, subject: Any, marks: Any) -> bool:
    """Add a marks record for a student.

    Validates student existence, subject uniqueness, and marks range.
    """
    if not isinstance(student_id, int) or student_id <= 0:
        print("Student ID must be a positive number.")
        return False

    if not student_id_exists(student_id):
        print(f"Student with ID {student_id} does not exist.")
        return False

    subject_text = _normalize_subject(subject)
    if subject_text is None:
        print("Subject is required.")
        return False

    marks_value = _normalize_marks(marks)
    if marks_value is None:
        print("Marks must be an integer between 0 and 100.")
        return False

    if _subject_exists(student_id, subject_text):
        print(f"Student {student_id} already has marks for subject '{subject_text}'.")
        return False

    query = "INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?);"
    conn = get_connection()
    if conn is None:
        print("Database connection failed while adding marks.")
        return False

    try:
        with conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute(query, (student_id, subject_text, marks_value))
        return True
    except IntegrityError:
        print(f"Marks for subject '{subject_text}' already exist for student {student_id}.")
        return False
    except Exception as e:
        print(f"Error adding marks: {e}")
        return False
    finally:
        conn.close()


def get_marks(student_id: int) -> List[MarkRecord]:
    """Retrieve marks for a specific student."""
    if not isinstance(student_id, int) or student_id <= 0:
        print("Student ID must be a positive number.")
        return []

    query = "SELECT mark_id, student_id, subject, marks FROM marks WHERE student_id = ? ORDER BY subject;"
    return _fetch_rows(query, (student_id,))


def get_mark(mark_id: int) -> Optional[MarkRecord]:
    """Return a single marks record by its record ID."""
    if not isinstance(mark_id, int) or mark_id <= 0:
        return None

    query = "SELECT mark_id, student_id, subject, marks FROM marks WHERE mark_id = ?;"
    rows = _fetch_rows(query, (mark_id,))
    return rows[0] if rows else None


def update_marks(mark_id: int, subject: Any = None, marks: Any = None) -> bool:
    """Update a marks record while validating subject and marks."""
    if subject is None and marks is None:
        print("No values were provided to update.")
        return False

    record = get_mark(mark_id)
    if not record:
        print(f"No marks record found with ID {mark_id}.")
        return False

    update_fields: List[str] = []
    params: List[Any] = []

    if subject is not None:
        subject_text = _normalize_subject(subject)
        if subject_text is None:
            print("Subject cannot be empty.")
            return False

        if _subject_exists(record["student_id"], subject_text, exclude_mark_id=mark_id):
            print(f"Student {record['student_id']} already has marks for subject '{subject_text}'.")
            return False

        update_fields.append("subject = ?")
        params.append(subject_text)

    if marks is not None:
        marks_value = _normalize_marks(marks)
        if marks_value is None:
            print("Marks must be an integer between 0 and 100.")
            return False

        update_fields.append("marks = ?")
        params.append(marks_value)

    query = f"UPDATE marks SET {', '.join(update_fields)} WHERE mark_id = ?;"
    params.append(mark_id)

    conn = get_connection()
    if conn is None:
        print("Database connection failed while updating marks.")
        return False

    try:
        with conn:
            cursor = conn.execute(query, tuple(params))
            if cursor.rowcount == 0:
                print(f"No marks record found with ID {mark_id}.")
                return False
        return True
    except IntegrityError:
        print("A duplicate subject entry exists for this student.")
        return False
    except Exception as e:
        print(f"Error updating marks: {e}")
        return False
    finally:
        conn.close()


def delete_marks(mark_id: int) -> bool:
    """Delete a marks record from the database."""
    if not isinstance(mark_id, int) or mark_id <= 0:
        print("Mark record ID must be a positive number.")
        return False

    query = "DELETE FROM marks WHERE mark_id = ?;"
    conn = get_connection()
    if conn is None:
        print("Database connection failed while deleting marks.")
        return False

    try:
        with conn:
            cursor = conn.execute(query, (mark_id,))
            if cursor.rowcount == 0:
                print(f"No record found with mark_id: {mark_id}")
                return False
        return True
    except Exception as e:
        print(f"Error deleting marks: {e}")
        return False
    finally:
        conn.close()
