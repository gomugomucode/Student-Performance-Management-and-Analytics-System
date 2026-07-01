import unittest
from unittest.mock import patch

from models.student import search_students


class TestStudentSearch(unittest.TestCase):
    @patch("models.student._fetch_students")
    def test_search_students_uses_ilike_for_partial_name(self, mock_fetch):
        mock_fetch.return_value = [{"student_id": 1, "name": "Anupam"}]

        results = search_students("an")

        self.assertEqual(results[0]["name"], "Anupam")
        query, params = mock_fetch.call_args.args
        self.assertIn("ILIKE", query)
        self.assertNotIn("student_id = %s", query)
        self.assertEqual(params, ("%an%",))


if __name__ == "__main__":
    unittest.main()
