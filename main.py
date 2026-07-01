from database.schema import create_tables
from cli.menu import run_cli
from services.error_handling import log_exception
from services.logging_config import configure_logging


def main() -> None:
    print("Initializing Student Performance Management System...")
    configure_logging()
    try:
        create_tables()
        run_cli()
    except Exception as error:
        log_exception(error, "application startup")
        raise


if __name__ == "__main__":
    main()

