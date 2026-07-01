from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from psycopg.errors import IntegrityError

from database.connection import execute_statement, fetch_all_rows, get_connection, release_connection
from services.error_handling import log_exception, normalize_exception
from services.logging_config import configure_logging
from services.validation import (
    DatabaseConnectionError,
    DuplicateIDError,
    MissingRecordError,
    ValidationError,
    ensure_unique_student_id,
    validate_age,
    validate_department,
    validate_gender,
    validate_name,
    validate_optional_text,
    validate_semester,
    validate_student_id,
)

StudentRecord = Dict[str, Optional[Any]]


def _fetch_students(query: str, params: Tuple[Any, ...] = ()) -> List[StudentRecord]:
    """Execute a query and return student rows as dictionaries."""
    configure_logging()
    return fetch_all_rows(query, params)


def add_student(
    student_id: int,
    name: str,
    age: Optional[int] = None,
    grade: Optional[str] = None,
    gender: Optional[str] = None,
    semester: Optional[int] = None,
    department: Optional[str] = None,
) -> bool:
    """Insert a new student record into the database."""
    student_id = validate_student_id(student_id)
    name = validate_name(name, "Student name")
    age = validate_age(age)
    gender = validate_gender(gender)
    semester = validate_semester(semester)
    department = validate_department(department)
    grade = validate_optional_text(grade, "Grade", max_length=20)

    ensure_unique_student_id(student_id, student_id_exists)

    query = """
    INSERT INTO students (student_id, name, gender, semester, department, age, grade)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while adding a student.")

    try:
        logger = logging.getLogger("student_system")
        logger.info("Creating student record for student_id=%s", student_id)
        with conn:
            conn.execute(query, (student_id, name, gender, semester, department, age, grade))
        return True
    except IntegrityError as error:
        log_exception(error, "insert student")
        raise DuplicateIDError(f"Student ID {student_id} already exists.") from error
    except Exception as error:
        normalized_error = normalize_exception(error, "insert student")
        log_exception(normalized_error, "insert student")
        raise normalized_error from error
    finally:
        release_connection(conn)


def student_id_exists(student_id: int) -> bool:
    """Return True when a student with the provided ID already exists."""
    student_id = validate_student_id(student_id)
    query = "SELECT 1 FROM students WHERE student_id = %s LIMIT 1;"

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while checking student ID.")

    try:
        logger = logging.getLogger("student_system")
        logger.info("Checking student existence for student_id=%s", student_id)
        with conn.cursor() as cursor:
            cursor.execute(query, (student_id,))
            return cursor.fetchone() is not None
    except Exception as error:
        normalized_error = normalize_exception(error, "check student id")
        log_exception(normalized_error, "check student id")
        raise normalized_error from error
    finally:
        release_connection(conn)


def get_all_students() -> List[StudentRecord]:
    """Return all student records from the database."""
    query = "SELECT student_id, name, gender, semester, department, age, grade FROM students ORDER BY student_id;"
    return _fetch_students(query)


def search_students(search_term: str) -> List[StudentRecord]:
    """Search student records by name fragment using PostgreSQL ILIKE."""
    if not search_term or not search_term.strip():
        return []

    normalized_term = search_term.strip()
    query = """
    SELECT student_id, name, gender, semester, department, age, grade
    FROM students
    WHERE name ILIKE %s
    ORDER BY student_id;
    """
    return _fetch_students(query, (f"%{normalized_term}%",))


def get_student(student_id: int) -> StudentRecord:
    """Return a single student record by student_id."""
    student_id = validate_student_id(student_id)
    query = """
    SELECT student_id, name, gender, semester, department, age, grade
    FROM students
    WHERE student_id = %s;
    """
    students = _fetch_students(query, (student_id,))
    return students[0] if students else {}


def update_student(
    student_id: int,
    name: Optional[str] = None,
    gender: Optional[str] = None,
    semester: Optional[int] = None,
    department: Optional[str] = None,
    age: Optional[int] = None,
    grade: Optional[str] = None,
) -> bool:
    """Update an existing student record."""
    student_id = validate_student_id(student_id)
    update_fields: List[str] = []
    params: List[Any] = []

    if name is not None:
        update_fields.append("name = %s")
        params.append(validate_name(name, "Student name"))
    if gender is not None:
        update_fields.append("gender = %s")
        params.append(validate_gender(gender))
    if semester is not None:
        update_fields.append("semester = %s")
        params.append(validate_semester(semester))
    if department is not None:
        update_fields.append("department = %s")
        params.append(validate_department(department))
    if age is not None:
        update_fields.append("age = %s")
        params.append(validate_age(age))
    if grade is not None:
        update_fields.append("grade = %s")
        params.append(validate_optional_text(grade, "Grade", max_length=20))

    if not update_fields:
        raise ValidationError("No values were provided to update.")

    query = f"UPDATE students SET {', '.join(update_fields)} WHERE student_id = %s;"
    params.append(student_id)

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while updating the student.")

    try:
        logger = logging.getLogger("student_system")
        logger.info("Updating student record for student_id=%s", student_id)
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(query, tuple(params))
                if cursor.rowcount == 0:
                    raise MissingRecordError(f"Student with ID {student_id} does not exist.")
        return True
    except Exception as error:
        normalized_error = normalize_exception(error, "update student")
        log_exception(normalized_error, "update student")
        raise normalized_error from error
    finally:
        release_connection(conn)


def delete_student(student_id: int) -> bool:
    """Delete a single student record from the database."""
    student_id = validate_student_id(student_id)
    query = "DELETE FROM students WHERE student_id = %s;"

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while deleting the student.")

    try:
        logger = logging.getLogger("student_system")
        logger.info("Deleting student record for student_id=%s", student_id)
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (student_id,))
                if cursor.rowcount == 0:
                    raise MissingRecordError(f"Student with ID {student_id} does not exist.")
        return True
    except Exception as error:
        normalized_error = normalize_exception(error, "delete student")
        log_exception(normalized_error, "delete student")
        raise normalized_error from error
    finally:
        release_connection(conn)
