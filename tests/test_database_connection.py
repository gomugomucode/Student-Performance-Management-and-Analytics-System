import os
import unittest
from unittest.mock import patch

from database.connection import get_database_config, get_connection_string


class TestDatabaseConnectionConfig(unittest.TestCase):
    @patch.dict(os.environ, {"DB_HOST": "db.internal", "DB_PORT": "5433", "DB_NAME": "studentdb", "DB_USER": "appuser", "DB_PASSWORD": "secret"}, clear=True)
    def test_get_database_config_uses_environment_values(self):
        config = get_database_config()

        self.assertEqual(config["host"], "db.internal")
        self.assertEqual(config["port"], 5433)
        self.assertEqual(config["dbname"], "studentdb")
        self.assertEqual(config["user"], "appuser")
        self.assertEqual(config["password"], "secret")

    @patch.dict(os.environ, {}, clear=True)
    def test_get_connection_string_has_postgresql_scheme(self):
        connection_string = get_connection_string()

        self.assertTrue(connection_string.startswith("postgresql://"))


if __name__ == "__main__":
    unittest.main()
