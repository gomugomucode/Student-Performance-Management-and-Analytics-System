import sqlite3
from sqlite3 import Error

DB_FILE = "database.db"

def get_connection():
    """Create and return a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
    return conn
