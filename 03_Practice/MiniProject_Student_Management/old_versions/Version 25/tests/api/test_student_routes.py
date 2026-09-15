"""
test_student_routes.py — API-level tests using FastAPI TestClient.

Day 033 Exercises: 8, 9, 10.
Day 035 Exercises: 2 (@pytest.mark.api), 7 (@pytest.mark.smoke on critical paths).

WHY API tests?
--------------
Unit tests verify service logic in isolation.
Integration tests verify the repository against a real database.
API tests verify the FULL HTTP layer: routing, serialisation, status codes,
and the global exception handlers — all in one shot.

The FastAPI TestClient simulates a real HTTP client talking to the real app.
Because we use dependency_overrides (Exercise 9), the real StudentService
(and therefore PostgreSQL) is never instantiated — the fake service returns
whatever we configure, keeping these tests fast and self-contained.

Architecture:
  Test (HTTP request via TestClient)
    ↓
  FastAPI app (real router, real middleware, real exception handlers)
    ↓
  Dependency override → mock_student_service (fake)
    ↓
  (no database)  ← PostgreSQL is absent

This means we test:
  - Correct URL routing (the right handler is invoked)
  - Correct HTTP status codes (200, 201, 404, etc.)
  - Correct JSON response shape
  - Global exception handlers (StudentNotFoundException → 404)
  - Pydantic serialisation / validation at the HTTP boundary

conftest.py supplies:
  - sample_student          : A ready-made Student_response_model
  - mock_student_service    : A MagicMock wired as StudentService
  - api_client              : TestClient with dependency_overrides applied
"""

import pytest
from unittest.mock import MagicMock

from exceptions import StudentNotFoundException
from models.student import Student_response_model


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 8 + 9: GET /students/{id} — happy path
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
@pytest.mark.smoke  # Exercise 7: GET /students/{id} is a critical-path smoke test
class TestGetStudentById:
    """HTTP tests for GET /students/{student_id}.

    Day 035 Exercise 2: @pytest.mark.api  -> run with `pytest -m api -v`.
    Day 035 Exercise 7: @pytest.mark.smoke -> run with `pytest -m smoke -v`.
    Smoke justification: if GET /students/{id} is broken, the entire student
    read path is down and no deployment should proceed.
    """

    def test_get_existing_student_returns_200(
        self,
        api_client,
        mock_student_service: MagicMock,
        sample_student: Student_response_model,
    ):
        """
        Exercise 8: GET /students/1 → HTTP 200 with correct JSON.

        Flow:
          TestClient sends GET /students/1
            ↓
          FastAPI router calls service.get_student_by_id(1)
            ↓
          mock_student_service (via dependency_override) returns sample_student
            ↓
          Router serialises to JSON and returns HTTP 200

        Exercise 9: The key insight here is dependency_overrides.
          Without DI the router would try to build the real service and open
          a database connection.  With DI we swap it transparently.
        """
        # ARRANGE — configure the fake service to return our sample student
        mock_student_service.get_student_by_id.return_value = sample_student

        # ACT — make the real HTTP request through the real FastAPI app
        response = api_client.get("/students/1")

        # ASSERT — status code
        assert response.status_code == 200

        # ASSERT — response body matches the expected student shape
        body = response.json()
        assert body["id"] == 1
        assert body["name"] == "Alice Test"
        assert body["age"] == 22
        assert body["city"] == "Mumbai"
        assert body["email"] == "alice.test@example.com"

    def test_get_student_calls_correct_service_method(
        self,
        api_client,
        mock_student_service: MagicMock,
        sample_student: Student_response_model,
    ):
        """
        The router must call get_student_by_id, not any other service method.

        This is the API-level equivalent of Exercise 6's interaction test:
        verify the router correctly translates the URL path parameter into
        a service call with the exact same integer.
        """
        mock_student_service.get_student_by_id.return_value = sample_student

        api_client.get("/students/1")

        # The service method must have been called with exactly id=1
        mock_student_service.get_student_by_id.assert_called_once_with(1)


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 10: GET /students/{id} — not-found path → HTTP 404
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
class TestGetStudentNotFound:
    """HTTP 404 tests — connecting Day 13 (CRUD), Day 18 (exception handling), Day 33 (tests).

    Day 035 Exercise 2: @pytest.mark.api.
    Not marked smoke because the error path, while important, is secondary
    to the happy-path smoke check above.
    """

    def test_get_nonexistent_student_returns_404(
        self,
        api_client,
        mock_student_service: MagicMock,
    ):
        """
        Exercise 10: GET /students/999999 → HTTP 404.

        Full chain exercised:
          GET /students/999999
            ↓
          Router calls service.get_student_by_id(999999)
            ↓
          mock_student_service raises StudentNotFoundException(student_id=999999)
            ↓
          Global exception handler in main.py catches it
            ↓
          HTTP 404 JSON response returned

        This test proves the wiring between:
          - The domain exception (StudentNotFoundException)
          - The global exception handler (Day 18 work)
          - The HTTP response (Day 13 status codes)
        """
        # ARRANGE — configure the fake service to raise as the real one would
        mock_student_service.get_student_by_id.side_effect = StudentNotFoundException(
            student_id=999999
        )

        # ACT
        response = api_client.get("/students/999999")

        # ASSERT — HTTP status code
        assert response.status_code == 404

    def test_404_response_body_matches_expected_shape(
        self,
        api_client,
        mock_student_service: MagicMock,
    ):
        """
        The 404 JSON body must match the shape defined in the global handler.

        Global handler (main.py) produces:
          {
            "error": "Not Found",
            "message": "Student with ID 999999 not found.",
            "student_id": 999999
          }

        We verify the exact shape here so that any future change to the
        exception handler that breaks the contract is immediately caught.
        """
        mock_student_service.get_student_by_id.side_effect = StudentNotFoundException(
            student_id=999999
        )

        response = api_client.get("/students/999999")

        body = response.json()
        assert body["error"] == "Not Found"
        assert "999999" in body["message"]   # message contains the missing id
        assert body["student_id"] == 999999


