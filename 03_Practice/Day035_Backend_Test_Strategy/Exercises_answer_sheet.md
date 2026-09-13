# Day 035: Backend Test Strategy — Answer Sheet

**Date:** 2026-09-09
**Project:** Student Management System (MiniProject_Student_Management)
**Tools:** pytest 8.3.3, pytest-cov 7.1.0, coverage 7.16.0, Python 3.14.5
**Suite Result (after all exercises):** 51/51 PASSED

---

## Exercise 1 — Run the Entire Suite (Baseline)

### Command

```bash
python -m pytest tests/ -v
```

### Metrics (Day 034 baseline, before today's additions)

| Metric | Value |
|--------|-------|
| Total tests | 39 |
| Passed | 39 |
| Failed | 0 |
| Skipped | 0 |
| Execution time | ~15 s |

| Category | Count |
|----------|-------|
| Unit tests | 11 |
| Integration tests | 17 |
| API tests | 11 |

### Metrics (after Day 035 additions)

| Metric | Value |
|--------|-------|
| Total tests | 51 |
| Passed | 51 |
| Failed | 0 |
| Skipped | 0 |
| Execution time | ~9 s |

| Category | Count | Change |
|----------|-------|--------|
| Unit tests | 23 | +12 (parametrize + regression) |
| Integration tests | 17 | 0 |
| API tests | 11 | 0 |

### Key Observation

Day 034's goal was to make the suite larger.
Day 035's goal is to make the suite **more useful** — through markers, coverage, and strategy.
The 12 new unit tests added today are not arbitrary additions; they are parametrized cases
that document the complete rule boundary and a permanent regression guard.

---

## Exercise 2 — Introduce Test Markers

### Configuration (`pytest.ini`)

```ini
[pytest]
markers =
    unit: Unit tests - isolate a single class using MagicMock; no DB required
    integration: Integration tests - require a real local PostgreSQL connection
    api: API tests - exercise HTTP layer via FastAPI TestClient; no DB required
    smoke: Smoke tests - critical-path subset; should pass before every deployment

testpaths = tests
norecursedirs = old_versions .git __pycache__ .pytest_cache htmlcov
addopts = --tb=short
```

`testpaths` restricts discovery to `tests/` — preventing pytest from accidentally
picking up legacy `old_versions/` directories that contain conflicting module names.

### Marker Placement

| Marker | Applied To |
|--------|------------|
| `@pytest.mark.unit` | All 5 test classes in `tests/unit/test_student_service.py` |
| `@pytest.mark.integration` | All 7 test classes in `tests/integration/test_student_repository.py` |
| `@pytest.mark.api` | All 5 test classes in `tests/api/test_student_routes.py` |
| `@pytest.mark.smoke` | `TestGetStudentById`, `TestGetAllStudents`, `TestCreateStudent` (api) |

### Selective Execution Results

```bash
# Unit only — no DB, fastest feedback
pytest -m unit -v
# → 23 passed, 28 deselected, 1 warning in 0.10s

# Integration only — needs local PostgreSQL
pytest -m integration -v
# → 17 passed, 34 deselected, 1 warning in 8.66s

# API only — HTTP layer, mocks only
pytest -m api -v
# → 11 passed, 40 deselected, 1 warning in 0.69s

# Smoke only — critical path gate
pytest -m smoke -v
# → 6 passed, 45 deselected, 1 warning in 0.68s
```

### Marker Tree

```text
                    ALL TESTS (51)
                         |
          +--------------+--------------+
          |              |              |
        unit           integ.          api
        (23)            (17)           (11)
                                        |
                                      smoke (6)
                                   [subset of api]
```

### Why Markers Matter

Without markers, every `pytest` run executes all 51 tests including the 17
integration tests that require a running PostgreSQL.  On a machine without a
database (e.g., a developer laptop mid-flight, a CI machine before the DB
service is ready), the suite fails.

With markers:
- `pytest -m "not integration"` runs 34 fast tests in < 1 second.
- `pytest -m smoke` gives a 6-test, < 1s gate before each deployment.
- `pytest -m integration` runs only when a real DB is available.

---

## Exercise 3 — Parametrize Validation Tests

### Problem Being Expressed

The rule is:
> Any blank input (empty, whitespace-only, tab, newline) must raise ValueError
> before reaching the repository.

