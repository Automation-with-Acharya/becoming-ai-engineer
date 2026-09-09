# Day 34: Database Integration Testing Exercises

## Exercise 1: Inspect the Current Integration Test Strategy

Open [`tests/integration/test_student_repository.py`](tests/integration/test_student_repository.py).

From Day 33, you already created `test_students` as an isolated table.

Inspect the following:

- How is it created?
- When is it cleared?
- Who owns the cleanup?
- What happens if a test fails?

Document the current lifecycle:

```text
Session Start
	|
Create test table
	|
Test
	|
TRUNCATE / cleanup
	|
Next Test
	|
Session End
	|
Drop test table
```

## Exercise 2: Add a Transaction-Aware Fixture

Create a practice fixture that conceptually manages database state:

```python
@pytest.fixture
def db_transaction(...):
	...
```

The desired mental model is:

```text
BEGIN
  |
Test
  |
ROLLBACK
```

This means test-created data disappears automatically.

Do not force this directly into every existing test if your current `DatabaseHelper` abstraction does not yet support the cleanest version.

The objective is to understand the pattern.

## Exercise 3: Compare `TRUNCATE` vs. `ROLLBACK`

Your existing Day 33 integration tests use table cleanup. Reason about these two strategies:

### Strategy A

```text
INSERT
DELETE / TRUNCATE
```

### Strategy B

```text
BEGIN
INSERT
ROLLBACK
```

Create a short comparison document with the following columns:

| Approach   | How it works | Advantages | Limitations | When I would use it |
| ---------- | ------------ | ---------- | ----------- | ------------------- |
| `TRUNCATE` |              |            |             |                     |
| `ROLLBACK` |              |            |             |                     |

The important insight is:

```text
TRUNCATE
	|
Physical test-data cleanup

ROLLBACK
	|
Transactional state reset
```

Neither strategy is automatically correct for every test architecture.

## Exercise 4: Test a Constraint Failure

Use the real PostgreSQL repository integration setup.

Your `students` table has constraints. Create a test that intentionally violates one.

For example, depending on your exact schema:

- Duplicate email
- `NULL` in a required column
- Duplicate primary key

The test should verify that the repository or database raises the expected failure.

The important flow is:

```text
Repository
	|
SQL
	|
PostgreSQL constraint
	|
Database error
	|
Repository logs and propagates
```

You are testing real database behavior here. A `MagicMock` cannot prove that a database constraint exists.

## Exercise 5: Verify Transaction Rollback

Create a controlled database experiment:

```text
BEGIN
	|
INSERT student A
	|
Force an error
	|
ROLLBACK
```

Then run a query such as:

```sql
SELECT ...;
```

Confirm that Student A does not remain.

The mental model is:

```text
Before
  `-- A does not exist

BEGIN
  `-- Insert A

Failure
  `-- ROLLBACK

After
  `-- A still does not exist
```

This is the practical meaning of atomicity.

## Exercise 6: Test the Repository Transaction Boundary

Your existing repository already has transaction-aware writes from Day 20.

Inspect:

- `add_student()`
- `delete_student()`

Then answer: What exact operations belong inside the same transaction?

For example:

```text
add_student
	|
Calculate ID
	|
INSERT
```

These operations need to be considered together because the result of the first operation feeds the second.

The architectural connection is:

```text
Business operation
	|
Repository transaction boundary
	|
Atomic database work
```

## Exercise 7: Test Failure During a Write

This is an important experiment. Conceptually create:

```text
Transaction
	|
Valid operation
	|
Invalid operation
	|
Exception
	|
Rollback
```

Then verify that the earlier successful operation did not remain committed.

This is the strongest practical demonstration of atomicity.

## Exercise 8: Observe the Difference Between Unit and Integration Tests

Compare the following:

### Unit test

```text
StudentService
	|
MagicMock Repository
	|
No database
```

### Integration test

```text
PostgresStudentRepository
	|
DatabaseHelper
	|
PostgreSQL
```

Answer the following:

- Which test can detect a bad SQL query? **Integration test.**
- Which test can detect a wrong business rule without requiring PostgreSQL? **Unit test.**
- Which test can verify PostgreSQL constraints? **Integration test.**
- Which test is likely to run fastest? **Unit test.**

This is why a mature backend needs both.

## Exercise 9: Failure Cleanup Drill

Intentionally create a test that raises an exception after inserting data.

For example:

```python
repo.add_student(...)
raise RuntimeError("intentional test failure")
```

Then determine:

- Does the inserted record remain?
- Does cleanup still happen?

This will teach you why fixture teardown is so important.

The goal is not to keep a broken test. Fix it immediately after observing the behavior.

## Exercise 10: Test Suite Isolation

Run:

```bash
pytest -v
```

Then run:

```bash
pytest -v tests/integration/
```

Run the integration tests in a different order where practical.

The key question is: Does the result depend on test execution order?

It should not.

A test suite where Test A followed by Test B works, but Test B followed by Test A fails, has an isolation problem.
