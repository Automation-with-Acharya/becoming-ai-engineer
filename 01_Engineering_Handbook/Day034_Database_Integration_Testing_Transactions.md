# Day 034 — Database Integration Testing & Transaction Safety

**Date:** Tuesday, 8 September 2026  
**Project:** Project ₹50L  
**Phase:** Phase 1 — Core AI/GenAI + Backend Engineering  
**Week:** Week 5 — Advanced SQL, Database Optimization, Repository Improvements & Testing  
**Primary Focus:** Real PostgreSQL integration testing, transaction-aware test isolation, rollback, SAVEPOINT, fixture lifecycle, and repository transaction boundaries

---

## 1. Learning Objectives

By the end of Day 034, the goal is to be able to:

- Explain why database integration tests are different from unit tests.
- Understand how test isolation works when a test touches a real PostgreSQL database.
- Use pytest fixtures to control database test setup and cleanup.
- Compare transaction rollback with table cleanup such as `TRUNCATE`.
- Understand PostgreSQL `SAVEPOINT` and when partial rollback is useful.
- Deliberately trigger database constraint failures and verify the resulting rollback behavior.
- Inspect where the current repository starts and completes its own transactions.
- Recognize when an outer test transaction can and cannot control an application's internal transaction.
- Verify that tests are independent of execution order.
- Connect these testing techniques to production repository and backend architecture.

> **Connection to Day 020:** Day 020 introduced ACID transactions, `COMMIT`, and `ROLLBACK`. Day 034 applies that knowledge to the practical problem of proving transaction behavior through automated integration tests.

---

# 2. The Big Picture

A backend can pass every unit test and still fail in production because the real database behaves differently from a mock.

The important distinction is:

```text
Unit Test
    ↓
Does my Python/business logic behave correctly?

Integration Test
    ↓
Does my repository behave correctly with PostgreSQL?

API Test
    ↓
Does the HTTP/API layer expose the correct behavior?
```

Day 033 established the three testing layers.

Day 034 goes deeper into the integration boundary:

```text
Test
 │
 ├── arrange database state
 │
 ├── execute repository operation
 │
 ├── PostgreSQL applies constraints + transactions
 │
 ├── verify committed / rolled-back state
 │
 └── clean up so the next test starts from a known state
```

The objective is not simply “make tests pass.”

The objective is to make test results trustworthy.

---

# 3. What Makes an Integration Test Different?

## 3.1 Unit Test

A unit test isolates one piece of application logic.

Example:

```python
mock_repository = MagicMock()
service = StudentService(mock_repository)
```

The repository is replaced with a mock.

Advantages:

- very fast
- deterministic
- no database required
- excellent for business-logic behavior

But it does not prove that PostgreSQL accepts the SQL or behaves as expected.

---

## 3.2 Integration Test

An integration test crosses a real system boundary.

For the Student Management project:

```text
StudentRepository
        ↓
   psycopg / DB helper
        ↓
   PostgreSQL
        ↓
   real tables + constraints + transactions
```

This can uncover problems that mocks cannot detect:

- SQL syntax mistakes
- incorrect column names
- constraint violations
- transaction behavior
- incorrect data types
- database-generated behavior
- isolation problems
- repository assumptions that do not match the schema

This is why Day 033's repository tests intentionally connected to a real PostgreSQL database.

---

# 4. Test Isolation — The Core Problem

Suppose Test A inserts a student:

```text
Test A
INSERT student
↓
student remains in DB
```

Then Test B executes:

```sql
SELECT * FROM students;
```

Now Test B may see Test A's data.

That creates a hidden dependency:

```text
Test B depends on Test A
```

This is dangerous because tests can pass when run together but fail individually, or pass on one machine and fail on another.

A good test suite aims for:

```text
Test A ────────┐
               ├── independent outcomes
Test B ────────┤
               │
Test C ────────┘
```

A test should ideally be able to run:

```bash
pytest path/to/test.py
```

or in a different order without changing the result.

---

# 5. Database Isolation Strategies

There are several ways to isolate database tests.

## Strategy A — Cleanup Before/After Tests

