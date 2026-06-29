import csv
from pathlib import Path
from typing import List, Dict

from models.marks import get_marks
from models.student import get_student
from database.connection import get_connection

EXPORT_DIR = Path("reports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _write_csv(filename: str, headers: List[str], rows: List[Dict[str, object]]) -> str:
    output_path = EXPORT_DIR / filename
    with output_path.open(mode="w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return str(output_path.resolve())


def export_students_to_csv() -> str:
    query = "SELECT student_id, name, gender, semester, department, age, grade FROM students ORDER BY student_id;"
    conn = get_connection()
    if conn is None:
        raise RuntimeError("Unable to connect to the database.")

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        students = [
            {
                "student_id": row[0],
                "name": row[1],
                "gender": row[2] or "",
                "semester": row[3] if row[3] is not None else "",
                "department": row[4] or "",
                "age": row[5] if row[5] is not None else "",
                "grade": row[6] or "",
            }
            for row in rows
        ]
        return _write_csv("students_export.csv", ["student_id", "name", "gender", "semester", "department", "age", "grade"], students)
    finally:
        conn.close()


def export_marks_to_csv() -> str:
    query = "SELECT mark_id, student_id, subject, marks FROM marks ORDER BY student_id, mark_id;"
    conn = get_connection()
    if conn is None:
        raise RuntimeError("Unable to connect to the database.")

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        marks = [
            {
                "mark_id": row[0],
                "student_id": row[1],
                "subject": row[2],
                "marks": row[3],
            }
            for row in rows
        ]
        return _write_csv("marks_export.csv", ["mark_id", "student_id", "subject", "marks"], marks)
    finally:
        conn.close()
