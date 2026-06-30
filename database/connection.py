from pathlib import Path
import sqlite3
from sqlite3 import Error

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "database.db"


def get_connection():
    """Create and return a database connection to the SQLite database.

    The database file is stored in the workspace root so all code paths use the same file
    regardless of the current working directory.
    """
    try:
        return sqlite3.connect(DB_FILE)
    except Error as e:
        print(f"Database connection error: {e}")
        return None
