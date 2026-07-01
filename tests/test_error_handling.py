import unittest

import psycopg

from services.error_handling import get_user_message, normalize_exception
from services.validation import DatabaseConnectionError, MissingRecordError, ValidationError


class TestErrorHandling(unittest.TestCase):
    def test_validation_error_returns_direct_message(self):
        error = ValidationError("Name is required.")
        self.assertEqual(get_user_message(error), "Name is required.")

    def test_missing_record_error_returns_friendly_message(self):
        error = MissingRecordError("Student not found")
        self.assertEqual(get_user_message(error), "The requested record could not be found.")

    def test_psycopg_error_returns_generic_database_message(self):
        error = psycopg.Error("syntax error")
        self.assertIn("temporarily unavailable", get_user_message(error))

    def test_unexpected_exception_is_reraised(self):
        with self.assertRaises(RuntimeError):
            normalize_exception(RuntimeError("boom"), "demo")


if __name__ == "__main__":
    unittest.main()
