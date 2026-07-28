"""
Centralized Logging Configuration — Day 017: Python Logging Practice.

This module sets up a single, reusable logger for the entire application.
All other modules import and use `get_logger()` to obtain a correctly
configured Logger instance instead of calling `print()`.

Design decisions:
-----------------
- One root logger name ("student_management") is shared across all modules
  via child loggers (e.g., "student_management.routers.students").
  This ensures consistent formatting and avoids duplicate handlers.
- FileHandler writes ALL log records (DEBUG and above) to a rotating file.
- StreamHandler (console) shows INFO and above so the terminal stays readable.
- The Formatter includes timestamp, level, module name, and the message —
  giving full context in every log line.

Exercise 1: logging.basicConfig equivalent → replaced by manual Logger setup
            for finer-grained control (separate console vs file levels).
Exercise 2: Write logs to logs/application.log (FileHandler).
Exercise 3: Replace print() with logger.info() / logger.error() / logger.warning().
Exercise 4: Log exceptions inside try/except blocks with logger.exception().
Exercise 5: Review output on both console and log file.
"""

import logging
import os


# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "application.log")

# Root logger name — all child loggers in the app use this as their parent.
ROOT_LOGGER_NAME = "student_management"

# Log format: timestamp | level | module | message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ──────────────────────────────────────────────────────────────────────────────
# Internal: Build and wire the root application logger (called once at import)
# ──────────────────────────────────────────────────────────────────────────────

def _configure_root_logger() -> logging.Logger:
    """
    Create and configure the root 'student_management' logger.

    Handlers:
        FileHandler   → logs/application.log (level: DEBUG, captures everything)
        StreamHandler → console / terminal    (level: INFO, less noise in dev)

    The logger's own level is set to DEBUG so that both handlers receive all
    records; each handler then applies its own level filter.

    Returns:
        logging.Logger: Configured root application logger.
    """
    # Ensure the logs/ directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(ROOT_LOGGER_NAME)

    # Guard against duplicate handlers if this function is somehow called again
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)  # Let handlers decide their own threshold

    # ── Shared Formatter ─────────────────────────────────────────────────────
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # ── Exercise 2: File Handler ──────────────────────────────────────────────
    # Writes every log record (DEBUG+) to logs/application.log in append mode.
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # ── Exercise 1: Console (Stream) Handler ─────────────────────────────────
    # Shows INFO and above on the terminal so development output stays concise.
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Prevent records from being forwarded to the root (Python's root) logger,
    # which would cause duplicate output if third-party libs also log.
    # logger.propagate = False

    return logger


# Initialise once when this module is first imported.
_configure_root_logger()


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def get_logger(name: str) -> logging.Logger:
    """
    Retrieve a named child logger under the 'student_management' hierarchy.

    Usage (in any module):
        from logger_config import get_logger
        logger = get_logger(__name__)

    The `__name__` pattern produces names like:
        student_management.routers.students
        student_management.services.student_service
        student_management.database.database_helper

    All child loggers inherit the FileHandler and StreamHandler configured
    on the parent, so no additional setup is needed in each module.

    Args:
        name (str): Typically `__name__` of the calling module.

    Returns:
        logging.Logger: Named child logger ready for use.
    """
    # Build a fully-qualified child logger name, e.g.:
    #   __name__ = "routers.students"
    #   → full name = "student_management.routers.students"
    full_name = f"{ROOT_LOGGER_NAME}.{name}"
    return logging.getLogger(full_name)
