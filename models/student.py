from __future__ import annotations

import sqlite3
from sqlite3 import IntegrityError
from typing import Any, Dict, List, Optional

from database.connection import get_connection

StudentRecord = Dict[str, Optional[Any]]


def _fetch_students(query: str, params: tuple = ()) -> List[StudentRecord]:
    """Run a query that returns student rows and convert them to dictionaries."""
    conn = get_connection()
    if conn is None:
        print("Database connection failed while fetching student records.")
        return []

    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching student records: {e}")
        return []
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
    """Insert a new student into the database.

    Returns True when the student is created successfully. Duplicate IDs are
    rejected before insertion, and the SQLite primary key constraint provides
    a second level of protection.
    """
    if not isinstance(student_id, int) or student_id <= 0:
        print("Student ID must be a positive number.")
        return False

    name = str(name).strip()
    if not name:
        print("Student name is required.")
        return False

    if student_id_exists(student_id):
        print(f"Student ID {student_id} already exists. Please choose a unique ID.")
        return False

    query = """
    INSERT INTO students (student_id, name, gender, semester, department, age, grade)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    conn = get_connection()
    if conn is None:
        print("Database connection failed while adding a student.")
        return False

    try:
        with conn:
            conn.execute(query, (student_id, name, gender, semester, department, age, grade))
        return True
    except IntegrityError:
        print(f"Student ID {student_id} already exists. Please choose a unique ID.")
        return False
    except Exception as e:
        print(f"Error adding student: {e}")
        return False
    finally:
        conn.close()


def student_id_exists(student_id: int) -> bool:
    """Return True when a student with the provided ID already exists."""
    query = "SELECT 1 FROM students WHERE student_id = ? LIMIT 1;"
    conn = get_connection()
    if conn is None:
        print("Database connection failed while checking student ID.")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(query, (student_id,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking student ID: {e}")
        return False
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
    """Update an existing student record.

    Only the provided values are changed, and all unspecified fields remain
    unchanged.
    """
    update_fields: List[str] = []
    params: List[Any] = []

    if name is not None:
        update_fields.append("name = ?")
        params.append(name.strip())
    if gender is not None:
        update_fields.append("gender = ?")
        params.append(gender.strip())
    if semester is not None:
        update_fields.append("semester = ?")
        params.append(semester)
    if department is not None:
        update_fields.append("department = ?")
        params.append(department.strip())
    if age is not None:
        update_fields.append("age = ?")
        params.append(age)
    if grade is not None:
        update_fields.append("grade = ?")
        params.append(grade.strip())

    if not update_fields:
        print("No values were provided to update.")
        return False

    query = f"UPDATE students SET {', '.join(update_fields)} WHERE student_id = ?;"
    params.append(student_id)

    conn = get_connection()
    if conn is None:
        print("Database connection failed while updating the student.")
        return False

    try:
        with conn:
            cursor = conn.execute(query, tuple(params))
            if cursor.rowcount == 0:
                print(f"Student with ID {student_id} does not exist.")
                return False
        return True
    except Exception as e:
        print(f"Error updating student: {e}")
        return False
    finally:
        conn.close()


def delete_student(student_id: int) -> bool:
    """Delete a single student record from the database."""
    query = "DELETE FROM students WHERE student_id = ?;"
    conn = get_connection()
    if conn is None:
        print("Database connection failed while deleting the student.")
        return False

    try:
        with conn:
            cursor = conn.execute(query, (student_id,))
            if cursor.rowcount == 0:
                print(f"Student with ID {student_id} does not exist.")
                return False
        return True
    except Exception as e:
        print(f"Error deleting student: {e}")
        return False
    finally:
        conn.close()