Before parametrize, expressing this for 6 inputs required 6 nearly-identical test methods.

### Solution

```python
@pytest.mark.parametrize("invalid_name", [
    "",           # completely empty string
    " ",          # single space
    "   ",        # multiple spaces
    "\t",         # tab character
    "\n",         # newline
    "\t\n  \t",    # mixed whitespace
], ids=["empty_string", "single_space", "multi_space", "tab", "newline", "mixed_whitespace"])
def test_blank_name_raises_value_error(self, invalid_name, service, mock_repo):
    with pytest.raises(ValueError):
        service.add_student(name=invalid_name, age=20, city="City", email="v@e.com")
    mock_repo.add_student.assert_not_called()
```

### Output Structure

```
TestValidationParametrize::test_blank_name_raises_value_error[empty_string]    PASSED
TestValidationParametrize::test_blank_name_raises_value_error[single_space]    PASSED
TestValidationParametrize::test_blank_name_raises_value_error[multi_space]     PASSED
TestValidationParametrize::test_blank_name_raises_value_error[tab]             PASSED
TestValidationParametrize::test_blank_name_raises_value_error[newline]         PASSED
TestValidationParametrize::test_blank_name_raises_value_error[mixed_whitespace] PASSED
TestValidationParametrize::test_valid_name_is_accepted[plain_name]             PASSED
TestValidationParametrize::test_valid_name_is_accepted[padded_name]            PASSED
TestValidationParametrize::test_valid_name_is_accepted[name_with_space]        PASSED
```

### Why This Is Better

The parametrized form:
1. **Documents the complete rule boundary** in one block — both valid and invalid cases.
2. **Fails precisely** — if `"\t"` slips through validation, exactly
   `test_blank_name_raises_value_error[tab]` fails, not a generic test.
3. **Trivially extensible** — adding a new edge case means adding one line to the
   `parametrize` list, not writing a new test method.
4. **Communicates intent** — the `ids=` list names each case, making test output
   self-documenting.

> The goal is not to reduce line count. The goal is to express:
> **One behavior, many examples.**

---

## Exercise 4 — Generate a Coverage Report

### Commands Run

```bash
python -m coverage run --source=. --omit="tests/*,old_versions/*" -m pytest tests/ -q
python -m coverage report --skip-empty
python -m coverage html
```

### Coverage Report Output

```
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
app.py                                   3      3     0%
auth\jwt_bearer.py                      20     12    40%
auth\jwt_utils.py                       31     18    42%
auth\password_utils.py                   6      1    83%
config.py                               12      0   100%
database\__init__.py                     2      0   100%
database\database_helper.py            103     20    81%
dependencies.py                         11      2    82%
exceptions\__init__.py                   2      0   100%
exceptions\student_exceptions.py         4      0   100%
logger_config.py                        31      2    94%
main.py                                 53      9    83%
middleware\request_middleware.py        30      1    97%
models\__init__.py                       2      0   100%
models\student.py                       12      0   100%
repositories\__init__.py                 2      0   100%
repositories\student_repository.py      96     34    65%
routers\__init__.py                      2      0   100%
routers\auth.py                         56     33    41%
routers\students.py                     37      4    89%
schemas\__init__.py                      2      0   100%
schemas\student_schema.py                9      0   100%
services\__init__.py                     2      0   100%
services\student_service.py             69     21    70%
--------------------------------------------------------
TOTAL                                  597    160    73%
```

### Coverage Summary by Category

| File | Coverage | Notes |
|------|----------|-------|
| `config.py` | 100% | Only constants — fully covered |
| `schemas/student_schema.py` | 100% | All validation paths exercised |
| `exceptions/student_exceptions.py` | 100% | Used in every not-found scenario |
| `models/student.py` | 100% | Pydantic model — always constructed |
| `middleware/request_middleware.py` | 97% | Logging middleware — high coverage |
| `logger_config.py` | 94% | Logging setup — nearly complete |
| `routers/students.py` | 89% | Most endpoints covered; search path partially missed |
| `main.py` | 83% | Startup, shutdown, handlers covered; some edge cases missed |
| `database/database_helper.py` | 81% | Pool creation/closing covered; error retry paths missed |
| `dependencies.py` | 82% | DI functions covered; some branches missed |
| `services/student_service.py` | 70% | Core methods covered; `search_students` not tested |
| `repositories/student_repository.py` | 65% | Core CRUD covered; `search_students` not tested |
| `auth/jwt_bearer.py` | 40% | Auth middleware — token validation paths untested |
| `auth/jwt_utils.py` | 42% | JWT token creation/parsing mostly untested |
| `routers/auth.py` | 41% | Login/register routes not yet tested |
| `app.py` | 0% | Uvicorn runner — not executed during tests (correct) |

