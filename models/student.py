
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.connection import get_connection

def add_student(student_id, name, age=None, grade=None, gender=None, semester=None, department=None):
    """
    Adds a new student to the database. Supports age/grade, gender/semester/department, or all.

    Args:
        student_id (int): The unique identifier for the student.
        name (str): The name of the student.
        age (int, optional): The age of the student.
        grade (str, optional): The grade of the student.
        gender (str, optional): The gender of the student.
        semester (int, optional): The semester of the student.
        department (str, optional): The department of the student.

    Returns:
        bool: True if the student was added successfully, False otherwise.
    """
    query = """
    INSERT INTO students (student_id, name, gender, semester, department, age, grade)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    
    conn = get_connection()
    if conn is None:
        return False
        
    try:
        with conn:
            cursor = conn.cursor()
            # Explicitly executing with all parameters (defaults will pass as None if omitted)
            cursor.execute(query, (student_id, name, gender, semester, department, age, grade))
        return True
    except Exception as e:
        print(f"Error adding student: {e}")
        return False
    finally:
        conn.close()




def get_student(student_id):
    """
    Retrieves a student's information from the database.

    Args:
        student_id (int): The unique identifier for the student.

    Returns:
        dict: A dictionary containing the student's information, or an empty dictionary if the student is not found.
    """
    # Code to retrieve the student from the database goes here
    query = """
    SELECT id, name,gender ,semester, department, age, grade FROM students WHERE id = ?;
    """
    
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute(query, (student_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "gender": row[2],
                "semester": row[3],
                "department": row[4],
                "age": row[5],
                "grade": row[6]
            }
        else:
            print(f"Student with ID {student_id} not found.")
            return {}
    except Exception as e:
        print(f"Error retrieving student from database: {e}")
        return {}
    finally:
        conn.close()



def update_student(student_id, name=None, gender=None, semester=None, department=None, age=None, grade=None):
    """
    Updates a student's information in the database.

    Args:
        student_id (int): The unique identifier for the student.
        name (str, optional): The new name of the student. Defaults to None.
        gender (str, optional): The new gender of the student. Defaults to None.
        semester (int, optional): The new semester of the student. Defaults to None.
        department (str, optional): The new department of the student. Defaults to None.
        age (int, optional): The new age of the student. Defaults to None.
        grade (str, optional): The new grade of the student. Defaults to None.

    Returns:
        bool: True if the student was updated successfully, False otherwise.
    """
    # Code to update the student in the database goes here
    pass

def delete_student(student_id):
    """
    Deletes a student from the database.

    Args:
        student_id (int): The unique identifier for the student.

    Returns:
        bool: True if the student was deleted successfully, False otherwise.
    """
    # Code to delete the student from the database goes here
    pass


