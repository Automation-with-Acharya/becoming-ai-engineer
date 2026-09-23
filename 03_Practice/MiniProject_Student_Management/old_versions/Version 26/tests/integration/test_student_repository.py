"""
test_student_repository.py - Integration tests for PostgresStudentRepository.

Day 033 Exercise 7 + Day 034 Exercises 1-10.
Day 035 Exercise 2: @pytest.mark.integration applied to all test classes.

WHY integration tests?
----------------------
Unlike unit tests (which mock the repository), integration tests intentionally
exercise the REAL repository against a REAL database.  They verify:
  - SQL queries are syntactically and semantically correct.
  - Data is persisted and retrieved with the correct shape.
  - Database constraints (UNIQUE, NOT NULL, PRIMARY KEY) are enforced.
  - Transaction semantics (ROLLBACK on failure) work as expected.

ISOLATION STRATEGY (Day 033):
  Tests run against a dedicated "test_students" table that is:
    - Created before the first test (session-scoped fixture).
    - TRUNCATED before each individual test (function-scoped autouse fixture).
    - Dropped after the entire session completes.

Day 034 additions:
  - db_transaction fixture: demonstrates BEGIN -> Test -> ROLLBACK pattern.
  - Constraint failure tests: prove PostgreSQL enforces UNIQUE / PRIMARY KEY.
  - Rollback verification: confirm failed transactions leave no trace.
  - Atomicity test: partial write inside a failed transaction does not persist.
  - Failure cleanup drill: teardown runs even when a test raises.
  - Isolation check: test results are order-independent.

PREREQUISITE:
  Local PostgreSQL must be running (localhost:5432, db=student_db).
  Tests are skipped automatically if the connection cannot be established.
"""

import re
import pytest
import psycopg

from database.database_helper import DatabaseHelper
from repositories.student_repository import PostgresStudentRepository
from models.student import Student_model


# ---------------------------------------------------------------------------
# Constant: isolated test table name
# ---------------------------------------------------------------------------

# Using a distinct table name guarantees tests never touch the real "students"
# table that holds development or production data.
TEST_TABLE = "test_students"


# ---------------------------------------------------------------------------
# Session-scoped DB helper — pool opened once for the whole session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def db_helper():
    """
    Open a real DatabaseHelper pool for the entire test session.

    scope="session": created ONCE, shared across all integration tests.
    Auto-skips if local PostgreSQL is not reachable, preventing CI failures
    on machines without a running database server.
    """
    helper = DatabaseHelper(host="localhost", port="5432")
    try:
        helper.open_pool()
    except Exception as exc:
        pytest.skip(
            f"Integration tests skipped — local PostgreSQL not reachable: {exc}"
        )
    yield helper
    helper.close_pool()


# ---------------------------------------------------------------------------
# Session-scoped: create test table once, drop it at session end
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def create_test_table(db_helper: DatabaseHelper):
    """
    Create test_students once before any test; drop it at session end.

    Day 034 Exercise 1 — Lifecycle analysis:
      - CREATION  : Once at session start via CREATE TABLE IF NOT EXISTS.
      - OWNER     : This session-scoped fixture — pytest runs it first.
      - CLEANUP   : DROP TABLE in teardown (after yield) at session end.
      - ON FAILURE: The autouse clear_test_table TRUNCATES before the NEXT
        test, so a crashed test cannot leak data to its successor.  The DROP
        runs at session end via pytest's guaranteed fixture teardown.

    Lifecycle diagram:
      Session Start
        |
      CREATE TABLE (this fixture setup)
        |
      TRUNCATE before each test (clear_test_table autouse)
        |
      Test runs
        |
      TRUNCATE before next test (even if previous test failed)
        |
      Session End
        |
      DROP TABLE (this fixture teardown, after yield)
    """
    create_sql = f"""
        CREATE TABLE IF NOT EXISTS {TEST_TABLE} (
            id    INTEGER PRIMARY KEY,
            name  VARCHAR(100) NOT NULL,
            age   INTEGER      NOT NULL,
            city  VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        )
    """
    migrate_sql = f"""
        ALTER TABLE {TEST_TABLE}
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
        UPDATE {TEST_TABLE} SET is_active = TRUE WHERE is_active IS NULL;
        ALTER TABLE {TEST_TABLE} ALTER COLUMN is_active SET DEFAULT TRUE;
        ALTER TABLE {TEST_TABLE} ALTER COLUMN is_active SET NOT NULL;
    """
    drop_sql = f"DROP TABLE IF EXISTS {TEST_TABLE}"

    # Use a pool connection for DDL — keeps table management separate from
    # application query traffic.
    with db_helper._pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_sql)
            cur.execute(migrate_sql)
        conn.commit()

    yield  # all tests run here

    # Teardown: drop test table — runs even if tests failed.
    with db_helper._pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(drop_sql)
        conn.commit()