Example:

```sql
TRUNCATE TABLE test_students RESTART IDENTITY;
```

The next test starts with a known table state.

Advantages:

- simple
- easy to understand
- works even when application code commits internally

Disadvantages:

- performs database cleanup work
- can become slower for large test suites
- cleanup must be reliable

This is close to the approach already established in the Day 033 integration tests.

---

## Strategy B — Rollback the Test Transaction

Conceptually:

```text
BEGIN
  ↓
run test operations
  ↓
ROLLBACK
```

The database returns to its previous state.

This can be extremely fast and clean when all database writes made by the test happen inside the same transaction controlled by the test fixture.

However, there is an important architectural condition:

> The test can only roll back work that is still part of the transaction it controls.

If the application starts its own transaction and commits it internally, an outer test transaction cannot magically undo that already-committed work.

This distinction is one of the most important lessons of Day 034.

---

## Strategy C — Dedicated Test Database / Schema

Another approach is to run tests against a completely isolated database or schema.

Example:

```text
Production DB
     │
     └── application data

Test DB
     │
     └── integration-test data
```

This greatly reduces the chance of corrupting development or production data.

For larger systems, teams may go further and create disposable databases or containers for test runs.

---

# 6. PostgreSQL Transactions in Testing

A transaction provides an atomic unit of work.

Basic model:

```sql
BEGIN;

INSERT INTO students (...)
VALUES (...);

UPDATE students
SET ...;

COMMIT;
```

Or:

```sql
BEGIN;

INSERT ...;

-- Something goes wrong

ROLLBACK;
```

The important testing question becomes:

> What state should exist after the operation succeeds, and what state should exist after it fails?

Integration tests should verify both.

---

# 7. Testing Rollback Behavior

A useful failure test deliberately causes PostgreSQL to reject an operation.

For example, a unique constraint can be violated:

```sql
INSERT INTO students (id, name, email)
VALUES (1, 'Alice', 'alice@example.com');

INSERT INTO students (id, name, email)
VALUES (1, 'Bob', 'bob@example.com');
```

The second operation should fail if the schema enforces uniqueness for the relevant key.

The test should not stop at:

```python
with pytest.raises(...):
    repository_operation()
```

A stronger integration test also verifies the resulting database state.

For example:

```text
Before
  ↓
known state
  ↓
operation succeeds
  ↓
operation fails
  ↓
rollback
  ↓
verify final state
```

This tests the behavior of the actual database transaction rather than only the Python exception path.

---

# 8. Why Rollback Is Not Automatically a Universal Test-Cleanup Mechanism

It is tempting to think:

```text
Every test = BEGIN + ROLLBACK
```

That is a useful pattern, but it is not universally sufficient.

A transaction cannot automatically undo every side effect in a distributed application.

Examples of side effects that may require different cleanup mechanisms:

```text
Database transaction      → ROLLBACK
Filesystem write          → delete test file
External API call         → mock / sandbox / compensating action
Message published        → test queue / purge / isolation
Background worker         → controlled test lifecycle
External service state   → explicit cleanup or sandbox
```

Therefore:

> Transaction rollback is a database isolation technique, not a universal application-state reset button.

This distinction becomes increasingly important in distributed systems.

---

# 9. SAVEPOINT — Partial Rollback

PostgreSQL also supports `SAVEPOINT` inside a transaction.

Conceptually:

```sql
BEGIN;

INSERT ...;

SAVEPOINT before_risky_operation;

-- risky operation

ROLLBACK TO SAVEPOINT before_risky_operation;

-- continue transaction

COMMIT;
```

This lets a transaction undo part of its work without discarding the entire transaction.

Mental model:

```text
BEGIN
 │
 ├── Operation A
 │
 ├── SAVEPOINT
 │
 ├── Operation B
 │      ↓
 │    failure
 │      ↓
 └── rollback to SAVEPOINT

Continue from here
      ↓
COMMIT
```

SAVEPOINT is especially useful when a larger transaction contains a section that can safely be retried or abandoned.

---

# 10. pytest Fixtures and Test Lifecycle

