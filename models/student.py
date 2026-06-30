from __future__ import annotations

import sqlite3
from sqlite3 import IntegrityError
from typing import Any, Dict, List, Optional

from database.connection import get_connection
from services.validation import (
    DatabaseConnectionError,
    DuplicateIDError,
    MissingRecordError,
    ValidationError,
    validate_age,
    validate_department,
    validate_gender,
    validate_name,
    validate_optional_text,
    validate_semester,
    validate_student_id,
    ensure_unique_student_id,
)

StudentRecord = Dict[str, Optional[Any]]


def _fetch_students(query: str, params: tuple = ()) -> List[StudentRecord]:
    """Run a query that returns student rows and convert them to dictionaries."""
    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Unable to connect to the database.")

    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def add_student(
    student_id: int,
    name: str,
    age: Optional[int] = None,
    grade: Optional[str] = None,
    gender: Optional[str] = None,
    semester: Optional[int] = None,
    department: Optional[str] = None,
) -> bool:
    """Insert a new student into the database."""
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
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while adding a student.")

    try:
        with conn:
            conn.execute(query, (student_id, name, gender, semester, department, age, grade))
        return True
    except IntegrityError as error:
        raise DuplicateIDError(f"Student ID {student_id} already exists.") from error
    finally:
        conn.close()


def student_id_exists(student_id: int) -> bool:
    """Return True when a student with the provided ID already exists."""
    student_id = validate_student_id(student_id)
    query = "SELECT 1 FROM students WHERE student_id = ? LIMIT 1;"

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while checking student ID.")

    try:
        cursor = conn.cursor()
        cursor.execute(query, (student_id,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def get_all_students() -> List[StudentRecord]:
    """Return all student records from the database."""
    query = "SELECT student_id, name, gender, semester, department, age, grade FROM students ORDER BY student_id;"
    return _fetch_students(query)


def search_students(search_term: str) -> List[StudentRecord]:
    """Search student records by name fragment or exact student ID."""
    query = """
    SELECT student_id, name, gender, semester, department, age, grade
    FROM students
    WHERE name LIKE ? OR student_id = ?
    ORDER BY student_id;
    """
    student_id = int(search_term) if search_term.isdigit() else -1
    return _fetch_students(query, (f"%{search_term}%", student_id))


def get_student(student_id: int) -> StudentRecord:
    """Retrieve a single student record by student_id."""
    student_id = validate_student_id(student_id)
    query = """
    SELECT student_id, name, gender, semester, department, age, grade
    FROM students
    WHERE student_id = ?;
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
        update_fields.append("name = ?")
        params.append(validate_name(name, "Student name"))
    if gender is not None:
        update_fields.append("gender = ?")
        params.append(validate_gender(gender))
    if semester is not None:
        update_fields.append("semester = ?")
        params.append(validate_semester(semester))
    if department is not None:
        update_fields.append("department = ?")
        params.append(validate_department(department))
    if age is not None:
        update_fields.append("age = ?")
        params.append(validate_age(age))
    if grade is not None:
        update_fields.append("grade = ?")
        params.append(validate_optional_text(grade, "Grade", max_length=20))

    if not update_fields:
        raise ValidationError("No values were provided to update.")

    query = f"UPDATE students SET {', '.join(update_fields)} WHERE student_id = ?;"
    params.append(student_id)

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while updating the student.")

    try:
        with conn:
            cursor = conn.execute(query, tuple(params))
            if cursor.rowcount == 0:
                raise MissingRecordError(f"Student with ID {student_id} does not exist.")
        return True
    finally:
        conn.close()


def delete_student(student_id: int) -> bool:
    """Delete a single student record from the database."""
    student_id = validate_student_id(student_id)
    query = "DELETE FROM students WHERE student_id = ?;"

    conn = get_connection()
    if conn is None:
        raise DatabaseConnectionError("Database connection failed while deleting the student.")

    try:
        with conn:
            cursor = conn.execute(query, (student_id,))
            if cursor.rowcount == 0:
                raise MissingRecordError(f"Student with ID {student_id} does not exist.")
        return True
    finally:
        conn.close()