# ─────────────────────────────────────────────────────────────────────────────
# GET /students/ — list all students
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
@pytest.mark.smoke  # Exercise 7: GET /students/ is part of the critical smoke path
class TestGetAllStudents:
    """HTTP tests for GET /students/.

    Day 035 Exercise 2: @pytest.mark.api.
    Day 035 Exercise 7: @pytest.mark.smoke.
    Smoke justification: listing students is a fundamental read operation
    whose failure indicates basic routing or serialisation is broken.
    """

    def test_get_all_students_returns_200_with_list(
        self,
        api_client,
        mock_student_service: MagicMock,
        sample_student: Student_response_model,
    ):
        """
        GET /students/ must return HTTP 200 and a JSON array of students.
        """
        mock_student_service.get_all_students.return_value = [sample_student]

        response = api_client.get("/students/")

        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 1
        assert body[0]["name"] == "Alice Test"

    def test_get_all_students_returns_empty_list_when_no_students(
        self,
        api_client,
        mock_student_service: MagicMock,
    ):
        """
        GET /students/ with no students must return HTTP 200 and an empty array.

        An empty list is NOT a 404 — the resource (the collection) exists;
        it is just empty.  This is a common HTTP semantics mistake.
        """
        mock_student_service.get_all_students.return_value = []

        response = api_client.get("/students/")

        assert response.status_code == 200
        assert response.json() == []