pytest fixtures are the mechanism used to prepare and clean up test state.

A fixture can provide a database-related resource:

```python
@pytest.fixture
def resource():
    setup()
    yield resource
    cleanup()
```

The key idea is:

```text
setup
  ↓
yield
  ↓
test executes
  ↓
teardown
```

This is especially useful for database integration tests because cleanup should happen even when the test fails.

A conceptual database fixture looks like:

```python
@pytest.fixture
def db_connection():
    connection = create_connection()
    yield connection
    connection.close()
```

The `yield` separates setup from teardown.

---

# 11. Fixture Scope Matters

pytest fixtures can have different scopes.

Common examples:

```text
function  → once per test
class     → once per test class
module    → once per test module
session   → once for the entire test run
```

The choice affects both performance and isolation.

For example:

```text
session fixture
     ↓
create shared test resources once
```

while:

```text
function fixture
     ↓
reset state for every test
```

A practical pattern is often:

```text
Session
  └── create isolated test infrastructure

Function
  └── reset / isolate data for each test
```

The correct scope depends on what is being shared and what must remain independent.

---

# 12. TRUNCATE vs ROLLBACK

Both can help with integration-test isolation, but they solve the problem differently.

| Technique | Core Idea | Strength | Main Caveat |
|---|---|---|---|
| `ROLLBACK` | Undo transaction changes | Fast and elegant | Only works for work inside that transaction |
| `TRUNCATE` | Explicitly clear table data | Simple and robust | Requires cleanup work and controlled access |
| Dedicated test DB/schema | Isolate environment | Strong safety boundary | More infrastructure |
| Disposable database/container | Recreate environment | Very strong isolation | More startup/infrastructure cost |

For the current Student Management project, the existing isolated `test_students` table plus explicit cleanup remains a practical approach.

The important lesson is not that one technique is always superior.

The important lesson is:

> Choose isolation based on where transaction boundaries actually exist.

---

# 13. Transaction Boundaries in the Current Repository

The Student Management repository contains transaction-aware database operations.

The important design question is:

```text
Who owns the transaction?
```

Possibilities include:

```text
Repository owns transaction
Service owns transaction
API/request layer owns transaction
Unit-of-work owns transaction
```

The current repository's write path uses the database helper's transaction-aware operation for `add_student`.

Conceptually:

```text
StudentService
      ↓
PostgresStudentRepository
      ↓
execute_write_transaction(...)
      ↓
PostgreSQL transaction
```

That means the repository/database-helper layer controls when the transaction starts and ends for that operation.

This is precisely why an integration-test author must inspect transaction ownership before attempting an outer rollback fixture.

---

# 14. The Important Test-Transaction Trap

Consider this design:

```text
Test Fixture
BEGIN
   ↓
Repository method
   ↓
Repository opens its own transaction
   ↓
Repository COMMIT
   ↓
Test Fixture ROLLBACK
```

The final rollback cannot undo the repository's already-committed changes.

The misconception is:

```text
Outer ROLLBACK
     ↓
undo everything
```

The actual behavior is closer to:

```text
Outer transaction
     │
     └── repository's independently committed work

Outer ROLLBACK
     ↓
can only undo work still belonging to the outer transaction
```

This is an architectural lesson as much as a testing lesson.

If transaction ownership is not shared, the test cannot assume that a surrounding transaction controls the application operation.

---

# 15. Constraint-Failure Testing

A strong integration test suite should include both successful and unsuccessful database operations.

Examples of useful failure paths:

```text
duplicate key
foreign key violation
NOT NULL violation
invalid data type
missing required record
```

The important pattern is:

```text
Arrange
  ↓
Create valid initial state
  ↓
Act
  ↓
Trigger expected database/application failure
  ↓
Assert exception / API result
  ↓
Assert final database state
```

The final state assertion is what transforms the test from “the code raised an error” into “the system maintained the required data invariant.”

---

# 16. Verifying Test Order Independence

A high-quality integration suite should not depend on execution order.

A useful mental experiment:

```text
Run Test A
Run Test B
Run Test C
```

