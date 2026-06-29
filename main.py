from database.schema import create_tables
from cli.menu import run_cli


def main() -> None:
    print("Initializing Student Performance Management System...")
    create_tables()
    run_cli()


if __name__ == "__main__":
    main()

