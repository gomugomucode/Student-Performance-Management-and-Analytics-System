from models.marks import get_marks
from models.student import get_student


def student_exists(student_id: int) -> bool:
    """Return True if the student exists in the database."""
    return bool(get_student(student_id))


def calculate_student_average(student_id: int):
    """Calculate the average mark for a single student."""
    marks = get_marks(student_id)
    if not marks:
        return None

    total = sum(mark["marks"] for mark in marks)
    return total / len(marks)


def calculate_class_average():
    """Calculate the average mark for all students."""
    # SQLite-level aggregation could be more efficient, but the model is simple and explicit.
    import sqlite3
    from database.connection import get_connection

    query = "SELECT AVG(marks) FROM marks;"
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row and row[0] is not None:
            return float(row[0])
        return None
    except sqlite3.Error:
        return None
    finally:
        conn.close()
