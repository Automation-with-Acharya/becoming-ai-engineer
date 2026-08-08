import psycopg


class DatabaseHelper:
    """A small helper class to manage PostgreSQL connections and basic student table operations."""

    def __init__(self, dbname="student_db", user="postgres", password="password@postgres", host="localhost", port="5432"):
        # Store the database connection details so the helper can reconnect whenever needed.
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        # Create a connection only once. If it already exists, reuse it.
        if self.connection is None:
            self.connection = psycopg.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            # Make sure the students table exists before using it.
            self._create_table_if_not_exists()
        return self.connection

    def _create_table_if_not_exists(self):
        # Create the students table if it does not already exist.
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
        # Open the connection if needed, then run the SQL query.
        if self.connection is None:
            self.connect()

        with self.connection.cursor() as cur:
            cur.execute(query, params)
            # If the query returns rows, collect them; otherwise return None.
            result = cur.fetchall() if cur.description else None

        # Commit only when asked, which is useful for INSERT, UPDATE, and DELETE.
        if commit:
            self.connection.commit()

        return result

    def fetch_all(self, query, params=None):
        # Return all rows for a SELECT query.
        return self.execute_query(query, params=params, commit=False) or []

    def fetch_one(self, query, params=None):
        # Return the first matching row, or None if no row exists.
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def close(self):
        # Close the database connection to free up resources.
        if self.connection is not None:
            self.connection.close()
            self.connection = None