# ---------------------------------------------------------------------------
# Function-scoped autouse: TRUNCATE before each test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_test_table(db_helper: DatabaseHelper, create_test_table):
    """
    TRUNCATE the test table BEFORE each test function.

    Day 034 Exercise 1 — Why BEFORE (not after)?
      Cleaning before guarantees isolation even when the previous test
      crashed without teardown.  The fixture runs in setup phase, so the
      table is always empty when the test body begins.

    Day 034 Exercise 3 — TRUNCATE vs ROLLBACK:
      TRUNCATE  = physical data removal after the fact.
      ROLLBACK  = transactional state reset (data never committed).
      TRUNCATE is simpler here because the repository commits each write
      internally via execute_write_transaction() — there is no open
      transaction available for the test to roll back.
    """
    with db_helper._pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {TEST_TABLE} RESTART IDENTITY")
        conn.commit()


# ---------------------------------------------------------------------------
# Repo fixture — redirects all SQL to the isolated test table
# ---------------------------------------------------------------------------

@pytest.fixture
def repo(db_helper: DatabaseHelper) -> PostgresStudentRepository:
    """
    Return a PostgresStudentRepository backed by the isolated test table.

    The _TestDatabaseHelper adapter intercepts every SQL string and replaces
    'students' with TEST_TABLE before execution.  The real repository
    implementation runs completely unchanged.
    """
    return PostgresStudentRepository(_TestDatabaseHelper(db_helper))


class _TestDatabaseHelper:
    """
    Adapter around DatabaseHelper that rewrites SQL table names.

    Every SQL string targeting 'students' is redirected to TEST_TABLE.
    We wrap (rather than subclass) DatabaseHelper because its __init__
    reads settings and creates pool state — borrowing the already-opened
    session pool via wrapping is simpler and avoids that coupling.
    """

    def __init__(self, real_helper: DatabaseHelper):
        # Expose pool so any code that accesses _pool directly still works.
        self._pool = real_helper._pool
        self._real = real_helper

    @staticmethod
    def _swap(sql: str) -> str:
        """Replace standalone word 'students' with TEST_TABLE."""
        return re.sub(r'\bstudents\b', TEST_TABLE, sql)

    def fetch_all(self, sql, params=None):
        """Forward to real helper with table name swapped."""
        return self._real.fetch_all(self._swap(sql), params)

    def fetch_one(self, sql, params=None):
        """Forward to real helper with table name swapped."""
        return self._real.fetch_one(self._swap(sql), params)

    def execute_write(self, sql, params=None):
        """Forward to real helper with table name swapped."""
        return self._real.execute_write(self._swap(sql), params)

    def execute_write_transaction(self, fn):
        """
        Run a multi-step transaction with SQL rewritten to use TEST_TABLE.

        We wrap fn with _wrapped which supplies a _SwappingCursor proxy
        instead of the real psycopg cursor.  The proxy intercepts execute()
        and rewrites SQL before forwarding.

        We do NOT assign to cur.execute directly because psycopg Cursor is
        a C extension — its attributes are read-only (AttributeError).
        """
        def _wrapped(cur):
            return fn(_SwappingCursor(cur))
        return self._real.execute_write_transaction(_wrapped)


