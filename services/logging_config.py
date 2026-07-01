from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"


def configure_logging(log_dir: Optional[Path] = None) -> None:
    """Configure rotating file handlers for the application."""
    log_directory = log_dir or LOG_DIR
    log_directory.mkdir(parents=True, exist_ok=True)

    for file_name in ["application.log", "database.log", "errors.log"]:
        (log_directory / file_name).touch(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.handlers:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
            handler.close()

    logger = logging.getLogger("student_system")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    for handler_name, file_name, level in [
        ("application", "application.log", logging.INFO),
        ("database", "database.log", logging.INFO),
        ("errors", "errors.log", logging.ERROR),
    ]:
        file_handler = logging.handlers.RotatingFileHandler(
            log_directory / file_name,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.set_name(handler_name)
        logger.addHandler(file_handler)

    logger.info("Logging initialized")
