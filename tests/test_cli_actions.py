import unittest
from unittest.mock import patch

from cli.actions import _select_student_from_name


class TestStudentSelection(unittest.TestCase):
    @patch("cli.actions.read_choice", return_value=2)
    @patch("cli.actions.search_students_records", return_value=[
        {"student_id": 1, "name": "Anupam"},
        {"student_id": 2, "name": "Anusha"},
    ])
    @patch("cli.actions.read_non_empty_text", return_value="anu")
    def test_select_student_from_name_uses_user_choice(self, _mock_prompt, _mock_search, _mock_choice):
        student = _select_student_from_name()

        self.assertEqual(student["student_id"], 2)
        self.assertEqual(student["name"], "Anusha")

    @patch("cli.actions.search_students_records", return_value=[{"student_id": 3, "name": "Anurag"}])
    @patch("cli.actions.read_non_empty_text", return_value="anu")
    def test_select_student_from_name_returns_single_match(self, _mock_prompt, _mock_search):
        student = _select_student_from_name()

        self.assertEqual(student["student_id"], 3)
        self.assertEqual(student["name"], "Anurag")


if __name__ == "__main__":
    unittest.main()