**Overall: 73% — a solid baseline for a codebase of this complexity.**

---

## Exercise 5 — Identify the Most Important Untested Code

### Coverage Improvement Should Be Risk-Driven, Not Percentage-Driven

Blindly chasing 100% coverage would lead to testing the Uvicorn runner (`app.py`)
and JSON serialization details that add no engineering value.

### Priority Classification

#### Category A — HIGH PRIORITY: Important Business Logic

| File | Uncovered Code | Risk |
|------|---------------|------|
| `services/student_service.py` (70%) | `search_students()` method — real query logic, no test | **HIGH** — a bug in search returns wrong students silently |
| `repositories/student_repository.py` (65%) | `search_students()` SQL — `ILIKE` query path | **HIGH** — SQL error would surface only in production |

`search_students` is used in the router (`routers/students.py`) and exposed via the API.
It is active production code with no unit or integration test coverage.

#### Category B — HIGH PRIORITY: Error Handling

| File | Uncovered Code | Risk |
|------|---------------|------|
| `database/database_helper.py` (81%) | Pool connection retry logic, connection error recovery | **HIGH** — if the retry path is broken, DB outages cause unhandled exceptions |
| `main.py` (83%) | Global `ValueError` handler edge cases, lifespan error path | **MEDIUM** — the happy path is covered; edge cases in error handling are not |
| `auth/jwt_utils.py` (42%) | Token expiry checks, invalid signature handling | **HIGH** — a bug here would silently accept or reject tokens incorrectly |

#### Category C — MEDIUM: Infrastructure Branches

| File | Uncovered Code | Risk |
|------|---------------|------|
| `auth/jwt_bearer.py` (40%) | Token extraction from `Authorization` header, scheme validation | **MEDIUM** — auth works in production but edge cases (missing header, wrong scheme) are not tested |
| `routers/auth.py` (41%) | Login and register route handlers | **MEDIUM** — these are complete routes that have zero test coverage; a breaking change would be undetected |

#### Category D — LOW: Defensive / Unreachable Code

| File | Uncovered Code | Risk |
|------|---------------|------|
| `app.py` (0%) | Uvicorn runner entrypoint | **LOW** — this is `if __name__ == "__main__": uvicorn.run(...)`. It cannot be unit/integration tested and should not be. |
| `logger_config.py` (94%) | Log formatter edge case (6%) | **LOW** — logging misconfiguration would not cause a production failure; just missing log entries |

### Recommended Testing Priority

```text
1. search_students (service + repository)  ← HIGH PRIORITY
   → Add 1 unit test (mock repo) + 1 integration test (real DB)

2. auth routes (jwt_utils, jwt_bearer, routers/auth.py) ← HIGH/MEDIUM
   → Add unit tests for token generation/validation
   → Add API tests for login/register endpoints

3. database_helper retry logic ← MEDIUM
   → Add unit test with a failing connection mock

4. app.py ← Skip (correct to leave at 0%)
```

---

## Exercise 6 — Add One High-Value Regression Test

### Bug Scenario: Blank Name Leaks to Database

**The bug:**
If `StudentSchema.validate_student_name()` failed silently (returned the blank string
instead of raising `ValueError`), blank names would be inserted into PostgreSQL.
Students with `name=''` or `name='   '` would exist in the database, violating the
meaningful-content invariant of the business domain.

**This was a realistic risk in earlier versions** — the validation was added in Day 013.
Any future refactor that accidentally removes or silences the validation would cause this.

### Regression Test Added: `TestRegressionBlankNameNotPersistedToDb`

