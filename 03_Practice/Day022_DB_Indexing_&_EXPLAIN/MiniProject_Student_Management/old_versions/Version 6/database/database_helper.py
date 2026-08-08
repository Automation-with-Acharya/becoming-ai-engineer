"""
Database Helper Module.

This module manages PostgreSQL database connections and SQL query executions using psycopg library.
"""

import psycopg


class DatabaseHelper:
    """
    A helper class to manage PostgreSQL database connections and basic operations.
    """

    def __init__(self, dbname="student_db", user="postgres", password="password@postgres", host="localhost", port="5432"):
        """
        Initialize database connection settings.

        Args:
            dbname (str): PostgreSQL database name. Defaults to 'student_db'.
            user (str): PostgreSQL username. Defaults to 'postgres'.
            password (str): PostgreSQL password.
            host (str): Database server host. Defaults to 'localhost'.
            port (str): Database server port. Defaults to '5432'.
        """
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
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
            # Ensure the students table exists
            self._create_table_if_not_exists()
        return self.connection

    def _create_table_if_not_exists(self):
        """
        Create the 'students' table if it does not already exist in PostgreSQL.
        """
        with self.connection.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL
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
