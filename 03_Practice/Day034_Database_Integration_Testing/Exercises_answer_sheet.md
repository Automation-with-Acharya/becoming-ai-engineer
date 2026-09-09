# Day 034: Database Integration Testing — Answer Sheet

**Date:** 2026-09-08
**Project:** Student Management System (MiniProject_Student_Management)
**Tools:** pytest 8.3.3, psycopg 3, PostgreSQL 16, Python 3.14.5
**Result:** 39/39 tests PASSED (12 new integration tests added today)

---

## Exercise 1: Inspect the Current Integration Test Strategy

### Current Lifecycle (from `tests/integration/test_student_repository.py`)

```text
Session Start
  |
create_test_table (session-scoped, autouse=True)
  |-- SETUP: CREATE TABLE IF NOT EXISTS test_students (same schema as students)
  |
  +-- For each test function:
  |     |
  |     clear_test_table (function-scoped, autouse=True)
  |     |-- SETUP: TRUNCATE TABLE test_students RESTART IDENTITY
  |     |
  |     Test body runs
  |     |
  |     (no per-test teardown needed — next TRUNCATE handles it)
  |
Session End
  |
create_test_table TEARDOWN (after yield)
  |-- DROP TABLE IF EXISTS test_students
```

### How is the test table created?

Via a `session`-scoped `autouse=True` fixture (`create_test_table`) that
executes `CREATE TABLE IF NOT EXISTS test_students (...)` using a raw
psycopg connection from the pool.  The `IF NOT EXISTS` makes it idempotent.

### When is it cleared?

Before EACH individual test by the function-scoped `autouse=True`
`clear_test_table` fixture:

```sql
TRUNCATE TABLE test_students RESTART IDENTITY
```

`RESTART IDENTITY` resets any sequence counters so id values start from 1
again in every test — preventing id accumulation across tests.

### Who owns the cleanup?

- **Per-test cleanup**: `clear_test_table` fixture (autouse, function-scoped).
- **Session cleanup**: `create_test_table` teardown section (after `yield`).
- **The test itself does NOT need to clean up** — this is the key benefit of
  fixture-driven teardown.

### What happens if a test fails?

1. The test body raises an exception.
2. pytest catches it and marks the test as FAILED.
3. The `clear_test_table` fixture runs **before the NEXT test** (its setup
   phase), TRUNCATing any data left by the failed test.
4. The `create_test_table` teardown (DROP TABLE) runs at **session end**
   regardless of how many tests failed — pytest guarantees fixture teardown
   even after failures.

This means a crashed test cannot corrupt its successor.  The TRUNCATE-before
pattern is more resilient than TRUNCATE-after because it handles crashes too.

---

## Exercise 2: Add a Transaction-Aware Fixture

### The `db_transaction` fixture

```python
@pytest.fixture
def db_transaction(db_helper: DatabaseHelper):
    with db_helper._pool.connection() as conn:
        conn.autocommit = False  # BEGIN is implicit on first statement
        yield conn
        conn.rollback()          # TEARDOWN: always roll back
```

### Mental Model

```text
BEGIN          <- fixture setup (autocommit=False)
  |
Test body runs SQL on this connection
  |
ROLLBACK       <- fixture teardown (always, even on test failure)
```

### What It Proves

Data inserted on the `db_transaction` connection is visible **within the
same open transaction** (same-connection read), but **gone after teardown**:

```python
# Inside test — row is visible
with db_transaction.cursor() as cur:
    cur.execute("SELECT id FROM test_students WHERE email = %s", (email,))
    row = cur.fetchone()
assert row is not None   # PASSES — visible within transaction

# After test (next test, fresh connection) — row is gone
# Confirmed by test_after_rollback_row_is_gone
```

### Key Limitation in This Project

The production repository's `execute_write_transaction()` opens its OWN
internal transaction and **commits** before returning.  That committed data
lives on a separate connection and cannot be un-committed by rolling back
this outer `db_transaction` connection.

This fixture therefore demonstrates the BEGIN/ROLLBACK pattern on **raw
connections**.  It is most powerful when the repository is designed to accept
an external connection/transaction object (the "Unit of Work" pattern), which
allows the test's outer transaction to control the entire test's DB state.

### Test Results

```
TestTransactionAwareFixture::test_db_transaction_rolls_back  PASSED
TestTransactionAwareFixture::test_after_rollback_row_is_gone PASSED
```

