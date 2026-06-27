from database.connection import get_connection

def create_tables():
    """Create the students and marks tables with foreign key constraints enforced."""
    
    students_table = """
    CREATE TABLE IF NOT EXISTS students(
        student_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        gender TEXT,
        semester INTEGER,
        department TEXT
    );
    """
    
    marks_table = """
    CREATE TABLE IF NOT EXISTS marks(
        mark_id INTEGER PRIMARY KEY,
        student_id INTEGER,
        subject TEXT,
        marks INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
    );
    """
    
    conn = get_connection()
    if conn is not None:
        try:
            # Enforce foreign key constraints in SQLite
            conn.execute("PRAGMA foreign_keys = ON;")
            
            # Use a context manager to handle transactions automatically
            with conn:
                cursor = conn.cursor()
                cursor.execute(students_table)
                cursor.execute(marks_table)
                
            print("Database tables initialized successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    create_tables()
