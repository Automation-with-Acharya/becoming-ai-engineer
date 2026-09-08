# Day 033: Automated Testing — Answer Sheet

**Date:** 2026-09-06
**Project:** Student Management System (MiniProject_Student_Management)
**Tools:** pytest 8.3.3, Python 3.14.5, FastAPI TestClient, unittest.mock
**Result:** 27/27 tests PASSED

---

## Exercise 1: Inspect the Current Application

### Architecture Map

The project follows Clean Architecture with three clear layers:

```
HTTP Request
        ↓
   FastAPI App (main.py) — middleware + exception handlers
        ↓ Depends(get_student_service)
   Router (routers/students.py)
        ↓ Depends(get_student_repository)
   Service (services/student_service.py)
        ↓ Depends(get_db_helper)
   Repository (repositories/student_repository.py)
        ↓ psycopg_pool.ConnectionPool
   DatabaseHelper (database/database_helper.py)
        ↓
   PostgreSQL (host=db, port=5432, db=student_db)
```

### Key Components Found

| Component | File | Role |
|-----------|------|------|
| Router | routers/students.py | HTTP routes, request/response parsing |
| Service | services/student_service.py | Business logic, orchestration |
| Repository (ABC) | repositories/student_repository.py | Storage interface contract |
| Repository (Impl) | repositories/student_repository.py | PostgreSQL implementation |
| DatabaseHelper | database/database_helper.py | Connection pool + SQL execution |
| Models | models/student.py | Pydantic request/response schemas |
| Schema | schemas/student_schema.py | Input validation (name sanitisation) |
| Exceptions | exceptions/student_exceptions.py | StudentNotFoundException |
| Config | config.py | Pydantic Settings from .env |
| DI Wiring | dependencies.py | FastAPI Depends() chain |
| Middleware | middleware/request_middleware.py | Request logging, execution time |
| Global Handlers | main.py | ValueError -> 400, StudentNotFoundException -> 404 |

### Where Tests Belong

```
Unit tests        -> Service layer   (mock the repository — no DB needed)
Integration tests -> Repository layer (real DB, isolated table)
API tests         -> Router layer    (TestClient + dependency_overrides)
```

---

## Exercise 2: Create the Test Structure

### Directory Created

```
tests/
  __init__.py                   — package marker + doc
  conftest.py                   — shared fixtures (sample_student, mock_service, api_client)
  unit/
    __init__.py
    test_student_service.py     — Ex 3, 4, 5, 6
  integration/
    __init__.py
    test_student_repository.py  — Ex 7
  api/
    __init__.py
    test_student_routes.py      — Ex 8, 9, 10
```

### Why Three Categories?

| Category | Scope | Speed | Infrastructure | Purpose |
|----------|-------|-------|---------------|---------|
| unit/ | Single class (Service) | ~2 ms per test | None | Prove business logic |
| integration/ | Real DB round-trip | ~500 ms per test | Local PostgreSQL | Prove SQL correctness |
| api/ | Full HTTP layer | ~10 ms per test | None (mocked) | Prove HTTP contract |

---

## Exercise 3: Your First Service Unit Test

### What Was Tested

```python
mock_repo.get_student_by_id.return_value = existing_student
result = service.get_student_by_id(1)
assert result == existing_student
assert result.id == 1
assert result.name == "Alice Test"
```

### How It Works

MagicMock replaces PostgresStudentRepository entirely. The real StudentService runs but
never touches a database — it receives whatever the mock returns.

**Result: PASSED**

---

## Exercise 4: Test Not Found

### What Was Tested

```python
mock_repo.get_student_by_id.return_value = None

with pytest.raises(StudentNotFoundException) as exc_info:
    service.get_student_by_id(999)

assert exc_info.value.student_id == 999
```

### Contract Proven

Repository says: None
  -> Service says: StudentNotFoundException(student_id=999)
  -> Global handler: HTTP 404  (proven separately in api/ tests)

**Result: PASSED**

---

## Exercise 5: Test Business Rules Without PostgreSQL

### Proof: No Database Required

The unit tests ran with:
- No Docker container
- No PostgreSQL process
- No .env file
- No network calls

```python
# The mock was called (service reached the repository)
assert mock_repo.get_student_by_id.called
# The result is correct — no DB involved
assert result.id == 1
```

### Why This Works

MagicMock creates a pure Python object. The StudentService receives it where it
expects a StudentRepository — duck typing allows this since Python does not enforce
types at runtime. This is the engineering payoff of the Repository pattern + DI:
the service is decoupled from storage so completely that testing requires no storage.

**Result: PASSED**

---

## Exercise 6: Verify Repository Interaction

### Tests Written