Then:

```text
Run Test C
Run Test A
Run Test B
```

The final result should be the same.

A practical command is to run individual tests repeatedly and then run the complete module.

The suite should not rely on:

- a previous test having inserted a row
- a specific database sequence value
- a specific execution order
- stale records remaining from an earlier test
- manual cleanup performed outside pytest

This is one reason deterministic fixtures matter.

---

# 17. Failure-Safe Cleanup

Cleanup must happen even when the test itself raises an unexpected exception.

Bad conceptual design:

```python
setup()
test_code()
cleanup()
```

If `test_code()` raises before `cleanup()`, the database may remain dirty.

Fixture-based teardown is safer:

```python
@pytest.fixture
def resource():
    setup()
    yield resource
    cleanup()
```

pytest will execute the teardown section after the test completes, including when the test fails, subject to the fixture lifecycle actually being entered.

This is one of the reasons fixtures are preferable to scattered manual cleanup code.

---

# 18. Unit vs Integration vs API — Final Comparison

| Test Layer | Real DB? | Main Question |
|---|---:|---|
| Unit | No | Is the business logic correct? |
| Integration | Yes | Does the repository/database boundary work correctly? |
| API | Usually No for current project | Does the HTTP contract and dependency wiring work correctly? |

The layers are complementary.

```text
             API Tests
                 │
                 ▼
         Application / Service
                 │
                 ▼
        Integration Tests
                 │
                 ▼
          PostgreSQL
                 │
                 ▼
        Actual persistence
```

A mature test strategy does not choose one layer and discard the others.

It puts the right assertions at the right boundary.

---

# 19. Practical Day 034 Experiments

## Experiment 1 — Inspect Existing Integration Isolation

Review the Day 033 integration test setup.

Identify:

- which table is used for testing
- when it is created
- when it is truncated
- when it is dropped
- which fixture scope controls each lifecycle stage

Expected mental model:

```text
Test Session
   ↓
create isolated table
   ↓
Test 1 → clean/reset → execute
   ↓
Test 2 → clean/reset → execute
   ↓
...
   ↓
drop test table
```

---

## Experiment 2 — Transaction-Aware Fixture

Understand how a fixture can own a transaction:

```text
fixture
  ↓
BEGIN
  ↓
yield connection
  ↓
test executes
  ↓
ROLLBACK
```

Then explicitly check whether the application repository participates in that exact transaction.

Do not assume transaction ownership merely because both the test and repository use PostgreSQL.

---

## Experiment 3 — TRUNCATE vs ROLLBACK

Compare the two workflows:

```text
TRUNCATE strategy
-----------------
Test starts
↓
run repository
↓
cleanup table
↓
next test
```

versus:

```text
ROLLBACK strategy
-----------------
BEGIN
↓
run repository
↓
ROLLBACK
↓
next test
```

The key experiment is observing whether the repository's own transaction commits before the test's cleanup boundary.

---

## Experiment 4 — Force a Constraint Failure

Deliberately create a database state that causes a constraint violation.

Then verify:

1. the expected exception occurs
2. no unexpected partial state remains
3. the database can continue serving subsequent tests

This proves failure handling instead of only testing the happy path.

---

## Experiment 5 — SAVEPOINT Mental Model

Execute the conceptual flow:

```sql
BEGIN;

INSERT ...;

SAVEPOINT checkpoint;

-- risky operation

ROLLBACK TO SAVEPOINT checkpoint;

COMMIT;
```

The key observation is that work before the savepoint can remain while work after the savepoint is undone.

---

## Experiment 6 — Order Independence

Run individual integration tests and then the full suite.

Confirm that no test requires another test to have run first.

A passing suite is not enough; independence is part of correctness.

---

# 20. Enterprise Mapping — How This Appears in ASP.NET Core

The concepts transfer directly to enterprise .NET systems.

Typical architecture:

```text
Controller
   ↓
Service
   ↓
Repository / EF Core DbContext
   ↓
SQL Server / PostgreSQL
```

The same questions still apply:

