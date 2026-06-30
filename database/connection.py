from pathlib import Path
import sqlite3
from sqlite3 import Error
from config import DB_FILE


def get_connection():
    """Create and return a database connection to the SQLite database.

    The database file is stored in the workspace root so all code paths use the same file
    regardless of the current working directory.
    """
    try:
        connection = sqlite3.connect(DB_FILE)
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection
    except Error as error:
        print(f"Database connection error: {error}")
        return None
