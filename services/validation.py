from __future__ import annotations

import re
from typing import Any, Callable, Optional, Set


class ValidationError(ValueError):
    """Base exception for validation failures."""


class DuplicateIDError(ValidationError):
    """Raised when a unique identifier is already used."""


class MissingRecordError(ValidationError):
    """Raised when an expected database record is missing."""


class DatabaseConnectionError(Exception):
    """Raised when the PostgreSQL database cannot be opened."""


class ExportError(Exception):
    """Raised when a report cannot be written to disk."""


GENDER_CHOICES: Set[str] = {
    "Male",
    "Female",
    "Other",
    "Non-binary",
    "Prefer not to say",
    "Prefer not to disclose",
}


def _normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    return text if text else None


def validate_student_id(value: Any) -> int:
    """Validate that student_id is a positive integer."""
    if value is None:
        raise ValidationError("Student ID is required.")

    if isinstance(value, str):
        value = value.strip()
        if not value.isdigit():
            raise ValidationError("Student ID must be a positive integer.")
        value = int(value)

    if not isinstance(value, int) or value <= 0:
        raise ValidationError("Student ID must be a positive integer.")

    return value


def validate_name(name: Any, field_name: str = "Name") -> str:
    """Validate non-empty text for student or subject names."""
    text = _normalize_text(name)
    if text is None:
        raise ValidationError(f"{field_name} is required and cannot be empty.")

    if len(text) > 100:
        raise ValidationError(f"{field_name} must have at most 100 characters.")

    return text


def validate_optional_text(value: Any, field_name: str, max_length: int = 100) -> Optional[str]:
    """Validate optional string fields such as department and grade."""
    if value is None:
        return None

    text = _normalize_text(value)
    if text is None:
        return None

    if len(text) > max_length:
        raise ValidationError(f"{field_name} must have at most {max_length} characters.")

    return text


def validate_age(value: Any, allow_empty: bool = True) -> Optional[int]:
    """Validate that age is a positive integer in a realistic range."""
    text = _normalize_text(value)
    if text is None:
        if allow_empty:
            return None
        raise ValidationError("Age is required.")

    if not text.isdigit():
        raise ValidationError("Age must be a positive integer.")

    age = int(text)
    if age <= 0 or age > 130:
        raise ValidationError("Age must be between 1 and 130.")

    return age


def validate_gender(value: Any, allow_empty: bool = True) -> Optional[str]:
    """Validate and normalize gender input."""
    text = _normalize_text(value)
    if text is None:
        return None if allow_empty else validate_name(value, "Gender")

    normalized = text.title()
    if normalized in GENDER_CHOICES:
        return normalized

    short_map = {
        "m": "Male",
        "f": "Female",
        "o": "Other",
        "nb": "Non-binary",
        "n": "Prefer not to say",
    }
    normalized = short_map.get(text.lower(), normalized)
    if normalized in GENDER_CHOICES:
        return normalized

    raise ValidationError(
        f"Gender must be one of: {', '.join(sorted(GENDER_CHOICES))}."
    )


def validate_semester(value: Any, allow_empty: bool = True) -> Optional[int]:
    """Validate the semester value as an integer between 1 and 12."""
    text = _normalize_text(value)
    if text is None:
        if allow_empty:
            return None
        raise ValidationError("Semester is required.")

    if not text.isdigit():
        raise ValidationError("Semester must be a positive integer.")

    semester = int(text)
    if semester <= 0 or semester > 12:
        raise ValidationError("Semester must be between 1 and 12.")

    return semester


def validate_department(value: Any, allow_empty: bool = True) -> Optional[str]:
    """Validate department text as an optional field."""
    return validate_optional_text(value, "Department", max_length=100)


def validate_subject_name(value: Any) -> str:
    """Validate subject names used for marks records."""
    return validate_name(value, field_name="Subject")


def validate_marks(value: Any) -> int:
    """Validate marks in the inclusive range 0-100."""
    text = _normalize_text(value)
    if text is None:
        raise ValidationError("Marks are required.")

    if not re.fullmatch(r"\d+", text):
        raise ValidationError("Marks must be a whole number between 0 and 100.")

    value_int = int(text)
    if value_int < 0 or value_int > 100:
        raise ValidationError("Marks must be between 0 and 100.")

    return value_int


def ensure_unique_student_id(student_id: int, exists: Callable[[int], bool]) -> None:
    """Raise when a student ID already exists in the system."""
    if exists(student_id):
        raise DuplicateIDError(f"Student ID {student_id} already exists.")


def ensure_student_exists(student_id: int, exists: Callable[[int], bool]) -> None:
    """Raise when the referenced student does not exist."""
    if not exists(student_id):
        raise MissingRecordError(f"Student with ID {student_id} was not found.")


def ensure_mark_exists(mark_id: int, exists: Callable[[int], bool]) -> None:
    """Raise when the referenced marks record does not exist."""
    if not exists(mark_id):
        raise MissingRecordError(f"Marks record with ID {mark_id} was not found.")
