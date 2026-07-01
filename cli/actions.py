from models.marks import add_marks as add_marks_record
from models.marks import delete_marks as delete_marks_record
from models.marks import get_marks as fetch_marks
from models.marks import update_marks as update_marks_record
from models.student import add_student as add_student_record
from models.student import delete_student as delete_student_record
from models.student import get_all_students as fetch_all_students
from models.student import get_student as fetch_student
from models.student import search_students as search_students_records
from models.student import student_id_exists
from models.student import update_student as update_student_record
from services.analytics import calculate_class_average, calculate_student_average, student_exists
from services.export import export_marks_to_csv, export_students_to_csv
from services.validation import (
    DatabaseConnectionError,
    DuplicateIDError,
    ExportError,
    MissingRecordError,
    ValidationError,
)
from cli.utils import (
    confirm_action,
    print_banner,
    print_error,
    print_info,
    print_menu,
    print_success,
    print_table,
    read_choice,
    read_int_range,
    read_non_empty_text,
    read_optional_text,
    read_positive_int,
    wait_for_enter,
)


def student_menu() -> None:
    """Render and manage the student submenu."""
    while True:
        print_banner("Student Management")
        print_menu(
            "Options",
            [
                "1. Add student",
                "2. View all students",
                "3. Search student",
                "4. View student",
                "5. Update student",
                "6. Delete student",
                "7. Back",
            ],
        )

        choice = read_choice("Select an option: ", 1, 7)

        if choice == 1:
            create_student()
        elif choice == 2:
            view_all_students()
        elif choice == 3:
            search_student()
        elif choice == 4:
            view_student()
        elif choice == 5:
            update_student()
        elif choice == 6:
            remove_student()
        else:
            break


def marks_menu() -> None:
    """Render and manage the marks submenu."""
    while True:
        print_banner("Marks Management")
        print_menu(
            "Options",
            [
                "1. Add marks",
                "2. View marks",
                "3. Update marks",
                "4. Delete marks",
                "5. Back",
            ],
        )

        choice = read_choice("Select an option: ", 1, 5)

        if choice == 1:
            create_marks()
        elif choice == 2:
            view_marks()
        elif choice == 3:
            update_marks()
        elif choice == 4:
            remove_marks()
        else:
            break


def analytics_menu() -> None:
    """Render and manage the analytics submenu."""
    while True:
        print_banner("Analytics")
        print_menu(
            "Options",
            [
                "1. Student average",
                "2. Class average",
                "3. Back",
            ],
        )

        choice = read_choice("Select an option: ", 1, 3)

        if choice == 1:
            student_average()
        elif choice == 2:
            class_average()
        else:
            break


def export_menu() -> None:
    """Render and manage the export submenu."""
    while True:
        print_banner("Export")
        print_menu(
            "Options",
            [
                "1. Export students to CSV",
                "2. Export marks to CSV",
                "3. Back",
            ],
        )

        choice = read_choice("Select an option: ", 1, 3)

        if choice == 1:
            export_students()
        elif choice == 2:
            export_marks()
        else:
            break


def create_student() -> None:
    print_banner("Add Student")
    student_id = read_positive_int("Student ID: ")

    if student_id_exists(student_id):
        print_error(f"Student ID {student_id} is already taken. Use a different ID.")
        wait_for_enter()
        return

    name = read_non_empty_text("Name: ")
    gender = read_optional_text("Gender [optional]: ")
    semester = read_positive_int("Semester [optional]: ", allow_empty=True)
    department = read_optional_text("Department [optional]: ")
    age = read_positive_int("Age [optional]: ", allow_empty=True)
    grade = read_optional_text("Grade [optional]: ")

    try:
        success = add_student_record(
            student_id,
            name,
            age=age,
            grade=grade,
            gender=gender,
            semester=semester,
            department=department,
        )
        if success:
            print_success("Student added successfully.")
        else:
            print_error("Failed to add the student.")
    except (ValidationError, DuplicateIDError, DatabaseConnectionError) as error:
        print_error(f"Unable to add student: {error}")
    except Exception as error:
        print_error(f"Unexpected error while adding student: {error}")

    wait_for_enter()


