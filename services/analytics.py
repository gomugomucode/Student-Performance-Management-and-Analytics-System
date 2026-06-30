from __future__ import annotations

import numpy as np
import pandas as pd
from database.connection import get_connection
from models.student import get_student
from typing import Optional

GRADE_BOUNDARIES = {
    "A": 90,
    "B": 75,
    "C": 60,
    "D": 50,
    "E": 40,
}


def _load_marks_dataframe() -> pd.DataFrame:
    """Load marks joined with student names from SQLite into a pandas DataFrame."""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    query = """
    SELECT
        m.mark_id,
        m.student_id,
        s.name AS student_name,
        m.subject,
        m.marks
    FROM marks m
    LEFT JOIN students s ON m.student_id = s.student_id
    """

    try:
        df = pd.read_sql_query(query, conn)
        if df.empty:
            return df
    
    # errors="coerce" forces invalid data (e.g., text or missing values) into NaN.
    # fillna(0) replaces those NaN values with 0..astype(int) ensures all column data becomes integers.

        df["marks"] = pd.to_numeric(df["marks"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        print(f"Error loading marks dataframe: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def _compute_grade(percentage: float) -> str:
    """Return a grade based on percentage thresholds."""
    if percentage >= GRADE_BOUNDARIES["A"]:
        return "A"
    if percentage >= GRADE_BOUNDARIES["B"]:
        return "B"
    if percentage >= GRADE_BOUNDARIES["C"]:
        return "C"
    if percentage >= GRADE_BOUNDARIES["D"]:
        return "D"
    if percentage >= GRADE_BOUNDARIES["E"]:
        return "E"
    return "F"


def _calculate_student_report() -> pd.DataFrame:
    """Build a summary report per student with totals, averages, percentages, grades, and pass/fail."""
    df = _load_marks_dataframe()
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby(["student_id", "student_name"], dropna=False)["marks"].agg(
        total_marks="sum",
        subject_count="count",
        average_marks="mean",
        min_marks="min",
    ).reset_index()

    # Percentage assumes each subject carries 100 marks.
    grouped["percentage"] = (grouped["total_marks"] / (grouped["subject_count"] * 100)) * 100
    grouped["grade"] = grouped["percentage"].apply(_compute_grade)
    grouped["pass_fail"] = np.where(
        (grouped["percentage"] >= 40) & (grouped["min_marks"] >= 35),
        "Pass",
        "Fail",
    )

    # Round numeric summaries for readability.
    grouped["average_marks"] = grouped["average_marks"].round(2)
    grouped["percentage"] = grouped["percentage"].round(2)
    return grouped.drop(columns=["min_marks"])


def individual_student_report(student_id: int) -> pd.DataFrame:
    """Return a single student's analytic summary."""
    report = _calculate_student_report()
    if report.empty:
        return report
    return report[report["student_id"] == student_id].reset_index(drop=True)


def complete_class_report() -> pd.DataFrame:
    """Return the class report for every student."""
    report = _calculate_student_report()
    return report.sort_values(by=["total_marks", "percentage"], ascending=[False, False]).reset_index(drop=True)


def subject_wise_report() -> pd.DataFrame:
    """Return a subject-wise summary of average and highest marks."""
    df = _load_marks_dataframe()
    if df.empty:
        return df

    subject_avg = df.groupby("subject")["marks"].mean().round(2).reset_index().rename(columns={"marks": "average_marks"})
    idx = df.groupby("subject")["marks"].idxmax()
    highest = df.loc[idx, ["subject", "student_id", "student_name", "marks"]].rename(columns={"marks": "highest_mark"}).reset_index(drop=True)
    return pd.merge(subject_avg, highest, on="subject")


def student_exists(student_id: int) -> bool:
    """Return True if the student exists in the database."""
    return bool(get_student(student_id))


def student_total_marks_report() -> pd.DataFrame:
    """Return total marks per student.

    Total marks are the sum of all subject marks for each student.
    """
    report = _calculate_student_report()
    return report[["student_id", "student_name", "total_marks"]] if not report.empty else report


def student_average_marks_report() -> pd.DataFrame:
    """Return average marks per student.

    Average marks are the mean mark across all subjects for each student.
    """
    report = _calculate_student_report()
    return report[["student_id", "student_name", "average_marks"]] if not report.empty else report


def student_percentage_report() -> pd.DataFrame:
    """Return percentage for each student.

    Percentage is computed from total marks over the maximum possible marks.
    """
    report = _calculate_student_report()
    return report[["student_id", "student_name", "percentage"]] if not report.empty else report


def student_grade_report() -> pd.DataFrame:
    """Return computed grade for each student."""
    report = _calculate_student_report()
    return report[["student_id", "student_name", "grade"]] if not report.empty else report


def student_pass_fail_report() -> pd.DataFrame:
    """Return pass/fail status for each student.

    A student passes when average percentage is at least 40 and every subject score is at least 35.
    """
    report = _calculate_student_report()
    return report[["student_id", "student_name", "pass_fail"]] if not report.empty else report


def class_average() -> Optional[float]:
    """Calculate the class average across all marks.

    Class average is the mean of all the marks entered in the class.
    """
    df = _load_marks_dataframe()
    if df.empty:
        return None
    return float(df["marks"].mean().round(2))


def highest_scorer() -> pd.DataFrame:
    """Return the student or students with the highest total marks."""
    report = _calculate_student_report()
    if report.empty:
        return report
    max_total = report["total_marks"].max()
    return report[report["total_marks"] == max_total][["student_id", "student_name", "total_marks", "percentage", "grade"]]


def lowest_scorer() -> pd.DataFrame:
    """Return the student or students with the lowest total marks."""
    report = _calculate_student_report()
    if report.empty:
        return report
    min_total = report["total_marks"].min()
    return report[report["total_marks"] == min_total][["student_id", "student_name", "total_marks", "percentage", "grade"]]


def top_students(limit: int = 5) -> pd.DataFrame:
    """Return the top N students by total marks."""
    report = _calculate_student_report()
    if report.empty:
        return report
    return report.sort_values(by=["total_marks", "percentage"], ascending=[False, False]).head(limit)


def subject_average_report() -> pd.DataFrame:
    """Return average marks per subject.

    Subject-wise average is the mean of marks for each subject across all students.
    """
    df = _load_marks_dataframe()
    if df.empty:
        return df
    subject_avg = df.groupby("subject")["marks"].mean().reset_index()
    subject_avg["average_marks"] = subject_avg["marks"].round(2)
    return subject_avg[["subject", "average_marks"]]


def subject_highest_marks_report() -> pd.DataFrame:
    """Return the highest mark achieved in each subject.

    This includes the student who achieved the highest mark for each subject.
    """
    df = _load_marks_dataframe()
    if df.empty:
        return df

    idx = df.groupby("subject")["marks"].idxmax()
    highest = df.loc[idx].reset_index(drop=True)
    return highest[["subject", "student_id", "student_name", "marks"]].rename(columns={"marks": "highest_mark"})


def pass_percentage() -> Optional[float]:
    """Return the pass percentage for the class.

    Pass percentage is the share of students whose report status is 'Pass'.
    """
    report = _calculate_student_report()
    if report.empty:
        return None
    passes = (report["pass_fail"] == "Pass").sum()
    percent = (passes / len(report)) * 100
    return float(round(percent, 2))


def detailed_student_report() -> pd.DataFrame:
    """Return a complete report for all students including computed metrics."""
    return _calculate_student_report()
