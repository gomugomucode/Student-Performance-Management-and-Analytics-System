from cli.actions import analytics_menu, export_menu, marks_menu, student_menu
from cli.utils import print_banner, print_menu, print_success, read_choice


def run_cli() -> None:
    """Run the top-level application menu."""
    print_banner("Student Performance Management System")

    while True:
        print_menu(
            "Main Menu",
            [
                "1. Student Management",
                "2. Marks Management",
                "3. Analytics",
                "4. Export",
                "5. Exit",
            ],
        )

        choice = read_choice("Select an option: ", 1, 5)

        if choice == 1:
            student_menu()
        elif choice == 2:
            marks_menu()
        elif choice == 3:
            analytics_menu()
        elif choice == 4:
            export_menu()
        else:
            print_success("Thank you for using the Student Performance Management System. Goodbye!")
            break