def view_student() -> None:
    print_banner("View Student")
    student_id = read_positive_int("Student ID: ")
    student = fetch_student(student_id)

    if not student:
        print_error(f"Student with ID {student_id} was not found.")
        wait_for_enter()
        return

    print_student_summary(student)
    wait_for_enter()


def view_all_students() -> None:
    print_banner("All Students")
    students = fetch_all_students()

    if not students:
        print_info("No students are registered yet.")
        wait_for_enter()
        return

    print_success(f"Found {len(students)} student(s).")
    headers = ["ID", "Name", "Gender", "Semester", "Department", "Age", "Grade"]
    rows = [
        [
            str(student.get("student_id", "")),
            student.get("name", ""),
            student.get("gender", ""),
            str(student.get("semester", "")) if student.get("semester") is not None else "",
            student.get("department", ""),
            str(student.get("age", "")) if student.get("age") is not None else "",
            student.get("grade", ""),
        ]
        for student in students
    ]
    print_table(headers, rows)
    wait_for_enter()


def search_student() -> None:
    print_banner("Search Student")
    query = read_non_empty_text("Enter student ID or name fragment: ")
    results = search_students_records(query)

    if not results:
        print_error("No students matched your search. Try a different ID or name.")
        wait_for_enter()
        return

    print_success(f"Found {len(results)} matching student(s).")
    headers = ["ID", "Name", "Gender", "Semester", "Department", "Age", "Grade"]
    rows = [
        [
            str(student.get("student_id", "")),
            student.get("name", ""),
            student.get("gender", ""),
            str(student.get("semester", "")) if student.get("semester") is not None else "",
            student.get("department", ""),
            str(student.get("age", "")) if student.get("age") is not None else "",
            student.get("grade", ""),
        ]
        for student in results
    ]
    print_table(headers, rows)
    wait_for_enter()


def update_student() -> None:
    print_banner("Update Student")
    student_id = read_positive_int("Student ID: ")
    student = fetch_student(student_id)

    if not student:
        print_error(f"Student with ID {student_id} was not found.")
        wait_for_enter()
        return

    print_student_summary(student)
    print_info("Enter new values, or leave blank to keep the current value.")

    name = read_optional_text("Name [optional]: ")
    gender = read_optional_text("Gender [optional]: ")
    semester = read_positive_int("Semester [optional]: ", allow_empty=True)
    department = read_optional_text("Department [optional]: ")
    age = read_positive_int("Age [optional]: ", allow_empty=True)
    grade = read_optional_text("Grade [optional]: ")

    if name is None and gender is None and semester is None and department is None and age is None and grade is None:
        print_info("No changes were provided. Student update canceled.")
        wait_for_enter()
        return

    try:
        updated = update_student_record(
            student_id,
            name=name,
            gender=gender,
            semester=semester,
            department=department,
            age=age,
            grade=grade,
        )
        if updated:
            print_success("Student updated successfully.")
        else:
            print_error("Student update failed.")
    except (ValidationError, MissingRecordError, DatabaseConnectionError) as error:
        print_error(f"Unable to update student: {error}")
    except Exception as error:
        print_error(f"Unexpected error while updating student: {error}")
    wait_for_enter()


def remove_student() -> None:
    print_banner("Delete Student")
    student_id = read_positive_int("Student ID: ")
    student = fetch_student(student_id)

    if not student:
        print_error(f"Student with ID {student_id} was not found.")
        wait_for_enter()
        return

    print_student_summary(student)
    if not confirm_action("Are you sure you want to delete this student? (Y/N): "):
        print_info("Delete operation canceled.")
        wait_for_enter()
        return

    try:
        deleted = delete_student_record(student_id)
        if deleted:
            print_success("Student deleted successfully.")
        else:
            print_error("Student deletion failed.")
    except (MissingRecordError, DatabaseConnectionError) as error:
        print_error(f"Unable to delete student: {error}")
    except Exception as error:
        print_error(f"Unexpected error while deleting student: {error}")
    wait_for_enter()


def create_marks() -> None:
    print_banner("Add Marks")
    student_id = read_positive_int("Student ID: ")
    subject = read_non_empty_text("Subject: ")
    marks = read_int_range("Marks (0-100): ", 0, 100)

    try:
        success = add_marks_record(student_id, subject, marks)
        if success:
            print_success("Marks added successfully.")
        else:
            print_error("Failed to add marks.")
    except (ValidationError, MissingRecordError, DuplicateIDError, DatabaseConnectionError) as error:
        print_error(f"Unable to add marks: {error}")
    except Exception as error:
        print_error(f"Unexpected error while adding marks: {error}")
    wait_for_enter()