```text
Who owns the transaction?
Where does it start?
Where does it commit?
What happens on exception?
How is test data isolated?
How is cleanup guaranteed?
```

In ASP.NET Core, common enterprise approaches include:

- EF Core transactions
- `DbContext` lifetime management
- integration-test fixtures
- test containers
- dedicated test databases
- transaction rollback for appropriate test scenarios

The technology changes.

The systems thinking does not.

---

# 21. Architecture Insight — Transaction Ownership Is a Design Decision

One of the strongest lessons from Day 034 is that transaction handling should have a deliberate ownership model.

For a simple repository operation:

```text
Repository
   └── transaction
```

may be sufficient.

For a multi-repository business operation:

```text
Service
 ├── Repository A
 └── Repository B
```

it may become necessary for the service or a unit-of-work abstraction to control one transaction spanning both operations.

Otherwise:

```text
Repository A → COMMIT
Repository B → fails
```

can leave the system partially changed.

This leads directly into more advanced transactional architecture and distributed consistency topics.

---

# 22. Common Mistakes

## Mistake 1 — Mocking the database for every repository test

This removes the very boundary the test is supposed to validate.

## Mistake 2 — Assuming an outer rollback controls internal commits

It does not if the application operation uses an independent transaction that has already committed.

## Mistake 3 — Cleaning data only when tests pass

Failure paths must also leave the environment usable.

## Mistake 4 — Sharing mutable test data between tests

This introduces hidden order dependencies.

## Mistake 5 — Testing only for exceptions

A database failure test should often also verify final state.

## Mistake 6 — Treating rollback as a universal cleanup mechanism

External side effects require other strategies.

---

# 23. Interview Questions

### Q1. What is the difference between a unit test and a database integration test?

A unit test isolates application logic, usually with mocks. A database integration test verifies the real application-to-database boundary using an actual database engine.

### Q2. Why can mocks miss database bugs?

Because mocks do not execute the real SQL, constraints, data types, query planning, transaction behavior, or database-specific semantics.

### Q3. Why is test isolation important?

Because one test's state should not affect another test's outcome. Otherwise tests become order-dependent and unreliable.

### Q4. When is transaction rollback a good test-isolation strategy?

When the test controls the same transaction in which the application performs its writes and no relevant side effects escape that transaction.

### Q5. Why might an outer test rollback fail to clean application data?

Because the application may open and commit a separate transaction before the outer test transaction rolls back.

### Q6. What is a SAVEPOINT?

A point inside a transaction to which PostgreSQL can roll back without discarding the entire transaction.

### Q7. Why use pytest fixtures for database tests?

They centralize setup and teardown and make resource lifecycle more reliable and reusable.

### Q8. What is the difference between `TRUNCATE` cleanup and rollback cleanup?

`TRUNCATE` explicitly resets table state; rollback undoes transactional changes. Rollback depends on transaction ownership, while truncation can serve as a separate explicit cleanup step.

### Q9. What should a constraint-failure integration test verify?

The expected error plus the resulting persisted database state, ensuring no unintended partial write remains.

### Q10. Why is transaction ownership an architectural concern?

Because multi-step operations may need one consistent transaction. Poorly defined boundaries can create partial commits and inconsistent state.

---

# 24. Cheat Sheet

## Transaction

```text
BEGIN
  ↓
operations
  ↓
COMMIT
```

or:

```text
BEGIN
  ↓
operations
  ↓
ROLLBACK
```

## SAVEPOINT

```text
BEGIN
  ↓
operation A
  ↓
SAVEPOINT
  ↓
operation B
  ↓
ROLLBACK TO SAVEPOINT
  ↓
continue
  ↓
COMMIT
```

## pytest fixture lifecycle

```text
setup
 ↓
yield
 ↓
test
 ↓
teardown
```

## Test isolation choices

```text
Rollback
TRUNCATE
Dedicated schema/database
Disposable test environment
```

## Test layers

```text
Unit        → business logic
Integration → DB/repository boundary
API         → HTTP/application contract
```

## Transaction ownership question

```text
WHO STARTS THE TRANSACTION?
WHO COMMITS IT?
WHO ROLLS IT BACK?
```

