from cli.actions import analytics_menu, export_menu, marks_menu, student_menu
from cli.utils import read_choice


def run_cli() -> None:
    """Run the top-level application menu."""
    print("\n=== Student Performance Management System ===\n")

    while True:
        print("Main Menu")
        print("1. Student Management")
        print("2. Marks Management")
        print("3. Analytics")
        print("4. Export")
        print("5. Exit")

        choice = read_choice("Enter your choice: ", 1, 5)

        if choice == 1:
            student_menu()
        elif choice == 2:
            marks_menu()
        elif choice == 3:
            analytics_menu()
        elif choice == 4:
            export_menu()
        else:
            print("\nThank you for using the Student Performance Management System. Goodbye!\n")
            break