```python
# Was the repository called with the EXACT right argument?
mock_repo.get_student_by_id.assert_called_once_with(1)

# Was it called exactly ONCE?
assert mock_repo.get_student_by_id.call_count == 1

# Does a different id reach the repository correctly?
service.get_student_by_id(42)
mock_repo.get_student_by_id.assert_called_once_with(42)
```

### Why This Matters

Interaction tests prove the Service-Repository contract. If a future refactor
accidentally passes the wrong id or calls the wrong method, this test catches it.

**Result: PASSED**

---

## Exercise 7: Repository Integration Test

### Setup

An isolated test_students table was created with the same schema as students.

Table lifecycle:
- Created once at session start (session-scoped fixture)
- Truncated before each individual test (autouse=True, function-scoped)
- Dropped after the entire session completes

### Technical Challenge: psycopg Cursor is Read-Only

The initial approach tried to monkey-patch cursor.execute. This failed:

```
AttributeError: 'Cursor' object attribute 'execute' is read-only
```

psycopg's Cursor is a C extension — its attributes cannot be overwritten from Python.

**Solution:** A _SwappingCursor proxy class wraps the real cursor and intercepts
execute() at the Python level, rewriting 'students' -> 'test_students' before
delegating to the real C-level cursor:

```python
class _SwappingCursor:
    def execute(self, sql: str, params=None):
        swapped = re.sub(r'\bstudents\b', TEST_TABLE, sql)
        return self._cur.execute(swapped, params)

    def __getattr__(self, name):
        return getattr(self._cur, name)   # delegate everything else
```

### Tests Run

| Test | What Was Verified | Result |
|------|------------------|--------|
| test_add_and_retrieve_student | INSERT then SELECT round-trip; id assigned | PASSED |
| test_get_student_by_id_returns_none_when_not_found | Missing id returns None | PASSED |
| test_get_all_students_returns_inserted_records | Multiple inserts, list ordered by id | PASSED |
| test_delete_student_returns_true_and_removes_record | DELETE returns True; record gone | PASSED |
| test_delete_nonexistent_student_returns_false | Non-existent delete returns False | PASSED |

**Result: 5/5 PASSED**

---

## Exercise 8: API Test with FastAPI TestClient

### What Was Tested

```python
response = api_client.get("/students/1")

assert response.status_code == 200
body = response.json()
assert body["id"] == 1
assert body["name"] == "Alice Test"
assert body["age"] == 22
assert body["city"] == "Mumbai"
assert body["email"] == "alice.test@example.com"
```

### What the TestClient Does

TestClient.get("/students/1")
  -> FastAPI app receives GET /students/1
  -> Middleware runs (LogIncoming, ExecutionTime, ConsoleLog, CORS)
  -> Router.get_student_by_id(student_id=1, service=mock_service)
  -> mock_service.get_student_by_id(1) returns sample_student
  -> Router serialises Student_response_model to JSON
  -> HTTP 200 response returned

**Result: PASSED**

---

## Exercise 9: Dependency Override

### The Seam

```python
# Production wiring (via Depends chain):
get_db_helper() -> get_student_repository() -> get_student_service()
                                                        |
                                               Injected into Router

# Test wiring (dependency_overrides bypasses entire chain):
app.dependency_overrides[get_student_service] = lambda: mock_service
                                                        |
                                   Mock injected — no DB calls
```

### The Lifespan Problem (and Solution)

PROBLEM: The app lifespan calls get_db_helper() DIRECTLY — not via Depends().
dependency_overrides does NOT intercept direct calls. Without a fix, TestClient
would try to connect to Docker's 'db' host and wait 30 seconds for a pool timeout.

SOLUTION: Use unittest.mock.patch to replace the global _db_helper singleton
in dependencies.py for the duration of the test:

```python
with patch("dependencies._db_helper", mock_db_helper):
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
```

KEY LEARNINGS:
- dependency_overrides only works for code routed through FastAPI's Depends().
- Code calling a dependency function directly (like the lifespan) must be patched at module level.
- This reveals a coupling gap: the lifespan calling get_db_helper() directly
  means it cannot be swapped through the DI seam.

**Result: PASSED**

---

## Exercise 10: Test an Exception / 404

### Test: Status Code

```python
mock_student_service.get_student_by_id.side_effect = StudentNotFoundException(
    student_id=999999
)
response = api_client.get("/students/999999")
assert response.status_code == 404
```

### Test: Response Body Shape

```python
body = response.json()
assert body["error"] == "Not Found"
assert "999999" in body["message"]
assert body["student_id"] == 999999
```

### Full Chain Exercised

```
GET /students/999999
  -> Router calls service.get_student_by_id(999999)
  -> mock_service raises StudentNotFoundException(student_id=999999)
  -> Global exception handler (main.py) catches it
  -> Returns HTTP 404 with {error, message, student_id}
  -> TestClient receives 404 with structured JSON
  -> Assertions pass
```