# ─────────────────────────────────────────────────────────────────────────────
# POST /students/ — create student
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
@pytest.mark.smoke  # Exercise 7: POST /students/ (create) is a critical smoke path
class TestCreateStudent:
    """HTTP tests for POST /students/.

    Day 035 Exercise 2: @pytest.mark.api.
    Day 035 Exercise 7: @pytest.mark.smoke.
    Smoke justification: if creating a student fails, the write path is broken
    and the system is not ready for production traffic.
    """

    def test_create_student_returns_201_with_created_record(
        self,
        api_client,
        mock_student_service: MagicMock,
        sample_student: Student_response_model,
    ):
        """
        POST /students/ must return HTTP 201 Created and the full student record.
        """
        mock_student_service.add_student.return_value = sample_student

        payload = {
            "name": "Alice Test",
            "age": 22,
            "city": "Mumbai",
            "email": "alice.test@example.com",
        }

        response = api_client.post("/students/", json=payload)

        assert response.status_code == 201
        body = response.json()
        assert body["id"] == 1
        assert body["name"] == "Alice Test"

    def test_create_student_with_empty_name_returns_400(
        self,
        api_client,
        mock_student_service: MagicMock,
    ):
        """
        POST /students/ with an invalid (whitespace-only) name must return HTTP 400.

        The ValueError from StudentSchema.validate_student_name is caught by the
        global ValueError handler in main.py and converted to HTTP 400.
        """
        # Configure the mock to raise ValueError (as the real service would for bad name)
        mock_student_service.add_student.side_effect = ValueError(
            "Name cannot be empty."
        )

        payload = {
            "name": "   ",   # whitespace-only — invalid
            "age": 20,
            "city": "Delhi",
            "email": "test@example.com",
        }

        response = api_client.post("/students/", json=payload)

        assert response.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /students/{id}
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
class TestDeleteStudent:
    """HTTP tests for DELETE /students/{student_id}.

    Day 035 Exercise 2: @pytest.mark.api.
    Not marked smoke — delete is important but less critical than read/write for
    a basic smoke gate (the system can be usable even if delete has issues).
    """

    def test_delete_existing_student_returns_200(
        self,
        api_client,
        mock_student_service: MagicMock,
    ):
        """
        DELETE /students/1 must return HTTP 200 and a confirmation message.
        """
        # delete_student returns None on success (no return value)
        mock_student_service.delete_student.return_value = None

        response = api_client.delete("/students/1")

        assert response.status_code == 200
        body = response.json()
        assert "message" in body
        assert "1" in body["message"]

    def test_delete_nonexistent_student_returns_404(
        self,
        api_client,
        mock_student_service: MagicMock,
    ):
        """
        DELETE /students/999 for a non-existent student must return HTTP 404.
        """
        mock_student_service.delete_student.side_effect = StudentNotFoundException(
            student_id=999
        )

        response = api_client.delete("/students/999")

        assert response.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 9: Explicit dependency override demonstration
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
class TestDependencyOverride:
    """Exercise 9: Prove that dependency_overrides swaps the real service.

    Day 035 Exercise 2: @pytest.mark.api.

    The api_client fixture (in conftest.py) already applies the override.
    This class makes the mechanism explicit and documented for educational
    purposes — it tests the SAME behaviour but with commentary explaining
    exactly what FastAPI's dependency_overrides does and why it matters.
    """

    def test_dependency_override_replaces_real_service(
        self,
        api_client,
        mock_student_service: MagicMock,
        sample_student: Student_response_model,
    ):
        """
        The mock_student_service (not PostgresStudentRepository) serves this request.

        Without dependency_overrides, FastAPI would call get_student_service()
        which calls get_student_repository() which calls get_db_helper() which
        tries to open a real database connection — and our test would fail with
        a connection error.

        With dependency_overrides, the entire chain is bypassed:
          FastAPI sees: "get_student_service is overridden → use lambda: mock"
          Result: the mock is injected directly, no DB connection is ever attempted.

        This is the "seam" that Dependency Injection creates for testing.
        The real engineering value: the same DI wiring used for clean production
        code is also the hook point for safe, fast, isolated testing.
        """
        mock_student_service.get_student_by_id.return_value = sample_student

        response = api_client.get("/students/1")

        # The mock was called — not the real service, not the real repository
        assert mock_student_service.get_student_by_id.called
        assert response.status_code == 200

        # The response contains the data our fake service returned
        body = response.json()
        assert body["id"] == sample_student.id
        assert body["name"] == sample_student.name
