import unittest

from services.validation import ValidationError, validate_marks, validate_subject_name


class TestMarksValidation(unittest.TestCase):
    def test_validate_marks_accepts_zero(self):
        self.assertEqual(validate_marks(0), 0)

    def test_validate_marks_rejects_above_range(self):
        with self.assertRaises(ValidationError):
            validate_marks(150)

    def test_validate_subject_name_rejects_blank(self):
        with self.assertRaises(ValidationError):
            validate_subject_name("   ")

    def test_validate_subject_name_accepts_text(self):
        self.assertEqual(validate_subject_name("Math"), "Math")


if __name__ == "__main__":
    unittest.main()