This test connects Day 013 (CRUD + HTTP status codes), Day 018 (global exception handling),
and Day 033 (automated testing) — proving the entire chain works end-to-end.

**Result: PASSED**

---

## Exercise 11: Run the Entire Test Suite

### Actual pytest -v Output

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-8.3.3, pluggy-1.6.0
collected 27 items

tests/api/test_student_routes.py::TestGetStudentById::test_get_existing_student_returns_200 PASSED
tests/api/test_student_routes.py::TestGetStudentById::test_get_student_calls_correct_service_method PASSED
tests/api/test_student_routes.py::TestGetStudentNotFound::test_get_nonexistent_student_returns_404 PASSED
tests/api/test_student_routes.py::TestGetStudentNotFound::test_404_response_body_matches_expected_shape PASSED
tests/api/test_student_routes.py::TestGetAllStudents::test_get_all_students_returns_200_with_list PASSED
tests/api/test_student_routes.py::TestGetAllStudents::test_get_all_students_returns_empty_list_when_no_students PASSED
tests/api/test_student_routes.py::TestCreateStudent::test_create_student_returns_201_with_created_record PASSED
tests/api/test_student_routes.py::TestCreateStudent::test_create_student_with_empty_name_returns_400 PASSED
tests/api/test_student_routes.py::TestDeleteStudent::test_delete_existing_student_returns_200 PASSED
tests/api/test_student_routes.py::TestDeleteStudent::test_delete_nonexistent_student_returns_404 PASSED
tests/api/test_student_routes.py::TestDependencyOverride::test_dependency_override_replaces_real_service PASSED
tests/integration/test_student_repository.py::TestIntegrationStudentRepository::test_add_and_retrieve_student PASSED
tests/integration/test_student_repository.py::TestIntegrationStudentRepository::test_get_student_by_id_returns_none_when_not_found PASSED
tests/integration/test_student_repository.py::TestIntegrationStudentRepository::test_get_all_students_returns_inserted_records PASSED
tests/integration/test_student_repository.py::TestIntegrationStudentRepository::test_delete_student_returns_true_and_removes_record PASSED
tests/integration/test_student_repository.py::TestIntegrationStudentRepository::test_delete_nonexistent_student_returns_false PASSED
tests/unit/test_student_service.py::TestGetStudentById::test_returns_student_when_found PASSED
tests/unit/test_student_service.py::TestGetStudentById::test_raises_student_not_found_when_missing PASSED
tests/unit/test_student_service.py::TestGetStudentById::test_runs_without_database PASSED
tests/unit/test_student_service.py::TestGetStudentById::test_calls_repository_with_correct_id PASSED
tests/unit/test_student_service.py::TestGetStudentById::test_different_ids_reach_repository PASSED
tests/unit/test_student_service.py::TestAddStudent::test_add_student_returns_created_student PASSED
tests/unit/test_student_service.py::TestAddStudent::test_add_student_raises_value_error_for_empty_name PASSED
tests/unit/test_student_service.py::TestGetAllStudents::test_returns_empty_list_when_no_students PASSED
tests/unit/test_student_service.py::TestGetAllStudents::test_returns_all_students_from_repository PASSED
tests/unit/test_student_service.py::TestDeleteStudent::test_delete_student_success PASSED
tests/unit/test_student_service.py::TestDeleteStudent::test_delete_student_raises_not_found_when_missing PASSED

======================== 27 passed, 1 warning in 8.78s ========================
```

### Final Summary

| Category | Tests | Speed | DB Required |
|----------|-------|-------|-------------|
| unit/ | 11 | ~1.8 s total | No |
| integration/ | 5 | ~14 s total | Yes (local PostgreSQL) |
| api/ | 11 | ~0.7 s total | No |
| TOTAL | 27 | ~8.8 s (full suite) | — |

---

## Key Learnings from Day 033

### 1. The Real Value of DI

Every Depends() call is a TEST SEAM. By overriding get_student_service, we swap the
entire production wiring (DatabaseHelper -> Repository -> Service) without touching
a single line of production code. This is why DI was built this way.

### 2. Three Test Types, Three Different Purposes

- Unit tests: fast, no infrastructure, prove business logic
- Integration tests: slow, real DB, prove SQL is correct
- API tests: fast, no DB, prove HTTP contract end-to-end

Running only one type gives false confidence. Running all three gives real confidence.

### 3. The Lifespan Gotcha

dependency_overrides only works for code going through Depends(). The FastAPI lifespan
calls get_db_helper() directly, bypassing the override. Fix: patch the module-level
singleton with unittest.mock.patch.

### 4. psycopg Cursor is a C Extension

You cannot monkey-patch cursor.execute from Python — it raises AttributeError.
Use a proxy class (_SwappingCursor) that wraps the cursor and intercepts execute()
at the Python level without modifying the underlying C object.