class _SwappingCursor:
    """
    Proxy for psycopg Cursor that rewrites SQL before execution.

    psycopg Cursor is a C extension — its attributes (including .execute)
    are read-only.  We wrap the cursor in a plain Python object and
    intercept only .execute(); everything else delegates to the real cursor.
    """

    def __init__(self, real_cursor):
        # Store in __dict__ directly to avoid triggering __setattr__.
        object.__setattr__(self, '_cur', real_cursor)

    def execute(self, sql: str, params=None):
        """Rewrite 'students' -> TEST_TABLE then delegate to real cursor."""
        swapped = re.sub(r'\bstudents\b', TEST_TABLE, sql)
        return self._cur.execute(swapped, params)

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def __getattr__(self, name):
        """Delegate any other attribute/method access to the real cursor."""
        return getattr(self._cur, name)


# ---------------------------------------------------------------------------
# Day 034 Exercise 2: Transaction-aware db_transaction fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def db_transaction(db_helper: DatabaseHelper):
    """
    Day 034 Exercise 2: Demonstrate the BEGIN -> Test -> ROLLBACK pattern.

    Instead of TRUNCATE (physical deletion after the test), this fixture
    wraps the entire test in a single database transaction that is always
    rolled back at the end — whether the test passes or fails.

    Mental model:
      BEGIN          <- fixture setup (autocommit=False)
        |
      Test body runs SQL on this connection
        |
      ROLLBACK       <- fixture teardown (always, even on failure)

    Advantages over TRUNCATE:
      - No committed data reaches disk — rollback is pure memory work.
      - Faster for write-heavy tests (no I/O flush + no index maintenance).
      - Leaves the table in bit-for-bit identical state to before the test.

    Limitation in this project:
      The production repository uses execute_write_transaction() which opens
      its OWN internal transaction and commits before returning.  Those
      commits are independent of this outer connection and cannot be undone
      by rolling back a separate connection.  This fixture demonstrates the
      PATTERN on raw connections; the conceptual lesson is the same.

    Yields: a psycopg connection with autocommit=False (open transaction).
    """
    with db_helper._pool.connection() as conn:
        # autocommit=False means BEGIN is implicit on the first statement.
        conn.autocommit = False
        yield conn
        # TEARDOWN: always roll back — discards all changes from the test.
        conn.rollback()