def view_marks() -> None:
    print_banner("View Marks")
    student_id = read_positive_int("Student ID: ")

    if not student_id_exists(student_id):
        print_error(f"Student with ID {student_id} does not exist.")
        wait_for_enter()
        return

    marks = fetch_marks(student_id)
    if not marks:
        print_info(f"No marks found for student ID {student_id}.")
        wait_for_enter()
        return

    print_success(f"Found {len(marks)} record(s) for student {student_id}.")
    headers = ["Record ID", "Subject", "Marks"]
    rows = [
        [
            str(mark.get("mark_id", "")),
            mark.get("subject", ""),
            str(mark.get("marks", "")),
        ]
        for mark in marks
    ]
    print_table(headers, rows)
    wait_for_enter()


def update_marks() -> None:
    print_banner("Update Marks")
    mark_id = read_positive_int("Marks record ID: ")
    subject = read_optional_text("Subject [optional]: ")
    marks = read_int_range("Marks (0-100) [optional]: ", 0, 100, allow_empty=True)

    if subject is None and marks is None:
        print_info("No updates provided. Marks update canceled.")
        wait_for_enter()
        return

    try:
        success = update_marks_record(mark_id, subject=subject, marks=marks)
        if success:
            print_success("Marks updated successfully.")
        else:
            print_error("Marks update failed.")
    except (ValidationError, MissingRecordError, DuplicateIDError, DatabaseConnectionError) as error:
        print_error(f"Unable to update marks: {error}")
    except Exception as error:
        print_error(f"Unexpected error while updating marks: {error}")
    wait_for_enter()


def remove_marks() -> None:
    print_banner("Delete Marks")
    mark_id = read_positive_int("Marks record ID: ")

    if not confirm_action("Are you sure you want to delete this marks record? (Y/N): "):
        print_info("Delete operation canceled.")
        wait_for_enter()
        return

    try:
        deleted = delete_marks_record(mark_id)
        if deleted:
            print_success("Marks deleted successfully.")
        else:
            print_error("Marks deletion failed.")
    except (MissingRecordError, DatabaseConnectionError) as error:
        print_error(f"Unable to delete marks: {error}")
    except Exception as error:
        print_error(f"Unexpected error while deleting marks: {error}")
    wait_for_enter()


def student_average() -> None:
    print_banner("Student Average")
    student_id = read_positive_int("Student ID: ")

    if not student_exists(student_id):
        print_error(f"Student with ID {student_id} does not exist.")
        wait_for_enter()
        return

    average = calculate_student_average(student_id)
    if average is None:
        print_info("No marks are available for this student.")
    else:
        print_success(f"Student {student_id} average: {average:.2f}")

    wait_for_enter()


def class_average() -> None:
    print_banner("Class Average")
    average = calculate_class_average()
    if average is None:
        print_info("No marks are available to calculate a class average.")
    else:
        print_success(f"Class average: {average:.2f}")

    wait_for_enter()


def export_students() -> None:
    print_banner("Export Students")
    try:
        path = export_students_to_csv()
        print_success(f"Student export completed: {path}")
    except ExportError as error:
        print_error(f"Export failed: {error}")
    except Exception as error:
        print_error(f"Unexpected export error: {error}")
    wait_for_enter()


def export_marks() -> None:
    print_banner("Export Marks")
    try:
        path = export_marks_to_csv()
        print_success(f"Marks export completed: {path}")
    except ExportError as error:
        print_error(f"Export failed: {error}")
    except Exception as error:
        print_error(f"Unexpected export error: {error}")
    wait_for_enter()


def print_student_summary(student: dict) -> None:
    print("Student details:")
    print(f"  ID: {student['student_id']}")
    print(f"  Name: {student['name']}")
    print(f"  Gender: {student.get('gender', 'N/A')}")
    print(f"  Semester: {student.get('semester', 'N/A')}")
    print(f"  Department: {student.get('department', 'N/A')}")
    print(f"  Age: {student.get('age', 'N/A')}")
    print(f"  Grade: {student.get('grade', 'N/A')}")