```python
@pytest.mark.unit
class TestRegressionBlankNameNotPersistedToDb:
    """
    Day 035 Exercise 6: Permanent regression guard for the blank-name bug.

    If someone accidentally removes the validation from StudentSchema or
    StudentService six months from now, this test fails with:
      AssertionError: Expected 'add_student' to not have been called.
    """

    def test_blank_name_does_not_reach_repository(self, service, mock_repo):
        with pytest.raises(ValueError, match="(?i)empty"):
            service.add_student(name="   ", age=25, city="City", email="r@e.com")
        mock_repo.add_student.assert_not_called()

    def test_whitespace_only_name_never_inserted_to_db(self, service, mock_repo):
        for bad_name in ["\t", "\n", "  \t  "]:
            with pytest.raises(ValueError):
                service.add_student(name=bad_name, age=20, city="City", email="b@e.com")
        mock_repo.add_student.assert_not_called()

    def test_empty_string_name_raises_not_falls_through(self, service, mock_repo):
        with pytest.raises(ValueError):
            service.add_student(name="", age=20, city="City", email="e@e.com")
        mock_repo.add_student.assert_not_called()
```

### What This Test Guards

```text
Future code change removes validation:
  service.add_student(name="   ")
    -> StudentSchema.validate_student_name("   ")  <- removed!
    -> no exception raised
    -> Student_model(name="   ") constructed
    -> repository.add_student(student) called  ← mock.assert_not_called() FAILS
    -> Test output: AssertionError: Expected 'add_student' to not have been called.
    -> ✅ Bug caught immediately
```

### Test Results

```
TestRegressionBlankNameNotPersistedToDb::test_blank_name_does_not_reach_repository PASSED
TestRegressionBlankNameNotPersistedToDb::test_whitespace_only_name_never_inserted_to_db PASSED
TestRegressionBlankNameNotPersistedToDb::test_empty_string_name_raises_not_falls_through PASSED
```

---

## Exercise 7 — Create a Smoke Test Group

### Critical Paths Identified and Marked

```python
@pytest.mark.api
@pytest.mark.smoke
class TestGetStudentById: ...      # GET /students/{id} - read path

@pytest.mark.api
@pytest.mark.smoke
class TestGetAllStudents: ...      # GET /students/ - list path

@pytest.mark.api
@pytest.mark.smoke
class TestCreateStudent: ...       # POST /students/ - write path
```

### Smoke Run Result

```bash
pytest -m smoke -v
# 6 passed, 45 deselected in 0.68s
```

### Smoke Test Selection Rationale

| Test Class | Smoke? | Justification |
|-----------|--------|---------------|
| `TestGetStudentById` | ✅ Yes | Core read path; if broken, no student can be fetched |
| `TestGetAllStudents` | ✅ Yes | List endpoint; proves basic routing and serialisation |
| `TestCreateStudent` | ✅ Yes | Write path; if broken, no new students can be created |
| `TestGetStudentNotFound` | ❌ No | Error path; important but not a deployment blocker |
| `TestDeleteStudent` | ❌ No | Delete is useful but system is usable without it |
| `TestDependencyOverride` | ❌ No | Infrastructure test; not a user-facing path |

### CI/CD Flow

```text
New Build
    |
Smoke Tests (6 tests, < 1s)
    |
Pass?
+-----+-----+
|           |
No         Yes
|           |
Stop    Continue to
        Full Suite (51 tests, ~9s)
            |
        Pass?
        +-------+-------+
        |               |
       No             Yes
        |               |
       Block         Deploy
```

The smoke gate saves CI/CD time — no need to run 9+ seconds of integration
tests if the 6 critical-path HTTP tests already fail in < 1 second.

---

## Exercise 8 — Test the Complete Critical Path

### User Journey: Create Student

```text
HTTP POST /students/
    |
[routers/students.py] router.post("/students/")
    |                   -> calls get_student_service() via Depends()
[dependencies.py]       -> builds StudentService(PostgresStudentRepository(db_helper))
    |
[services/student_service.py] StudentService.add_student()
    |                   -> validates name via StudentSchema
    |                   -> calls repository.add_student(Student_model)
[repositories/student_repository.py] PostgresStudentRepository.add_student()
    |                   -> execute_write_transaction(INSERT INTO students ...)
[database/database_helper.py] DatabaseHelper.execute_write_transaction()
    |
[PostgreSQL]            -> writes row, returns assigned id
    |
[repositories]          -> returns Student_response_model
[services]              -> returns Student_response_model
[routers]               -> serialises to JSON
    |
HTTP 201 Created + JSON body
```

