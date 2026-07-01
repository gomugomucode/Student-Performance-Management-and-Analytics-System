from __future__ import annotations

from typing import Any, Dict, List, Sequence


def build_student_rows(students: Sequence[Dict[str, Any]]) -> List[List[str]]:
    """Convert student dictionaries into display rows for the CLI table view."""
    return [
        [
            str(student.get("student_id", "")),
            student.get("name", ""),
            student.get("gender", ""),
            str(student.get("semester", "")) if student.get("semester") is not None else "",
            student.get("department", ""),
            str(student.get("age", "")) if student.get("age") is not None else "",
            student.get("grade", ""),
        ]
        for student in students
    ]


def build_mark_rows(marks: Sequence[Dict[str, Any]]) -> List[List[str]]:
    """Convert mark dictionaries into display rows for the CLI table view."""
    return [
        [
            str(mark.get("mark_id", "")),
            mark.get("subject", ""),
            str(mark.get("marks", "")),
        ]
        for mark in marks
    ]
