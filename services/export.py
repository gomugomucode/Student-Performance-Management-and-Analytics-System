import pandas as pd
from database.connection import get_connection, release_connection
from services.analytics import (
    complete_class_report,
    detailed_student_report,
    individual_student_report,
    subject_wise_report,
)
from services.validation import ExportError
import config

EXPORT_DIR = config.REPORTS_DIR
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _write_dataframe_csv(filename: str, df: pd.DataFrame) -> str:
    output_path = EXPORT_DIR / filename
    try:
        df.to_csv(output_path, index=False, encoding="utf-8")
    except Exception as error:
        raise ExportError(f"Failed to write export file {output_path}: {error}") from error
    return str(output_path.resolve())


def export_students_to_csv() -> str:
    query = "SELECT student_id, name, gender, semester, department, age, grade FROM students ORDER BY student_id;"
    conn = get_connection()
    if conn is None:
        raise ExportError("Unable to connect to the database for export.")

    try:
        df = pd.read_sql_query(query, conn)
        return _write_dataframe_csv("students_export.csv", df)
    finally:
        release_connection(conn)


def export_marks_to_csv() -> str:
    query = "SELECT mark_id, student_id, subject, marks FROM marks ORDER BY student_id, mark_id;"
    conn = get_connection()
    if conn is None:
        raise ExportError("Unable to connect to the database for export.")

    try:
        df = pd.read_sql_query(query, conn)
        return _write_dataframe_csv("marks_export.csv", df)
    finally:
        release_connection(conn)


def export_individual_student_report_to_csv(student_id: int) -> str:
    df = individual_student_report(student_id)
    if df.empty:
        raise ExportError(f"No report available for student ID {student_id}.")
    return _write_dataframe_csv(f"student_{student_id}_report.csv", df)


def export_complete_class_report_to_csv() -> str:
    df = complete_class_report()
    if df.empty:
        raise ExportError("No class report available.")
    return _write_dataframe_csv("class_report.csv", df)


def export_subject_report_to_csv() -> str:
    df = subject_wise_report()
    if df.empty:
        raise ExportError("No subject report available.")
    return _write_dataframe_csv("subject_report.csv", df)


def export_analytics_report_to_csv() -> str:
    df = detailed_student_report()
    if df.empty:
        raise ExportError("No analytics report available.")
    return _write_dataframe_csv("analytics_report.csv", df)