# ---------------------------------------------------------------------------
# Day 033 Exercise 7: Core integration tests (5 tests)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestIntegrationStudentRepository:
    """
    Day 033 Exercise 7: Real repository against real (isolated) table.

    Day 035 Exercise 2: @pytest.mark.integration -> run with `pytest -m integration -v`.
    Requires a local PostgreSQL connection; auto-skipped if DB is not reachable.

    Proves:
      - SQL INSERT is correct and returns the assigned id.
      - SQL SELECT by id finds the persisted row.
      - SQL SELECT for a missing id returns None (not an exception).
      - SQL DELETE removes the row and returns True.
      - SQL SELECT * returns all rows in id order.
    """

    def test_add_and_retrieve_student(self, repo: PostgresStudentRepository):
        """Full round-trip: INSERT then SELECT proves persistence end-to-end."""
        # ARRANGE
        student_data = Student_model(
            name="Integration Alice", age=23,
            city="Bangalore", email="integ.alice@example.com",
        )

        # ACT
        created = repo.add_student(student_data)

        # ASSERT — returned model has a valid id
        assert created.id is not None and created.id >= 1
        assert created.name == "Integration Alice"

        # Retrieve by id to confirm persistence
        fetched = repo.get_student_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.email == "integ.alice@example.com"

    def test_get_student_by_id_returns_none_when_not_found(
        self, repo: PostgresStudentRepository
    ):
        """
        Querying a non-existent id must return None (not raise).

        Repository contract: None -> Service raises StudentNotFoundException.
        The service behaviour is tested separately in unit tests.
        """
        assert repo.get_student_by_id(99999) is None

    def test_get_all_students_returns_inserted_records(
        self, repo: PostgresStudentRepository
    ):
        """All inserted students appear in get_all_students(), ordered by id."""
        repo.add_student(Student_model(
            name="Bob Integration", age=20, city="Mumbai",
            email="bob.integ@example.com",
        ))
        repo.add_student(Student_model(
            name="Carol Integration", age=21, city="Delhi",
            email="carol.integ@example.com",
        ))

        all_students = repo.get_all_students()

        assert len(all_students) == 2
        assert all_students[0].id < all_students[1].id   # ordered by id
        names = {s.name for s in all_students}
        assert "Bob Integration" in names
        assert "Carol Integration" in names

    def test_delete_student_returns_true_and_removes_record(
        self, repo: PostgresStudentRepository
    ):
        """Deleting an existing student returns True and makes it unreachable."""
        created = repo.add_student(Student_model(
            name="Dave Integration", age=24, city="Hyderabad",
            email="dave.integ@example.com",
        ))
        assert repo.delete_student(created.id) is True
        assert repo.get_student_by_id(created.id) is None

    def test_delete_nonexistent_student_returns_false(
        self, repo: PostgresStudentRepository
    ):
        """
        Deleting a non-existent student returns False (not raise).

        The service layer converts False to StudentNotFoundException.
        """
        assert repo.delete_student(99999) is False


# ---------------------------------------------------------------------------
# Day 034 Exercise 4: Constraint failure tests (2 tests)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestConstraintFailures:
    """
    Day 034 Exercise 4: Prove that PostgreSQL constraints are enforced.

    A MagicMock can NEVER verify that a DB constraint exists.
    Only a real PostgreSQL round-trip can prove it.

    Flow:
      Repository
        |
      SQL (INSERT with duplicate / conflicting key)
        |
      PostgreSQL constraint check
        |
      psycopg raises UniqueViolation (subclass of IntegrityError)
        |
      Repository logs and re-raises
        |
      Test catches with pytest.raises
    """

    def test_duplicate_email_raises_exception(
        self, repo: PostgresStudentRepository
    ):
        """
        Exercise 4: Inserting a student with a duplicate email must fail.

        Schema:  email VARCHAR(255) NOT NULL UNIQUE

        Expected behaviour:
          First insert  -> succeeds (row created)
          Second insert -> PostgreSQL raises UniqueViolation
          Repository    -> logs and re-raises
          Test          -> catches with pytest.raises
        """
        # ARRANGE: insert a student with a specific email
        repo.add_student(Student_model(
            name="Email Owner", age=22, city="Mumbai",
            email="duplicate@example.com",
        ))

        # ACT + ASSERT: same email must raise
        with pytest.raises(Exception) as exc_info:
            repo.add_student(Student_model(
                name="Duplicate Email", age=25, city="Delhi",
                email="duplicate@example.com",   # UNIQUE violation
            ))

        # psycopg raises psycopg.errors.UniqueViolation (subclass of IntegrityError).
        # Error messages vary by psycopg version so check for known keywords.
        error_msg = str(exc_info.value).lower()
        assert any(k in error_msg for k in ["unique", "duplicate", "violat", "constraint"])

    def test_duplicate_primary_key_raises_exception(
        self, db_helper: DatabaseHelper
    ):
        """
        Exercise 4: Inserting a row with a duplicate PRIMARY KEY must fail.

        We bypass the repository's auto-ID logic and insert id=1 twice,
        proving the DB-level PRIMARY KEY constraint is active independently
        of application-layer ID generation.
        """
        # Insert row with id=1 via raw connection
        with db_helper._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {TEST_TABLE} (id, name, age, city, email) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (1, "PK Owner", 20, "Chennai", "pk.owner@example.com"),
                )
            conn.commit()

        # Insert another row with the same id=1 — must fail
        with pytest.raises(Exception) as exc_info:
            with db_helper._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"INSERT INTO {TEST_TABLE} (id, name, age, city, email) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (1, "PK Dup", 21, "Pune", "pk.dup@example.com"),
                    )
                conn.commit()

        error_msg = str(exc_info.value).lower()
        assert any(k in error_msg for k in ["unique", "duplicate", "violat", "constraint"])