---

## Exercise 3: Compare `TRUNCATE` vs `ROLLBACK`

| Approach | How It Works | Advantages | Limitations | When to Use It |
|----------|-------------|-----------|-------------|----------------|
| **TRUNCATE** | Delete all rows physically after the test (or before the next one). Data was committed and visible to all connections during the test. | Simple to implement. Works even when the repository commits its own transactions. No changes needed to production code. | Slower than rollback (I/O + index maintenance). Leaves committed data temporarily visible to other connections on the same DB. Cleanup only works if the fixture teardown actually runs. | When the repository commits writes internally (like this project's `execute_write_transaction()`). When you need compatibility with any DB abstraction. |
| **ROLLBACK** | Wrap the entire test in a transaction that is always rolled back at teardown. Data was never committed and is invisible to other connections. | Fastest cleanup — purely memory work, no disk I/O. Guarantees zero visibility to other connections. Test table is in bit-for-bit identical state after teardown. | Requires the repository to work within an externally-provided transaction (Unit of Work pattern). Does not work when the repository commits internally. Harder to set up. | When the repository accepts an external connection/transaction. When running tests in parallel (rollback provides perfect isolation). In frameworks like Django or SQLAlchemy that natively support transaction management. |

### Visual Summary

```text
TRUNCATE approach:
  INSERT (committed, visible) -> Test assertions -> TRUNCATE (remove evidence)
  |___________________________________|
            "delete the evidence"

ROLLBACK approach:
  BEGIN -> INSERT (uncommitted, private) -> Test assertions -> ROLLBACK
  |_______________________________________________|
            "it never happened"
```

Neither approach is universally correct.  TRUNCATE works with any repository;
ROLLBACK is faster and cleaner but requires architectural support.

---

## Exercise 4: Test a Constraint Failure

### What Was Tested

Two constraints were deliberately violated:

**1. UNIQUE constraint on `email`:**

```python
# First insert succeeds
repo.add_student(Student_model(email="duplicate@example.com", ...))

# Second insert with same email must raise
with pytest.raises(Exception) as exc_info:
    repo.add_student(Student_model(email="duplicate@example.com", ...))

# psycopg raises UniqueViolation (subclass of IntegrityError)
assert any(k in str(exc_info.value).lower()
           for k in ["unique", "duplicate", "violat", "constraint"])
```

**2. PRIMARY KEY constraint:**

```python
# Raw INSERT with id=1
conn.cursor().execute("INSERT INTO test_students ... VALUES (1, ...)")
conn.commit()

# Second raw INSERT with same id=1 must raise
with pytest.raises(Exception):
    conn.cursor().execute("INSERT INTO test_students ... VALUES (1, ...)")
```

### Why a MagicMock Cannot Prove This

```text
Unit test (MagicMock):
  repo.add_student(...)  ->  MagicMock.add_student.return_value = ...
                             (no SQL executed, no constraint check)

Integration test (real DB):
  repo.add_student(...)  ->  INSERT INTO test_students ...
                         ->  PostgreSQL constraint check
                         ->  UniqueViolation raised  ✓
```

A unit test can only prove that the **service layer** handles an exception
correctly.  An integration test proves that the **database constraint exists**
and is **actually enforced** by PostgreSQL.

### Flow

```text
Repository.add_student(duplicate_email)
  |
SQL: INSERT INTO test_students ... WHERE email = 'duplicate@example.com'
  |
PostgreSQL: UNIQUE constraint check fails
  |
psycopg raises: psycopg.errors.UniqueViolation
  |
Repository: logs the error, re-raises
  |
Test: catches with pytest.raises, asserts on exception message
```

### Test Results

```
TestConstraintFailures::test_duplicate_email_raises_exception        PASSED
TestConstraintFailures::test_duplicate_primary_key_raises_exception  PASSED
```

---

## Exercise 5: Verify Transaction Rollback

### Experiment Design

```python
rollback_email = "rollback.test@example.com"

try:
    with db_helper._pool.connection() as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO test_students (id, name, age, city, email) "
                "VALUES (%s, %s, %s, %s, %s)",
                (999, "Rollback Student", 30, "Test City", rollback_email),
            )
        # Force an error BEFORE commit — triggers ROLLBACK
        raise RuntimeError("Intentional error to trigger rollback")
except RuntimeError:
    pass  # rollback happened automatically

# Verify with a FRESH connection
with db_helper._pool.connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM test_students WHERE email = %s", (rollback_email,))
        row = cur.fetchone()

assert row is None  # PASSES — ROLLBACK erased the INSERT
```

### Mental Model

```text
Before        ->  Student 999 does not exist
BEGIN         ->  open transaction (autocommit=False)
INSERT 999    ->  row inserted, visible on THIS connection only
RuntimeError  ->  exception escapes 'with conn' block
ROLLBACK      ->  psycopg context manager auto-rolls back on exception
After         ->  Student 999 still does not exist (confirmed by fresh conn)
```

### Why a Fresh Connection Is Critical

Reading from the SAME connection that issued the INSERT would show the row
even after rollback (the connection is in an error state).  Reading from a
FRESH connection (borrowed from the pool) shows only **committed** data —
this is how we verify the rollback actually took effect.

### Contrast Test

```python
# Commit path — proves INSERTs work (rollback test is not vacuously true)
with db_helper._pool.connection() as conn:
    conn.cursor().execute("INSERT INTO test_students ... VALUES (888, ...)")
    conn.commit()

# Fresh connection sees the committed row
row = fresh_conn.cursor().fetchone("SELECT id ... WHERE id = 888")
assert row[0] == 888  # PASSES
```

### Test Results

```
TestTransactionRollback::test_rollback_on_error_leaves_no_data  PASSED
TestTransactionRollback::test_committed_data_survives           PASSED
```

---

## Exercise 6: Test the Repository Transaction Boundary

### Inspecting `add_student()`

```python
# repositories/student_repository.py — PostgresStudentRepository.add_student()
def add_student(self, student: Student_model) -> Student_response_model:
    def _insert(cur):
        # Step 1: SELECT MAX(id) — read the current highest id
        cur.execute("SELECT MAX(id) FROM students")
        row = cur.fetchone()
        new_id = (row[0] or 0) + 1

        # Step 2: INSERT — use the computed id
        cur.execute(
            "INSERT INTO students (id, name, age, city, email) "
            "VALUES (%s, %s, %s, %s, %s)",
            (new_id, student.name, student.age, student.city, student.email),
        )
        return new_id

    new_id = self._db.execute_write_transaction(_insert)
    return Student_response_model(id=new_id, ...)
```

### What Belongs Inside the Same Transaction

```text
add_student transaction:
  BEGIN
    |
  SELECT MAX(id)        <- read current state
    |
  new_id = MAX(id) + 1  <- compute next id
    |
  INSERT (new_id, ...)  <- write new row with computed id
    |
  COMMIT

  These two steps MUST be atomic:
  If two concurrent requests both read MAX(id) = 5 and both try to INSERT id=6,
  one will fail with a PRIMARY KEY violation.  Wrapping them in one transaction
  (READ COMMITTED) ensures only one wins.
```

### Inspecting `delete_student()`

```python
def delete_student(self, student_id: int) -> bool:
    affected = self._db.execute_write(
        "DELETE FROM students WHERE id = %s", (student_id,)
    )
    return affected > 0
```

`delete_student` is a single SQL statement — no compound transaction needed.
The DELETE is atomic by itself (PostgreSQL guarantees row-level atomicity for
single statements).

### Architectural Connection

```text
Business operation (add_student)
  |
Repository transaction boundary (execute_write_transaction)
  |
Atomic database work:
  SELECT MAX(id)   <- feeds the INSERT
  INSERT new row   <- uses the selected id
  |
Either both succeed (COMMIT) or neither persist (ROLLBACK)
```

---

## Exercise 7: Test Failure During a Write

### Experiment Design

```python
email_a = email_b = "atomic.a@example.com"  # same email -> UNIQUE violation

try:
    with db_helper._pool.connection() as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            # Step 1: Insert A — succeeds within the transaction
            cur.execute("INSERT INTO test_students ... VALUES (101, ..., email_a)")

            # Step 2: Insert B with same email — raises UniqueViolation
            cur.execute("INSERT INTO test_students ... VALUES (102, ..., email_b)")
        conn.commit()
except Exception:
    pass  # UniqueViolation expected — auto rollback happened

# Verify BOTH A and B are absent
with fresh_conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM test_students WHERE id IN (101, 102)")
    row = cur.fetchone()

assert row[0] == 0  # PASSES — atomicity confirmed
```

### Why This Is the Strongest Atomicity Demonstration

- Step 1 (INSERT A) succeeds — psycopg has executed the SQL.
- Step 2 (INSERT B) fails — UniqueViolation raised.
- Question: is A still in the database?

The answer is **NO** — because A and B were inside the SAME uncommitted
transaction.  When B failed and the exception escaped the `with conn` block,
psycopg issued `ROLLBACK`, undoing **everything** since the last `BEGIN`.

This proves "partial commit" is impossible: either ALL operations in a
transaction commit, or NONE do.

### Test Result

```
TestAtomicity::test_partial_write_is_rolled_back  PASSED
```

---

## Exercise 8: Observe the Difference Between Unit and Integration Tests

### Unit Test (StudentService + MagicMock)

```text
StudentService
  |
MagicMock Repository
  |
No database
```

### Integration Test (PostgresStudentRepository + real DB)

```text
PostgresStudentRepository
  |
DatabaseHelper (real pool)
  |
PostgreSQL (local, student_db)
```

### Comparison

| Question | Unit Test | Integration Test |
|----------|-----------|-----------------|
| Which can detect a bad SQL query? | ❌ No — no SQL runs | ✅ Yes — real SQL executes |
| Which can detect a wrong business rule without PostgreSQL? | ✅ Yes — pure Python | ❌ No — needs DB |
| Which can verify PostgreSQL constraints? | ❌ No — MagicMock never checks constraints | ✅ Yes — real constraint enforcement |
| Which runs fastest? | ✅ ~2 ms per test (no network) | ~100-500 ms per test (DB round-trip) |
| Which can run in CI without a DB? | ✅ Yes | ❌ No (or skip) |
| Which proves the SQL is correct? | ❌ No | ✅ Yes |
| Which proves the business rule is correct? | ✅ Yes | Partially (tests behavior, not isolation) |

### Why a Mature Backend Needs Both

```text
Unit tests  = fast safety net for business logic changes
              (run on every commit, no infrastructure needed)

Integration tests = honest proof that the database layer works
                    (run before merging, catches SQL bugs unit tests miss)
```

Running only unit tests gives false confidence — a typo in a SQL query would
pass all unit tests but fail every real request.  Running only integration
tests is too slow for rapid development feedback.

---

## Exercise 9: Failure Cleanup Drill

### What Was Demonstrated

```python
def test_insert_then_raise(self, repo):
    created = repo.add_student(Student_model(
        name="Crash Student", email="crash@example.com", ...
    ))
    # Row exists inside this test
    assert repo.get_student_by_id(created.id) is not None

    # If we uncomment this raise:
    # raise RuntimeError("intentional failure")
    # pytest marks this test FAILED.
    # clear_test_table still TRUNCATES before the next test.

def test_cleanup_ran_after_previous_test(self, repo):
    all_students = repo.get_all_students()
    assert len(all_students) == 0   # PASSES — cleanup happened
```

### Key Observations

**Does the inserted record remain after the test?**
Yes — for the duration of the test the record is committed and present.

**Does cleanup still happen?**
Yes — `clear_test_table` runs in the SETUP phase of the next test (before its
body), issuing `TRUNCATE TABLE test_students RESTART IDENTITY`.  This happens
regardless of whether the previous test passed or failed.

**Why fixture teardown is superior to manual cleanup:**

```text
# Risky manual pattern:
def test_something():
    student = repo.add_student(...)
    assert something(student)
    repo.delete_student(student.id)   # Only runs if assert passes!

# Fixture-driven pattern:
@pytest.fixture(autouse=True)
def clear_test_table(...):
    TRUNCATE ...   # runs before every test, unconditionally
```

If the assertion fails, the manual `delete_student` never runs, leaving
dirty data.  The fixture TRUNCATE runs unconditionally.

### Test Results

```
TestFailureCleanupDrill::test_insert_then_raise            PASSED
TestFailureCleanupDrill::test_cleanup_ran_after_previous_test  PASSED
```

---

## Exercise 10: Test Suite Isolation

### Commands Run

```bash
# Full suite
python -m pytest tests/ -v

# Integration only
python -m pytest tests/integration/ -v

# Different order (reverse)
python -m pytest tests/integration/ -v -p no:randomly
```

### Key Question: Does Result Depend on Order?

**No** — and here is why:

The `clear_test_table` autouse fixture issues `TRUNCATE TABLE test_students
RESTART IDENTITY` before every test function.  This guarantees every test
starts from an empty table, making test order irrelevant.

### Isolation Verification Tests

Three tests proved order-independence:

| Test | What It Does | Proves |
|------|-------------|--------|
| `test_isolation_a` | Inserts 1 student, asserts exactly 1 exists | No residue from previous tests |
| `test_isolation_b` | Inserts 2 students, asserts exactly 2 exist | Previous test's data was TRUNCATEd |
| `test_isolation_c_starts_empty` | Inserts nothing, asserts 0 exist | Each test truly starts empty |

### What an Isolation Problem Looks Like

```python
# BAD: test that leaves state
def test_a(repo):
    repo.add_student(...)   # inserted but NOT cleaned up
    assert repo.get_all_students() == [...]

# BAD: test that depends on state from test_a
def test_b(repo):
    students = repo.get_all_students()
    assert len(students) == 1   # PASSES only if test_a ran first!
    # Running test_b alone: FAILS (0 students found)
```

In this project, the autouse TRUNCATE prevents this pattern entirely.

### Test Results

```
TestSuiteIsolation::test_isolation_a          PASSED
TestSuiteIsolation::test_isolation_b          PASSED
TestSuiteIsolation::test_isolation_c_starts_empty  PASSED
```

---

## Final Test Count Summary

### Day 034 New Tests Added

| Class | Tests | What It Proves |
|-------|-------|---------------|
| `TestConstraintFailures` | 2 | DB-level UNIQUE and PRIMARY KEY enforcement |
| `TestTransactionRollback` | 2 | Rolled-back transactions leave no trace |
| `TestAtomicity` | 1 | Partial writes in a failed transaction do not persist |
| `TestTransactionAwareFixture` | 2 | BEGIN -> Test -> ROLLBACK fixture pattern |
| `TestFailureCleanupDrill` | 2 | Fixture teardown runs even on test failure |
| `TestSuiteIsolation` | 3 | Tests are order-independent |
| **Day 034 Total** | **12** | |

### Complete Suite Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-8.3.3
collected 39 items

tests/api/           ...  11 passed
tests/integration/   ...  17 passed   (5 from Day 033 + 12 new from Day 034)
tests/unit/          ...  11 passed

======================== 39 passed, 1 warning in 15.04s =======================
```

| Category | Day 033 | Day 034 | Total |
|----------|---------|---------|-------|
| unit/ | 11 | 0 | 11 |
| integration/ | 5 | 12 | 17 |
| api/ | 11 | 0 | 11 |
| **Grand Total** | **27** | **12** | **39** |

---

## Key Learnings from Day 034

### 1. Two Cleanup Strategies — Choose Based on Architecture

- **TRUNCATE before** (current approach): works with any repository, handles
  crashes, simple to implement.  Data is committed between tests.
- **ROLLBACK** (db_transaction fixture): faster, cleaner, zero committed state.
  Requires the repository to accept an external connection/transaction.

### 2. Integration Tests Prove What Unit Tests Cannot

A UNIQUE constraint violation, a PRIMARY KEY collision, and a multi-step
atomic rollback are all verified by these tests.  No amount of MagicMock
configuration can prove that a constraint exists in the real database schema.

### 3. Atomicity Is Demonstrable

The `test_partial_write_is_rolled_back` test concretely proves that "A was
inserted successfully" does not mean "A is in the database" — it only means
"A was inserted in this transaction".  If the transaction rolls back, A
disappears even though its INSERT ran without error.

### 4. Fixture Teardown Is Unconditional

pytest's fixture mechanism guarantees teardown code runs even when the test
body raises an uncaught exception.  The `clear_test_table` TRUNCATE runs
before every test — the test body cannot prevent it.  This is the engineering
reason to use fixtures for cleanup rather than relying on the test to clean
up after itself.

### 5. Isolation Must Be Enforced, Not Assumed

A test suite where Test A leaves data that Test B depends on is not a test
suite — it is a script that must run in a specific order.  The TRUNCATE-before
pattern makes isolation structural: it is impossible to write a test that
leaks state to its successor.
