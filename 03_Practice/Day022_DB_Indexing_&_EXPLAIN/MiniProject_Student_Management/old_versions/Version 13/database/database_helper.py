"""
Database Helper Module.

This module manages PostgreSQL database connections and SQL query executions using psycopg library.

Day 017 Update: All print() statements replaced with structured logger calls.
                Exception logging via logger.exception() inside try/except blocks to capture full stack traces.
Day 019 Update: Database connection settings now read from config.py / .env (Exercise 5).
                Removed individual os.getenv() calls — settings object is the single source of truth.
"""

import psycopg

from config import settings
from logger_config import get_logger

logger = get_logger(__name__)


class DatabaseHelper:
    """
    A helper class to manage PostgreSQL database connections and basic operations.
    Supports configuration via environment variables for deployment flexibility.
    """

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        """
        Initialize database connection settings.

        If arguments are passed explicitly (e.g., from tests), they take priority.
        Otherwise, values are read from the centralized settings object which
        sources from .env / environment variables (Day 019 Exercise 5).

        Args:
            dbname (str, optional): PostgreSQL database name.
            user (str, optional): PostgreSQL username.
            password (str, optional): PostgreSQL password.
            host (str, optional): Database server host.
            port (str, optional): Database server port.
        """
        # Day 019 Exercise 5: Prefer explicit args (useful in tests), fall back to settings.
        self.dbname = dbname or settings.db_name
        self.user = user or settings.db_user
        self.password = password or settings.db_password
        self.host = host or settings.db_host
        self.port = port or str(settings.db_port)
        self.connection = None
        logger.debug(
            "DatabaseHelper initialized — host=%s, port=%s, db=%s, user=%s",
            self.host, self.port, self.dbname, self.user,
        )

    def connect(self):
        """
        Create a PostgreSQL database connection and ensure required tables exist.

        Returns:
            psycopg.Connection: Active database connection instance.

        Raises:
            psycopg.OperationalError: If connection to PostgreSQL fails.
        """
        if self.connection is None:
            try:
                logger.debug(
                    "Opening PostgreSQL connection to %s:%s/%s...",
                    self.host, self.port, self.dbname,
                )
                self.connection = psycopg.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port,
                )
                # Ensure the students table exists with all required columns
                self._create_table_if_not_exists()
                logger.info("PostgreSQL connection established and schema verified.")
            except Exception:
                # Exercise 4: logger.exception() captures the full stack trace in the log file
                logger.exception(
                    "Failed to connect to PostgreSQL at %s:%s/%s",
                    self.host, self.port, self.dbname,
                )
                raise
        return self.connection

    def _create_table_if_not_exists(self):
        """
        Create the 'students' table if it does not already exist in PostgreSQL.
        Includes all columns: id, name, age, city, email.
        """
        logger.debug("Checking/creating 'students' table schema...")
        with self.connection.cursor() as cur:
            # We add 'age' and 'city' columns to the create statement.
            # In the original CLI version, the table only had id and name, but the models
            # and repository queried age and city, which would fail if the database table didn't have them.
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    age INTEGER,
                    city VARCHAR(100),
                    email VARCHAR(100)
                )
                """
            )
        self.connection.commit()
        logger.debug("'students' table is ready.")

    def execute_query(self, query, params=None, commit=False):
        """
        Execute an SQL query against PostgreSQL database.

        Args:
            query (str): SQL query statement.
            params (tuple, optional): Parameters for SQL query. Defaults to None.
            commit (bool): Whether to commit transaction. Defaults to False.

        Returns:
            list | None: Query results if rows exist, otherwise None.

        Raises:
            Exception: Re-raises any psycopg database error after logging it.
        """
        if self.connection is None:
            self.connect()

        try:
            with self.connection.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchall() if cur.description else None

            if commit:
                self.connection.commit()

            logger.debug("Query executed successfully: %.80s", query.strip())
            return result

        except Exception:
            # Exercise 4: Log exception with full stack trace for any DB query failure
            logger.exception("Database query failed. Query: %.80s", query.strip())
            raise

    def fetch_all(self, query, params=None):
        """
        Fetch all matching rows for a SELECT query.

        Args:
            query (str): SQL SELECT query statement.
            params (tuple, optional): Parameters for SQL query. Defaults to None.

        Returns:
            list: List of row tuples matching query.
        """
        return self.execute_query(query, params=params, commit=False) or []

    def fetch_one(self, query, params=None):
        """
        Fetch a single matching row for a SELECT query.

        Args:
            query (str): SQL SELECT query statement.
            params (tuple, optional): Parameters for SQL query. Defaults to None.

        Returns:
            tuple | None: First matching row tuple, or None if no record found.
        """
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def close(self):
        """
        Close the PostgreSQL database connection to free resources.
        """
        if self.connection is not None:
            try:
                self.connection.close()
                self.connection = None
                logger.info("PostgreSQL connection closed successfully.")
            except Exception:
                logger.exception("Error occurred while closing the PostgreSQL connection.")
