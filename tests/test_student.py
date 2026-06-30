import unittest

from services.validation import (
    ValidationError,
    validate_age,
    validate_department,
    validate_gender,
    validate_name,
    validate_semester,
    validate_student_id,
)


class TestValidation(unittest.TestCase):
    def test_validate_student_id_accepts_positive_int(self):
        self.assertEqual(validate_student_id(10), 10)

    def test_validate_student_id_rejects_negative(self):
        with self.assertRaises(ValidationError):
            validate_student_id(-1)

    def test_validate_name_rejects_empty(self):
        with self.assertRaises(ValidationError):
            validate_name("   ")

    def test_validate_name_accepts_text(self):
        self.assertEqual(validate_name("Alice"), "Alice")

    def test_validate_gender_normalizes_short_codes(self):
        self.assertEqual(validate_gender("M"), "Male")
        self.assertEqual(validate_gender("f"), "Female")

    def test_validate_department_allows_none(self):
        self.assertIsNone(validate_department(None))

    def test_validate_semester_valid(self):
        self.assertEqual(validate_semester("3"), 3)

    def test_validate_age_allows_none(self):
        self.assertIsNone(validate_age(None))


if __name__ == "__main__":
    unittest.main()
