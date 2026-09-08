"""
test_student_repository.py — Integration tests for PostgresStudentRepository.

Day 033 Exercise 7.

WHY integration tests?
----------------------
Unlike unit tests (which mock the repository), integration tests intentionally
exercise the REAL repository against a REAL database.  They verify:
  - SQL queries are syntactically and semantically correct.
  - Data is persisted and retrieved with the correct shape.
  - The DatabaseHelper connection pool interacts correctly with PostgreSQL.

Architecture for these tests:
  Test
    ↓
  PostgresStudentRepository   ← real implementation
    ↓
  DatabaseHelper              ← real pool
    ↓
  local PostgreSQL (student_db) ← real database, isolated test table

ISOLATION STRATEGY:
  Tests run against a dedicated "test_students" table that is:
    - Created before the first test (session-scoped fixture).
    - Emptied before each individual test (function-scoped fixture).
    - Dropped after the entire session completes.
  This means they never touch the real "students" table and leave no
  permanent artifacts even if a test run is interrupted.

PREREQUISITE:
  Local PostgreSQL must be running and reachable at:
    host=localhost, port=5432, db=student_db, user=postgres
  (credentials read from .env via DatabaseHelper → config → settings).
  Tests are skipped automatically if the connection cannot be established.
"""

import pytest
import psycopg

from database.database_helper import DatabaseHelper
from repositories.student_repository import PostgresStudentRepository
from models.student import Student_model, Student_response_model


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

# Separate table name used exclusively during testing.
# Using a distinct name guarantees these tests never accidentally modify
# the real "students" table that holds development or production data.
TEST_TABLE = "test_students"


# ─────────────────────────────────────────────────────────────────────────────
# Session-scoped DB helper (pool opened once for the whole test session)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def db_helper():
    """
    Open a real DatabaseHelper connection pool for the test session.

    scope="session" means this fixture is created ONCE and shared across
    all tests in this module.  Opening/closing the pool for each individual
    test would be unnecessarily slow for an integration suite.

    The test is skipped automatically if the local PostgreSQL server is not
    reachable — this prevents CI failures on machines without a database.
    """
    helper = DatabaseHelper(
        # Connect to localhost regardless of what .env says (which may point
        # to "db" — the Docker Compose service hostname).
        host="localhost",
        port="5432",
    )
    try:
        helper.open_pool()
    except Exception as exc:
        pytest.skip(
            f"Integration tests skipped — local PostgreSQL not reachable: {exc}"
        )

    yield helper

    # Teardown: close the pool after all session tests complete.
    helper.close_pool()


# ─────────────────────────────────────────────────────────────────────────────
# Session-scoped: create the test table once, drop it after the session
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def create_test_table(db_helper: DatabaseHelper):
    """
    Create an isolated test table before any integration test runs.

    We mirror the "students" schema exactly so the repository's SQL queries
    work unmodified.  autouse=True means this fixture runs automatically for
    every test in the integration/ directory even if not explicitly requested.

    The table is dropped during teardown (after yield) to leave the database
    in a clean state after the test session.
    """
    create_sql = f"""
        CREATE TABLE IF NOT EXISTS {TEST_TABLE} (
            id    INTEGER PRIMARY KEY,
            name  VARCHAR(100) NOT NULL,
            age   INTEGER      NOT NULL,
            city  VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE
        )
    """
    drop_sql = f"DROP TABLE IF EXISTS {TEST_TABLE}"

    # Use a raw psycopg connection (outside the pool) for DDL — keeps table
    # management fully separate from application query traffic.
    with db_helper._pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_sql)
        conn.commit()

    yield  # Run all tests

    # Teardown — drop the test table after the session
    with db_helper._pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(drop_sql)
        conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Function-scoped: empty the test table before each individual test
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_test_table(db_helper: DatabaseHelper, create_test_table):
    """
    Truncate the test table before each test function.

    This ensures every test starts from a known empty state regardless of
    what a previous test inserted.  Tests remain independent — a failure or
    unexpected insert in test A cannot cause test B to fail.
    """
    with db_helper._pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {TEST_TABLE} RESTART IDENTITY")
        conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Repository fixture pointing at the test table
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def repo(db_helper: DatabaseHelper) -> PostgresStudentRepository:
    """
    Return a PostgresStudentRepository backed by the isolated test table.

    We use a _TestDatabaseHelper subclass that intercepts every SQL string
    before it reaches psycopg and replaces 'students' with TEST_TABLE.
    Subclassing DatabaseHelper is the clean approach because psycopg's
    Cursor.execute() is a C-extension method and cannot be monkey-patched.
    """
    test_db_helper = _TestDatabaseHelper(db_helper)
    return PostgresStudentRepository(test_db_helper)


