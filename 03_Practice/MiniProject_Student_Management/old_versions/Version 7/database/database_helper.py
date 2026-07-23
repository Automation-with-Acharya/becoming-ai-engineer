"""
Database Helper Module.

This module manages PostgreSQL database connections and SQL query executions using psycopg library.
"""

import os
import psycopg


class DatabaseHelper:
    """
    A helper class to manage PostgreSQL database connections and basic operations.
    Supports configuration via environment variables for deployment flexibility.
    """

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        """
        Initialize database connection settings. If arguments are not passed,
        they will fall back to environment variables or safe defaults.

        Args:
            dbname (str, optional): PostgreSQL database name.
            user (str, optional): PostgreSQL username.
            password (str, optional): PostgreSQL password.
            host (str, optional): Database server host.
            port (str, optional): Database server port.
        """
        # Read from environment variables if not passed explicitly, or fall back to CLI defaults.
        # This makes it easy to transition from local development to production or containerized environments.
        self.dbname = dbname or os.getenv("DB_NAME", "student_db")
        self.user = user or os.getenv("DB_USER", "postgres")
        self.password = password or os.getenv("DB_PASSWORD", "password@postgres")
        self.host = host or os.getenv("DB_HOST", "localhost")
        self.port = port or os.getenv("DB_PORT", "5432")
        self.connection = None

    def connect(self):
        """
        Create a PostgreSQL database connection and ensure required tables exist.

        Returns:
            psycopg.Connection: Active database connection instance.
        """
        if self.connection is None:
            self.connection = psycopg.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            # Ensure the students table exists with all required columns
            self._create_table_if_not_exists()
        return self.connection

    def _create_table_if_not_exists(self):
        """
        Create the 'students' table if it does not already exist in PostgreSQL.
        Includes all columns: id, name, age, city.
        """
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
                    city VARCHAR(100)
                )
                """
            )
        self.connection.commit()

    def execute_query(self, query, params=None, commit=False):
        """
        Execute an SQL query against PostgreSQL database.

        Args:
            query (str): SQL query statement.
            params (tuple, optional): Parameters for SQL query. Defaults to None.
            commit (bool): Whether to commit transaction. Defaults to False.

        Returns:
            list | None: Query results if rows exist, otherwise None.
        """
        if self.connection is None:
            self.connect()

        with self.connection.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchall() if cur.description else None

        if commit:
            self.connection.commit()

        return result

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
            self.connection.close()
            self.connection = None