### Which Test Layer Protects Each Part

| Layer | Protected By | Test File |
|-------|-------------|-----------|
| HTTP routing (URL, method, status code) | API test | `tests/api/test_student_routes.py` |
| JSON serialisation (response shape) | API test | `tests/api/test_student_routes.py` |
| Name validation (ValueError → 400) | Unit test + API test | both |
| Service delegation to repository | Unit test (mock repo) | `tests/unit/test_student_service.py` |
| SQL INSERT correctness | Integration test | `tests/integration/test_student_repository.py` |
| DB constraint enforcement (UNIQUE, PK) | Integration test | `tests/integration/test_student_repository.py` |
| Transaction atomicity | Integration test | `tests/integration/test_student_repository.py` |
| PostgreSQL connection/pool management | Integration test (implicitly) | `tests/integration/test_student_repository.py` |

### Coverage Map for the Create Path

```text
POST /students/
    |
    +-> [API Test] tests HTTP layer (status codes, JSON shape, error handler wiring)
    |
    +-> [Unit Test] tests service logic (validation, delegation, not-found handling)
    |
    +-> [Integration Test] tests SQL + DB constraints + transactions
    |
    +-> [NOT TESTED] auth middleware path (JWT validation for protected routes)
```

The one gap: JWT authentication on protected routes has no tests yet.
This is the `routers/auth.py` and `auth/jwt_bearer.py` coverage gap identified
in Exercise 5 (Category B).

---

## Exercise 9 — Repository Quality Review

### `repositories/student_repository.py` Analysis

**Are method names business-oriented?**
Yes. `add_student`, `get_student_by_id`, `get_all_students`, `delete_student`, `search_students`
read as domain operations, not SQL commands.  A developer reading the service code does not need
to know the underlying SQL to understand what the repository does.

**Are SQL details isolated?**
Yes. All SQL strings are defined inside repository methods and never exposed to the service or
router layers.  The service calls `repository.add_student(student_model)` and receives a
`Student_response_model` — no SQL, no cursor, no connection object leaks upward.

**Are transactions handled consistently?**
Mostly. `add_student` uses `execute_write_transaction()` (a multi-step atomic operation —
SELECT MAX(id) + INSERT).  `delete_student` uses `execute_write()` (single statement, atomic
by itself).  The pattern is intentional and consistent for the complexity of each operation.

**Are errors propagated appropriately?**
Yes. The repository logs the exception and re-raises it.  The service catches specific
exception types and either re-raises or wraps in a domain exception.  Neither layer silently
swallows errors.

**Are return models clear?**
Yes. All read methods return `Student_response_model` (which has `id: int`, guaranteed non-None).
Input-only methods receive `Student_model` (with `id: int | None`).  The boundary between
"before DB assigns an id" and "after DB assigns an id" is reflected in the type system.

### `services/student_service.py` Analysis

**Is business logic still outside the repository?**
Yes. The service handles:
  - Name validation (`StudentSchema.validate_student_name`)
  - Not-found detection (`None → StudentNotFoundException`)
  - Query cleaning (`search_students` strips the query before forwarding)

The repository does none of these — it only does SQL.

**Is database knowledge leaking upward?**
No. The service does not import psycopg, does not know about connection pools,
does not know about table names.  The entire `database/` package is invisible to the service.

**Could the service be tested without PostgreSQL?**
Yes — and the 23 unit tests prove it.  The service is tested in isolation with MagicMock
replacing the repository.  No database, no Docker, no .env.  This is the payoff of the
dependency injection / Repository Pattern approach.

---

## Exercise 10 — Final Test Architecture Diagram

### Component Diagram

