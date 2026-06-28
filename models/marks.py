from database.connection import get_connection



def add_marks(student_id, subject, marks):
    """Adds marks for a student in a specific subject."""
    query = "INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?);"
    
    conn = get_connection()
    if conn is None:
        return False
        
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        with conn:
            conn.execute(query, (student_id, subject, marks))
        return True
    except Exception as e:
        print(f"Error adding marks: {e}")
        return False
    finally:
        conn.close()

def get_marks(student_id):
    """Retrieves marks for a specific student as a list of dictionaries."""
    query = "SELECT subject, marks FROM marks WHERE student_id = ?;"
    
    conn = get_connection()
    if conn is None:
        return []
        
    try:
        cursor = conn.cursor()
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()
        
        # Convert tuples to list of dictionaries
        return [{"subject": row[0], "marks": row[1]} for row in rows]
    except Exception as e:
        print(f"Error retrieving marks: {e}")
        return []
    finally:
        conn.close()

def update_marks(mark_id, subject=None, marks=None):
    """Updates fields dynamically for a specific marks record."""
    # If no parameters are provided to update, exit early
    if subject is None and marks is None:
        return False

    # Dynamically build the UPDATE query based on provided arguments
    #  It is designed to be dynamic, meaning it allows you to update just the subject, just the marks, or both at the same time without overwriting unchanged data.
    fields = []
    params = []
    
    if subject is not None:
        fields.append("subject = ?")
        params.append(subject)
    if marks is not None:
        fields.append("marks = ?")
        params.append(marks)
    
    # ', '.join(fields): This turns our list of strings into a single string separated by commas.If updating both, it becomes: subject = ?, marks = ?If updating just marks, it becomes: marks = ?
        
    query = f"UPDATE marks SET {', '.join(fields)} WHERE mark_id = ?;"
    params.append(mark_id)

    conn = get_connection()
    if conn is None:
        return False
        
    try:
        with conn:
            cursor = conn.execute(query, tuple(params))
            # Verify if the row actually existed and was changed
            if cursor.rowcount == 0:
                print(f"No record found with mark_id: {mark_id}")
                return False
        return True
    except Exception as e:
        print(f"Error updating marks: {e}")
        return False
    finally:
        conn.close()

def delete_marks(mark_id):
    """Deletes a marks record from the database."""
    query = "DELETE FROM marks WHERE mark_id = ?;"
    
    conn = get_connection()
    if conn is None:
        return False
        
    try:
        with conn:
            cursor = conn.execute(query, (mark_id,))
            if cursor.rowcount == 0:
                print(f"No record found with mark_id: {mark_id}")
                return False
        return True
    except Exception as e:
        print(f"Error deleting marks: {e}")
        return False
    finally:
        conn.close()