# ---------------------------------------------------------------------------
# Day 034 Exercise 5: Transaction rollback verification (2 tests)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestTransactionRollback:
    """
    Day 034 Exercise 5: Prove that a rolled-back transaction leaves no trace.

    Mental model:
      Before  -> Student A does not exist
      BEGIN   -> open transaction (autocommit=False)
      INSERT A -> row inserted (not committed yet)
      Error   -> exception raised inside the transaction block
      ROLLBACK -> psycopg context manager auto-rolls back
      After   -> Student A still does not exist

    This is the practical meaning of Atomicity (A in ACID):
    either ALL operations commit or NONE do.
    """

    def test_rollback_on_error_leaves_no_data(
        self, db_helper: DatabaseHelper
    ):
        """
        Exercise 5: A transaction that raises is rolled back automatically.

        When a 'with pool.connection()' block exits with an active exception,
        psycopg automatically issues ROLLBACK before returning the connection
        to the pool.

        Steps:
          1. Open connection with autocommit=False (BEGIN implicit).
          2. INSERT a row.
          3. Raise an exception BEFORE commit.
          4. psycopg issues ROLLBACK.
          5. Verify row is absent using a FRESH connection.
        """
        rollback_email = "rollback.test@example.com"

        try:
            with db_helper._pool.connection() as conn:
                conn.autocommit = False
                with conn.cursor() as cur:
                    cur.execute(
                        f"INSERT INTO {TEST_TABLE} (id, name, age, city, email) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (999, "Rollback Student", 30, "Test City", rollback_email),
                    )
                # Force error BEFORE commit — triggers ROLLBACK
                raise RuntimeError("Intentional error to trigger rollback")
        except RuntimeError:
            pass  # expected — rollback happened automatically

        # Query with a FRESH connection to see what is actually committed
        with db_helper._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT id FROM {TEST_TABLE} WHERE email = %s",
                    (rollback_email,),
                )
                row = cur.fetchone()

        # Row must NOT exist — ROLLBACK erased the INSERT
        assert row is None, (
            f"ROLLBACK failed: student '{rollback_email}' found after rollback."
        )

    def test_committed_data_survives(self, db_helper: DatabaseHelper):
        """
        Exercise 5 (contrast): A committed transaction IS visible afterward.

        This proves the rollback test is meaningful — INSERTs do work when
        committed, so an absent row after rollback is a genuine ROLLBACK.
        """
        commit_email = "committed.test@example.com"

        # INSERT and COMMIT
        with db_helper._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {TEST_TABLE} (id, name, age, city, email) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (888, "Committed Student", 28, "Commit City", commit_email),
                )
            conn.commit()

        # Row IS visible on a fresh connection
        with db_helper._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT id FROM {TEST_TABLE} WHERE email = %s",
                    (commit_email,),
                )
                row = cur.fetchone()

        assert row is not None, (
            f"Commit did not persist: '{commit_email}' not found after COMMIT."
        )
        assert row[0] == 888