```text
                    Student Backend System
                    =====================

              HTTP Client (curl, Swagger UI, frontend)
                              |
                    +---------+---------+
                    |                   |
              POST /students/     GET /students/{id}
                    |                   |
                    v                   v
                ┌───────────────────────────────┐
                │         Router Layer          │
                │  routers/students.py          │
                │  routers/auth.py              │
                └──────────────┬────────────────┘
                               │
               ┌───────────────┴───────────────┐
               │  ┌─────────────────────────┐  │
               │  │       API Tests         │  │
               │  │  TestClient + mocks     │  │  ← tests/api/test_student_routes.py
               │  │  pytest -m api          │  │
               │  └─────────────────────────┘  │
               └───────────────┬───────────────┘
                               │ Depends() injection
                ┌──────────────┴────────────────┐
                │        Service Layer           │
                │  services/student_service.py   │
                │  schemas/student_schema.py     │
                └──────────────┬────────────────┘
                               │
               ┌───────────────┴───────────────┐
               │  ┌─────────────────────────┐  │
               │  │       Unit Tests        │  │
               │  │  MagicMock repository   │  │  ← tests/unit/test_student_service.py
               │  │  pytest -m unit         │  │
               │  └─────────────────────────┘  │
               └───────────────┬───────────────┘
                               │
                ┌──────────────┴────────────────┐
                │      Repository Layer          │
                │  repositories/student_rep...   │
                │  database/database_helper.py   │
                └──────────────┬────────────────┘
                               │
               ┌───────────────┴───────────────┐
               │  ┌─────────────────────────┐  │
               │  │   Integration Tests     │  │
               │  │  Real DB connection     │  │  ← tests/integration/test_student_rep...
               │  │  pytest -m integration  │  │
               │  └─────────────────────────┘  │
               └───────────────┬───────────────┘
                               │
                ┌──────────────┴────────────────┐
                │         PostgreSQL             │
                │  test_students (isolated table)│
                └───────────────────────────────┘
```

### Testing Lifecycle Diagram

```text
Developer makes a change
        |
        v
pytest -m unit                   ← < 0.5s, no infrastructure
(23 tests: service logic,
 validation, regression guards)
        |
     All pass?
        |
        v
pytest -m smoke                  ← < 1s, no infrastructure
(6 tests: critical HTTP paths)
        |
     All pass?
        |
        v
pytest -m "not integration"      ← < 1s, no infrastructure
(34 tests: unit + api)
        |
     All pass?
        |
        v
pytest -m integration            ← ~9s, needs local PostgreSQL
(17 tests: SQL + DB constraints
 + transactions + atomicity)
        |
     All pass?
        |
        v
coverage run -m pytest           ← identifies uncovered paths
        |
coverage report
        |
Risk classification
(A: business logic → test now
 B: error handling → test soon
 C: infrastructure → optional
 D: unreachable  → skip)
        |
        v
Merge / Deploy
```

### Current Coverage Snapshot

```text
Layer                 Coverage    Gap Analysis
─────────────────────────────────────────────────────────────────
schemas/              100%        Complete — all validation paths
models/               100%        Complete — Pydantic models
exceptions/           100%        Complete — custom exceptions
middleware/            97%        Near-complete — logging paths
logger_config          94%        Near-complete — setup code
routers/students       89%        Near — search endpoint partial
main.py                83%        Good — some error edge cases
database_helper        81%        Good — retry paths untested
dependencies           82%        Good — minor gaps
services/service       70%        search_students() not tested
repositories/          65%        search_students() not tested
auth/ (all files)      40-42%     Auth layer effectively untested
app.py                  0%        Correct — runner, not testable
─────────────────────────────────────────────────────────────────
TOTAL                  73%        Solid for a 51-test suite
```

### What Day 035 Added to the Strategy

| Before Day 035 | After Day 035 |
|---------------|--------------|
| 39 tests — all equivalent weight | 51 tests — structured by marker |
| `pytest` runs everything | `pytest -m smoke` runs the critical 6 in < 1s |
| No coverage measurement | 73% coverage, classified by risk priority |
| No regression tests | 3 permanent regression guards for the blank-name bug |
| 1 test per validation case | 1 parametrized test for 6 cases of the same rule |
| No formal test architecture | Full architectural diagram with CI/CD lifecycle |

---

## Final Test Count Summary

| Marker | Tests | Execution Time | Infrastructure |
|--------|-------|---------------|---------------|
| `unit` | 23 | ~0.1 s | None |
| `integration` | 17 | ~8.7 s | PostgreSQL |
| `api` | 11 | ~0.7 s | None |
| `smoke` | 6 | ~0.7 s | None |
| **Total** | **51** | **~9.2 s** | |

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-8.3.3
configfile: pytest.ini
collected 51 items

51 passed, 1 warning in 9.22s
=============================
```
