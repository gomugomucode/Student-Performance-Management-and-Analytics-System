from database.connection import get_connection, release_connection


def create_tables():
    """Create the students and marks tables with PostgreSQL-compatible constraints."""

    students_table = """
    CREATE TABLE IF NOT EXISTS students(
        student_id BIGSERIAL PRIMARY KEY,
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
        mark_id BIGSERIAL PRIMARY KEY,
        student_id BIGINT NOT NULL,
        subject TEXT NOT NULL,
        marks INTEGER NOT NULL CHECK(marks BETWEEN 0 AND 100),
        FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        UNIQUE(student_id, subject)
    );
    """

    conn = get_connection()
    if conn is None:
        print("Unable to initialize database tables because no PostgreSQL connection is available.")
        return

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(students_table)
                cursor.execute(marks_table)
        print("Database tables initialized successfully with PostgreSQL schema.")
    except Exception as error:
        print(f"Error creating tables: {error}")
    finally:
        release_connection(conn)


if __name__ == "__main__":
    create_tables()