# ---------------------------------------------------------------------------
# Day 034 Exercise 7: Atomicity — partial write in a failed transaction
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestAtomicity:
    """
    Day 034 Exercise 7: Partial writes inside a failed transaction do NOT persist.

    Scenario:
      Transaction
        |
      INSERT student A (valid — succeeds within transaction)
        |
      INSERT student B (UNIQUE violation — raises exception)
        |
      Exception -> psycopg ROLLBACK (context manager)
        |
      Result: neither A nor B remains in the database

    This is the strongest practical demonstration of Atomicity.
    Either ALL operations commit or NONE do — there is no partial state.
    """

    def test_partial_write_is_rolled_back(self, db_helper: DatabaseHelper):
        """
        Exercise 7: Inserting A then failing on B rolls back BOTH.

        Student A is inserted successfully.  Student B has the same email
        as A (UNIQUE violation).  The entire multi-step operation is
        atomic — since B fails, A is also absent after automatic rollback.
        """
        email_a = "atomic.a@example.com"
        email_b = email_a   # same email -> UNIQUE violation on second INSERT

        try:
            with db_helper._pool.connection() as conn:
                conn.autocommit = False
                with conn.cursor() as cur:
                    # Step 1: Insert A — succeeds in isolation
                    cur.execute(
                        f"INSERT INTO {TEST_TABLE} (id, name, age, city, email) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (101, "Atomic A", 22, "City A", email_a),
                    )
                    # Step 2: Insert B with same email — raises UniqueViolation.
                    # psycopg rolls back the entire transaction when the
                    # 'with conn' block exits with an active exception.
                    cur.execute(
                        f"INSERT INTO {TEST_TABLE} (id, name, age, city, email) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (102, "Atomic B", 23, "City B", email_b),
                    )
                conn.commit()
        except Exception:
            pass  # UniqueViolation expected — auto rollback happened

        # ASSERT: A is ALSO absent (the rollback was atomic)
        with db_helper._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT COUNT(*) FROM {TEST_TABLE} WHERE id IN (101, 102)"
                )
                row = cur.fetchone()

        assert row[0] == 0, (
            f"Atomicity violated: found {row[0]} row(s) after a failed "
            "transaction — ROLLBACK should have erased all inserts."
        )


# ---------------------------------------------------------------------------
# Day 034 Exercise 2: db_transaction fixture demonstration (2 tests)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestTransactionAwareFixture:
    """
    Day 034 Exercise 2: Demonstrate BEGIN -> Test -> ROLLBACK via db_transaction.

    The fixture yields a connection with autocommit=False.
    All SQL on that connection participates in the open transaction.
    Fixture teardown always calls rollback() — data is automatically discarded.

    Limitation: the production repository creates its OWN internal transactions
    (via execute_write_transaction + conn.transaction()) that commit independently.
    This fixture demonstrates the pattern on raw connections; the lesson is the same.
    """

    def test_db_transaction_rolls_back(
        self, db_helper: DatabaseHelper, db_transaction
    ):
        """
        Exercise 2: Data inserted on the transaction connection is rolled back.

        Within the test, the row is visible on the SAME connection
        (within-transaction read).  After teardown (rollback()), it is gone.
        """
        email = "tx.fixture@example.com"

        # INSERT on the transaction connection (not yet committed)
        with db_transaction.cursor() as cur:
            cur.execute(
                f"INSERT INTO {TEST_TABLE} (id, name, age, city, email) "
                "VALUES (%s, %s, %s, %s, %s)",
                (500, "TX Fixture Student", 25, "TX City", email),
            )

        # Visible within the SAME open transaction
        with db_transaction.cursor() as cur:
            cur.execute(
                f"SELECT id FROM {TEST_TABLE} WHERE email = %s", (email,)
            )
            row = cur.fetchone()
        assert row is not None, "Row should be visible within the open transaction"

        # After this test returns, db_transaction teardown calls rollback().
        # clear_test_table also TRUNCATES before the next test (belt-and-suspenders).

    def test_after_rollback_row_is_gone(
        self, db_helper: DatabaseHelper
    ):
        """
        Exercise 2 (follow-up): The row from the previous test is gone.

        Either rolled back by the db_transaction fixture or truncated by
        clear_test_table — either way, the table is empty here.
        """
        with db_helper._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT id FROM {TEST_TABLE} WHERE email = %s",
                    ("tx.fixture@example.com",),
                )
                row = cur.fetchone()

        assert row is None   # rolled back or truncated


