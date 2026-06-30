from database.connection import get_connection

def create_tables():
    """Create the students and marks tables with required constraints."""

    students_table = """
    CREATE TABLE IF NOT EXISTS students(
        student_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        gender TEXT,
        semester INTEGER,
        department TEXT,
        age INTEGER,
        grade TEXT
    );
    """

    marks_table = """
    CREATE TABLE IF NOT EXISTS marks(
        mark_id INTEGER PRIMARY KEY,
        student_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        marks INTEGER NOT NULL CHECK(marks BETWEEN 0 AND 100),
        FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        UNIQUE(student_id, subject)
    );
    """

    conn = get_connection()
    if conn is not None:
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            with conn:
                cursor = conn.cursor()
                cursor.execute(students_table)
                cursor.execute(marks_table)
            print("Database tables initialized successfully with combined schema.")
        except Exception as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    create_tables()
