import logging
import unittest
from pathlib import Path

from services.logging_config import configure_logging


class TestLoggingConfig(unittest.TestCase):
    def test_configure_logging_creates_rotating_handlers(self):
        configure_logging()
        log_dir = Path(__file__).resolve().parent.parent / "logs"
        self.assertTrue(log_dir.exists())
        self.assertTrue((log_dir / "application.log").exists())
        self.assertTrue((log_dir / "database.log").exists())
        self.assertTrue((log_dir / "errors.log").exists())

        logger = logging.getLogger("student_system")
        self.assertTrue(any(isinstance(handler, logging.handlers.RotatingFileHandler) for handler in logger.handlers))


if __name__ == "__main__":
    unittest.main()