class _TestDatabaseHelper:
    """
    Lightweight adapter around DatabaseHelper that rewrites table names.

    Every SQL string is passed through _swap() before execution so that
    queries targeting 'students' land on TEST_TABLE instead.  This lets us
    reuse the real PostgresStudentRepository implementation unchanged while
    isolating all writes to the disposable test table.

    Why not subclass DatabaseHelper directly?
    -----------------------------------------
    DatabaseHelper.__init__ reads from settings and sets up pool state.
    We want to borrow an already-opened pool from the session-scoped
    db_helper fixture rather than opening a second pool — wrapping is
    simpler and avoids that coupling.
    """

    def __init__(self, real_helper: DatabaseHelper):
        # Expose the pool so any code that accesses _pool directly still works.
        self._pool = real_helper._pool
        self._real = real_helper

    # ── SQL table-name rewriter ──────────────────────────────────────────────

    @staticmethod
    def _swap(sql: str) -> str:
        """Replace the standalone word 'students' with TEST_TABLE."""
        import re
        return re.sub(r'\bstudents\b', TEST_TABLE, sql)

    # ── Public API mirroring DatabaseHelper ─────────────────────────────────

    def fetch_all(self, sql: str, params=None):
        """Forward to real helper with the table name swapped."""
        return self._real.fetch_all(self._swap(sql), params)

    def fetch_one(self, sql: str, params=None):
        """Forward to real helper with the table name swapped."""
        return self._real.fetch_one(self._swap(sql), params)

    def execute_write(self, sql: str, params=None):
        """Forward to real helper with the table name swapped."""
        return self._real.execute_write(self._swap(sql), params)

    def execute_write_transaction(self, fn):
        """
        Run a multi-step transaction but rewrite all SQL inside the function.

        We wrap the caller's function (fn) with our own function (_wrapped)
        that supplies a _SwappingCursor proxy instead of the real psycopg
        cursor.  The proxy intercepts execute() calls and rewrites SQL before
        forwarding them.

        Crucially, we do NOT assign to cur.execute because psycopg's Cursor
        is a C extension and its attributes are read-only — assigning raises
        AttributeError.  Wrapping in a proxy object avoids that completely.
        """
        def _wrapped(cur):
            # Give the caller a proxy that intercepts .execute() calls.
            return fn(_SwappingCursor(cur))

        return self._real.execute_write_transaction(_wrapped)


class _SwappingCursor:
    """
    Proxy wrapper around a psycopg Cursor that rewrites SQL before execution.

    This class is needed because psycopg's Cursor is a C extension and its
    instance attributes (including .execute) are read-only — we cannot
    monkey-patch them.  Instead we wrap the cursor in a plain Python object
    and forward all attribute access to the real cursor, intercepting only
    .execute() to swap the table name.
    """

    def __init__(self, real_cursor):
        # Store the real cursor in __dict__ to avoid triggering __setattr__.
        object.__setattr__(self, '_cur', real_cursor)

    def execute(self, sql: str, params=None):
        """Rewrite 'students' → TEST_TABLE then delegate to the real cursor."""
        import re
        swapped = re.sub(r'\bstudents\b', TEST_TABLE, sql)
        return self._cur.execute(swapped, params)

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def __getattr__(self, name):
        """Delegate any other attribute/method access to the real cursor."""
        return getattr(self._cur, name)


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 7: Integration tests
# ─────────────────────────────────────────────────────────────────────────────

class TestIntegrationStudentRepository:
    """
    Integration tests for PostgresStudentRepository.

    These tests exercise the REAL repository against a REAL (isolated) database
    table.  They prove that:
      - SQL INSERT is correct and returns the assigned id.
      - SQL SELECT by id finds the persisted row.
      - SQL SELECT for a missing id returns None.
      - SQL DELETE removes the row and returns True.
      - SQL SELECT * returns all rows in id order.
    """

    def test_add_and_retrieve_student(self, repo: PostgresStudentRepository):
        """
        Add a student via the repository, then retrieve it by id.

        This is the most fundamental integration test: it proves the full
        round-trip (INSERT → SELECT) works end-to-end with real PostgreSQL.
        """
        # ARRANGE
        student_data = Student_model(
            name="Integration Alice",
            age=23,
            city="Bangalore",
            email="integ.alice@example.com",
        )

        # ACT — add to the real (test) database
        created = repo.add_student(student_data)

        # ASSERT — the returned model has a valid id
        assert created.id is not None
        assert created.id >= 1
        assert created.name == "Integration Alice"
        assert created.city == "Bangalore"

        # Retrieve by id to confirm persistence
        fetched = repo.get_student_by_id(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Integration Alice"
        assert fetched.email == "integ.alice@example.com"

    def test_get_student_by_id_returns_none_when_not_found(
        self, repo: PostgresStudentRepository
    ):
        """
        Querying a non-existent id must return None (not raise an exception).

        This verifies the repository's "not found" contract:
          Repository returns None → Service raises StudentNotFoundException.
        The service behaviour (exception raising) is tested separately in
        the unit tests.
        """
        result = repo.get_student_by_id(99999)

        assert result is None

    def test_get_all_students_returns_inserted_records(
        self, repo: PostgresStudentRepository
    ):
        """
        All inserted students must appear in get_all_students(), ordered by id.
        """
        # Insert two students
        repo.add_student(Student_model(
            name="Bob Integration", age=20, city="Mumbai", email="bob.integ@example.com"
        ))
        repo.add_student(Student_model(
            name="Carol Integration", age=21, city="Delhi", email="carol.integ@example.com"
        ))

        all_students = repo.get_all_students()

        assert len(all_students) == 2
        # Results must be ordered by id (smallest first)
        assert all_students[0].id < all_students[1].id
        names = {s.name for s in all_students}
        assert "Bob Integration" in names
        assert "Carol Integration" in names

    def test_delete_student_returns_true_and_removes_record(
        self, repo: PostgresStudentRepository
    ):
        """
        Deleting an existing student must return True and make the record unreachable.
        """
        created = repo.add_student(Student_model(
            name="Dave Integration", age=24, city="Hyderabad", email="dave.integ@example.com"
        ))

        # Delete must report success
        deleted = repo.delete_student(created.id)
        assert deleted is True

        # The student must no longer exist
        result = repo.get_student_by_id(created.id)
        assert result is None

    def test_delete_nonexistent_student_returns_false(
        self, repo: PostgresStudentRepository
    ):
        """
        Attempting to delete a student that does not exist must return False.

        The repository returns False (not raise) — the service layer is
        responsible for converting that to StudentNotFoundException.
        """
        result = repo.delete_student(99999)
        assert result is False