---

# 25. Final Mental Model

The strongest mental model from Day 034 is:

```text
                    TEST SUITE
                        │
         ┌──────────────┴──────────────┐
         │                             │
      Unit Tests                 Integration Tests
         │                             │
     mocked deps                 real PostgreSQL
                                       │
                              transaction + constraints
                                       │
                       ┌───────────────┴───────────────┐
                       │                               │
                   SUCCESS                         FAILURE
                       │                               │
                    COMMIT                         ROLLBACK
                       │                               │
                       └───────────────┬───────────────┘
                                       │
                                verify final state
                                       │
                                       ▼
                              isolate next test
```

The key engineering principle is:

> **A test is trustworthy only when its environment, transaction boundary, and cleanup behavior are understood.**

Testing database code is therefore not merely about writing assertions.

It is about proving that the repository behaves correctly against the real database while leaving the next test with a known, controlled starting point.

---

# 26. What Day 034 Added to the Project ₹50L Skill Stack

Day 033 established automated coverage.

Day 034 adds transaction-aware confidence.

The progression is:

```text
Day 029
Docker deployment
      ↓
Day 030
Advanced SQL JOINs
      ↓
Day 031
EXPLAIN / query performance
      ↓
Day 032
Indexes / query optimization
      ↓
Day 033
Repository + unit/integration/API testing
      ↓
Day 034
Transaction-safe integration testing
```

This is a meaningful shift from:

> “I can write backend code.”

Toward:

> “I can build backend systems whose persistence behavior is measurable, testable, isolated, and operationally trustworthy.”

That distinction matters significantly at Senior, Staff, and Principal engineering levels.

---

# 27. Revision Checklist

Before considering Day 034 fully internalized, confirm that you can explain these without notes:

- [ ] Why repository integration tests need a real PostgreSQL database.
- [ ] Why test isolation is necessary.
- [ ] How pytest fixtures provide setup and teardown.
- [ ] What a yield fixture does.
- [ ] Function vs session fixture scope at a high level.
- [ ] How `TRUNCATE` can be used for test cleanup.
- [ ] How rollback can be used for test isolation.
- [ ] Why rollback depends on transaction ownership.
- [ ] What a SAVEPOINT is.
- [ ] How to deliberately trigger and verify a constraint failure.
- [ ] Why final database state should be asserted after failure.
- [ ] Why an outer test transaction cannot undo an independently committed repository transaction.
- [ ] Why unit, integration, and API tests complement one another.
- [ ] Why rollback does not undo filesystem, message-bus, or external-service side effects.

---

# 28. Official Resources

### PostgreSQL — Transactions

https://www.postgresql.org/docs/current/tutorial-transactions.html

Focus: transaction control, `BEGIN`, `COMMIT`, and `ROLLBACK`.

### PostgreSQL — SAVEPOINT

https://www.postgresql.org/docs/current/sql-savepoint.html

Focus: creating savepoints and rolling back part of a transaction.

### pytest — Fixtures

https://docs.pytest.org/en/stable/how-to/fixtures.html

Focus: fixture setup/teardown, `yield` fixtures, reuse, and fixture scope.

---

# 29. Day 034 Completion Criteria

Day 034 is complete when you can confidently demonstrate:

1. A real PostgreSQL repository integration test.
2. A controlled isolated database state for tests.
3. A fixture-based setup/teardown lifecycle.
4. A deliberate database failure scenario.
5. Verification of rollback/final database state.
6. A clear explanation of `TRUNCATE` versus transaction rollback.
7. A clear explanation of SAVEPOINT.
8. An understanding of the current repository's transaction boundary.
9. Tests that remain independent of execution order.
10. A clear explanation of why unit and integration tests are both required.

---

# 30. One-Line Takeaway

> **Database integration testing is the discipline of proving that real persistence behavior, transaction boundaries, failure handling, and cleanup work correctly together—not merely that the Python code returns the expected value.**

---

**Day 034 — Database Integration Testing & Transaction Safety**  
**Status:** ✅ Engineering Handbook Completed