# ---------------------------------------------------------------------------
# Day 034 Exercise 9: Failure cleanup drill (2 tests)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFailureCleanupDrill:
    """
    Day 034 Exercise 9: Fixture teardown runs even when a test raises.

    Procedure:
      1. Insert a row in a test that (conceptually) raises RuntimeError.
      2. The clear_test_table autouse fixture TRUNCATES before the NEXT test.
      3. The next test confirms the table is empty — cleanup always occurs.

    This is why pytest fixtures are used for teardown rather than inline
    try/finally: pytest guarantees teardown code runs even on test failure.
    """

    def test_insert_then_raise(self, repo: PostgresStudentRepository):
        """
        Exercise 9: Insert a row, confirm it exists, then (optionally) raise.

        The TRUNCATE before the next test cleans up regardless.
        Uncomment the raise to observe cleanup behavior — the suite stays
        green because the cleanup is fixture-driven, not test-driven.
        """
        created = repo.add_student(Student_model(
            name="Crash Student", age=20, city="Crashville",
            email="crash@example.com",
        ))
        # Confirm the row exists inside this test
        assert repo.get_student_by_id(created.id) is not None

        # Uncomment to observe that teardown still runs:
        # raise RuntimeError("intentional failure — clear_test_table still runs")

    def test_cleanup_ran_after_previous_test(
        self, repo: PostgresStudentRepository
    ):
        """
        Exercise 9 (follow-up): The TRUNCATE cleared the row from the
        previous test.  Table must be empty at the start of this test.
        """
        all_students = repo.get_all_students()
        assert len(all_students) == 0, (
            f"Expected empty table after fixture teardown, "
            f"found {len(all_students)} row(s)."
        )


# ---------------------------------------------------------------------------
# Day 034 Exercise 10: Test suite isolation — order independence (3 tests)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestSuiteIsolation:
    """
    Day 034 Exercise 10: Prove that tests are order-independent.

    A suite where A->B passes but B->A fails has an isolation problem.
    The clear_test_table autouse fixture (TRUNCATE before each test)
    makes execution order irrelevant.

    Each test independently:
      1. Starts with an empty table (guaranteed by clear_test_table).
      2. Inserts its own data.
      3. Asserts on that data only.
      4. Leaves without explicit cleanup (next TRUNCATE handles it).
    """

    def test_isolation_a(self, repo: PostgresStudentRepository):
        """Isolation A: Insert one student, verify exactly one exists."""
        repo.add_student(Student_model(
            name="Isolation A", age=20, city="City A", email="iso.a@example.com"
        ))
        students = repo.get_all_students()
        # Must see EXACTLY the one student from THIS test — not leftovers.
        assert len(students) == 1
        assert students[0].name == "Isolation A"

    def test_isolation_b(self, repo: PostgresStudentRepository):
        """Isolation B: Insert two students, verify exactly two exist."""
        repo.add_student(Student_model(
            name="Isolation B1", age=21, city="City B", email="iso.b1@example.com"
        ))
        repo.add_student(Student_model(
            name="Isolation B2", age=22, city="City B", email="iso.b2@example.com"
        ))
        students = repo.get_all_students()
        # Must see EXACTLY the two students from THIS test.
        assert len(students) == 2
        names = {s.name for s in students}
        assert "Isolation B1" in names and "Isolation B2" in names

    def test_isolation_c_starts_empty(self, repo: PostgresStudentRepository):
        """Isolation C: Insert nothing — verify the table is empty."""
        students = repo.get_all_students()
        # If isolation works, the table is empty at the start of every test.
        # No data from tests A or B should be visible here.
        assert len(students) == 0, (
            f"Isolation failure: expected empty table, "
            f"found {len(students)} row(s) from a previous test."
        )
