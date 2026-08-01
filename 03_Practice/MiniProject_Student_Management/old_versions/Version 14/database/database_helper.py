"""
Database Helper Module.

This module manages PostgreSQL database connections and SQL query executions using psycopg library.

Day 017 Update: All print() statements replaced with structured logger calls.
                Exception logging via logger.exception() inside try/except blocks to capture full stack traces.
Day 019 Update: Database connection settings now read from config.py / .env (Exercise 5).
                Removed individual os.getenv() calls — settings object is the single source of truth.
Day 020 Update: Proper ACID transaction handling added.
                execute_write() wraps single write queries in an explicit BEGIN/COMMIT/ROLLBACK block.
                execute_write_transaction() runs a caller-supplied sequence of queries atomically.
                execute_query() now issues a rollback on failure to leave the connection in a clean state.
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

        Prefer `execute_write()` for INSERT / UPDATE / DELETE — it wraps the
        operation in an explicit transaction with automatic rollback on failure.
        Use this method directly only for SELECT queries or when `commit=False`.

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
            # Day 020: Rollback on any failure to leave the connection in a clean, usable state.
            # Without rollback, psycopg leaves the connection in an aborted transaction state
            # and all subsequent queries on the same connection will fail with
            # "InFailedSqlTransaction" until the transaction is explicitly rolled back.
            try:
                self.connection.rollback()
                logger.warning("Transaction rolled back after query failure: %.80s", query.strip())
            except Exception:
                logger.exception("Rollback itself failed after query error.")
            logger.exception("Database query failed. Query: %.80s", query.strip())
            raise

    def execute_write(self, query, params=None):
        """
        Day 020: Execute a single write (INSERT / UPDATE / DELETE) inside an explicit
        ACID transaction.

        Why a dedicated write method?
        --------------------------------
        psycopg3 by default operates in autocommit=False mode, meaning every statement
        is inside an implicit transaction. However, relying on an implicit transaction
        makes it easy to forget committing or rolling back. This method makes the
        transaction lifecycle explicit and self-contained:

          1. Executes the write query inside psycopg's `connection.transaction()` block.
          2. On success  : COMMIT is issued automatically when the `with` block exits.
          3. On failure  : ROLLBACK is issued automatically — the DB is restored to its
                           pre-operation state (Atomicity guarantee).

        ACID properties guaranteed:
          - Atomicity    : The write either completes fully or not at all.
          - Consistency  : DB constraints (NOT NULL, PRIMARY KEY) are enforced before COMMIT.
          - Isolation    : The transaction is isolated from concurrent writes at the
                           default READ COMMITTED level PostgreSQL provides.
          - Durability   : After COMMIT, the change survives server restarts.

        Args:
            query (str): SQL INSERT / UPDATE / DELETE statement.
            params (tuple, optional): Query parameters (use %s placeholders).

        Returns:
            None

        Raises:
            Exception: Re-raises any database error after logging and rolling back.
        """
        if self.connection is None:
            self.connect()

        try:
            with self.connection.transaction():   # BEGIN … COMMIT / ROLLBACK
                with self.connection.cursor() as cur:
                    cur.execute(query, params)
            logger.debug("Write transaction committed: %.80s", query.strip())
        except Exception:
            logger.exception("Write transaction rolled back. Query: %.80s", query.strip())
            raise

    def execute_write_transaction(self, steps):
        """
        Day 020: Execute multiple write queries as a single atomic transaction.

        Why this method?
        ----------------
        Some operations (e.g., ID-generation + INSERT) require two or more SQL
        statements to succeed or fail together. If the INSERT fails after the
        ID lookup has already read a value, re-running with a fresh ID lookup
        is safe. But wrapping both in one transaction prevents any other writer
        from grabbing the same ID in between (race condition under concurrent load).

        Usage example (repository):
            result = self.db_helper.execute_write_transaction([
                ("SELECT COALESCE(MAX(id),0)+1 FROM students", None, True),  # (query, params, fetch)
                lambda cur, next_id: cur.execute(INSERT_SQL, (next_id, ...)),
            ])

        For simplicity this API accepts a callable that receives the cursor and
        can return any value needed for subsequent steps:

            def steps(cur):
                cur.execute("SELECT COALESCE(MAX(id),0)+1 AS nid FROM students")
                next_id = cur.fetchone()[0]
                cur.execute(INSERT_SQL, (next_id, ...))
                return next_id

            new_id = self.db_helper.execute_write_transaction(steps)

        Args:
            steps (callable): A function that accepts a psycopg cursor and performs
                              all the necessary SQL operations. Its return value is
                              forwarded to the caller.

        Returns:
            Any: Whatever `steps(cursor)` returns.

        Raises:
            Exception: Re-raises any database error after rollback and logging.
        """
        if self.connection is None:
            self.connect()

        try:
            with self.connection.transaction():      # BEGIN … COMMIT / ROLLBACK
                with self.connection.cursor() as cur:
                    result = steps(cur)
            logger.debug("Multi-step write transaction committed.")
            return result
        except Exception:
            logger.exception("Multi-step write transaction rolled back.")
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
