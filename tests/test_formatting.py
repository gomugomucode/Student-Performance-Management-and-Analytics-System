import unittest

from services.formatting import build_mark_rows, build_student_rows


class TestFormattingHelpers(unittest.TestCase):
    def test_build_student_rows_formats_known_fields(self):
        rows = build_student_rows(
            [
                {
                    "student_id": 1,
                    "name": "Alice",
                    "gender": "Female",
                    "semester": 2,
                    "department": "CS",
                    "age": 20,
                    "grade": "A",
                }
            ]
        )

        self.assertEqual(
            rows,
            [["1", "Alice", "Female", "2", "CS", "20", "A"]],
        )

    def test_build_mark_rows_formats_mark_records(self):
        rows = build_mark_rows(
            [
                {"mark_id": 10, "subject": "Math", "marks": 88},
                {"mark_id": 11, "subject": "Science", "marks": 91},
            ]
        )

        self.assertEqual(
            rows,
            [["10", "Math", "88"], ["11", "Science", "91"]],
        )


if __name__ == "__main__":
    unittest.main()
