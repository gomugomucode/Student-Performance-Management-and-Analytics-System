import unittest

from models.marks import delete_marks_for_subject
from services.validation import ValidationError


class TestMarksDelete(unittest.TestCase):
    def test_delete_marks_for_subject_requires_subject(self):
        with self.assertRaises(ValidationError):
            delete_marks_for_subject(1, None)


if __name__ == "__main__":
    unittest.main()
