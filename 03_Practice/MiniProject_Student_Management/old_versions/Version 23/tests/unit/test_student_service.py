"""
test_student_service.py — Unit tests for StudentService.

Day 033 Exercises covered: 3, 4, 5, 6.

WHY unit tests?
---------------
A unit test isolates exactly one class (here: StudentService) and replaces
all of its collaborators (here: StudentRepository) with controlled fakes.

Result: these tests run in milliseconds, require NO database, NO Docker,
NO network access, and NO environment variables.  They only test the business
logic written inside StudentService itself.

The test doubles (MagicMock) play the role of the Repository and return
whatever the test configures — this lets us prove service behaviour under
any condition without spinning up infrastructure.

Architecture reminder:
  Test
    ↓
  StudentService          ← what we are testing
    ↓
  MagicMock (repository)  ← controlled fake
    ↓
  (no database)           ← PostgreSQL is completely absent
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, call

from services.student_service import StudentService
from models.student import Student_response_model
from exceptions import StudentNotFoundException


# ─────────────────────────────────────────────────────────────────────────────
# Local fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_repo() -> MagicMock:
    """
    Return a MagicMock acting as a StudentRepository.

    MagicMock automatically creates attributes and methods on first access,
    so we only need to configure the return values we care about per test.
    The real PostgresStudentRepository (and therefore PostgreSQL) is never
    instantiated.
    """
    return MagicMock()


@pytest.fixture
def service(mock_repo: MagicMock) -> StudentService:
    """
    Return a StudentService wired with the mock repository.

    This mirrors the production wiring:
      StudentService(repository=PostgresStudentRepository(db_helper))
    but the repository is a mock — no DB connection is made.
    """
    return StudentService(repository=mock_repo)


@pytest.fixture
def existing_student() -> Student_response_model:
    """A fully-populated student model used as a controlled return value."""
    return Student_response_model(
        id=1,
        name="Alice Test",
        age=22,
        city="Mumbai",
        email="alice.test@example.com",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 3: Service returns student when repository finds one
# ─────────────────────────────────────────────────────────────────────────────

class TestGetStudentById:
    """Tests for StudentService.get_student_by_id()."""

    def test_returns_student_when_found(
        self,
        service: StudentService,
        mock_repo: MagicMock,
        existing_student: Student_response_model,
    ):
        """
        Exercise 3: Happy path — repository returns a student, service passes it through.

        Flow:
          Test configures mock_repo.get_student_by_id(1) → existing_student
          ↓
          service.get_student_by_id(1) calls mock_repo
          ↓
          Service returns the student unchanged (no transformation needed here)
          ↓
          Assert: returned object equals the expected student

        PostgreSQL: NOT involved.  The mock replaces the entire repository.
        """
        # ARRANGE — tell the mock what to return when called with id=1
        mock_repo.get_student_by_id.return_value = existing_student

        # ACT — call the real service method
        result = service.get_student_by_id(1)

        # ASSERT — service should return whatever the repository gave it
        assert result == existing_student
        assert result.id == 1
        assert result.name == "Alice Test"

    # ─────────────────────────────────────────────────────────────────────────
    # Exercise 4: Service raises StudentNotFoundException when repo returns None
    # ─────────────────────────────────────────────────────────────────────────

    def test_raises_student_not_found_when_missing(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Exercise 4: Not-found path — repository returns None, service raises.

        Contract proven here:
          Repository says:  None  (student does not exist)
          Service says:     StudentNotFoundException
          Global handler:   HTTP 404  (tested separately in api/ tests)

        This is the Clean Architecture separation in action:
          - The service does NOT return None to the caller.
          - It raises a domain exception instead.
          - The router stays free of manual None-checks.
          - The global handler converts the domain exception to an HTTP response.
        """
        # ARRANGE — simulate "student not in database"
        mock_repo.get_student_by_id.return_value = None

        # ACT + ASSERT — the service must raise StudentNotFoundException
        with pytest.raises(StudentNotFoundException) as exc_info:
            service.get_student_by_id(999)

        # Verify the exception carries the correct student_id
        assert exc_info.value.student_id == 999

    # ─────────────────────────────────────────────────────────────────────────
    # Exercise 5: No database, no Docker, no environment variables required
    # ─────────────────────────────────────────────────────────────────────────

    def test_runs_without_database(
        self,
        service: StudentService,
        mock_repo: MagicMock,
        existing_student: Student_response_model,
    ):
        """
        Exercise 5: Prove PostgreSQL is completely absent from this test.

        The mock_repo fixture never opens a database connection.
        There is no .env dependency, no Docker socket, no network call.
        This test passes on any machine that has Python + pytest installed.

        The mock.called attribute confirms we went through the service logic
        (the method was actually invoked on the mock) without touching real storage.
        """
        mock_repo.get_student_by_id.return_value = existing_student

        result = service.get_student_by_id(1)

        # Verify the mock was called (service reached out to the repository)
        assert mock_repo.get_student_by_id.called, (
            "Service should have called repository.get_student_by_id — "
            "but the mock was never invoked."
        )
        # Verify the result is correct
        assert result.id == 1

    # ─────────────────────────────────────────────────────────────────────────
    # Exercise 6: Verify repository interaction contract
    # ─────────────────────────────────────────────────────────────────────────

    def test_calls_repository_with_correct_id(
        self,
        service: StudentService,
        mock_repo: MagicMock,
        existing_student: Student_response_model,
    ):
        """
        Exercise 6: Interaction test — was the repository called correctly?

        Beyond testing the returned value, we also test:
          - Was get_student_by_id called?   → assert_called_once_with
          - Was it called with the right argument (id=1)?
          - Was it called exactly ONCE (not zero times, not twice)?

        This establishes the Service ↔ Repository interaction contract.
        If a future refactor accidentally passes the wrong id or calls the
        wrong method, this test will catch it.

        NOTE: Do not over-test implementation details.  We test here because
        the correct id is a meaningful part of the observable behaviour, not
        just an implementation detail.
        """
        mock_repo.get_student_by_id.return_value = existing_student

        service.get_student_by_id(1)

        # Verify: called exactly once with exactly the right argument
        mock_repo.get_student_by_id.assert_called_once_with(1)

    def test_different_ids_reach_repository(
        self,
        service: StudentService,
        mock_repo: MagicMock,
        existing_student: Student_response_model,
    ):
        """
        Exercise 6 (extended): Each call forwards the exact id it received.

        Call service with id=42 → mock should be called with 42, not 1 or anything else.
        This ensures the service does not hardcode or transform the id before
        forwarding it to the repository.
        """
        student_42 = Student_response_model(
            id=42, name="Bob", age=25, city="Delhi", email="bob@example.com"
        )
        mock_repo.get_student_by_id.return_value = student_42

        result = service.get_student_by_id(42)

        mock_repo.get_student_by_id.assert_called_once_with(42)
        assert result.id == 42


# ─────────────────────────────────────────────────────────────────────────────
# Additional service method tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAddStudent:
    """Unit tests for StudentService.add_student()."""

    def test_add_student_returns_created_student(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Service delegates to repository and returns the created student.

        The schema validation (StudentSchema.validate_student_name) runs for real
        here — only the repository is mocked.  This tests both the validation
        and the delegation chain without hitting a database.
        """
        expected = Student_response_model(
            id=10, name="Charlie", age=21, city="Pune", email="charlie@example.com"
        )
        mock_repo.add_student.return_value = expected

        result = service.add_student(
            name="Charlie", age=21, city="Pune", email="charlie@example.com"
        )

        assert result == expected
        # Repository must have been called once (with a Student_model — verify via call_count)
        assert mock_repo.add_student.call_count == 1

    def test_add_student_raises_value_error_for_empty_name(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Name validation inside StudentSchema raises ValueError for blank names.

        The repository should NOT be called — validation failure is caught before
        the persistence layer is ever reached.
        """
        with pytest.raises(ValueError):
            service.add_student(
                name="   ",  # whitespace-only name fails validation
                age=20,
                city="Chennai",
                email="test@example.com",
            )

        # The repository must not have been touched at all
        mock_repo.add_student.assert_not_called()


class TestGetAllStudents:
    """Unit tests for StudentService.get_all_students()."""

    def test_returns_empty_list_when_no_students(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """Service correctly passes through an empty list from the repository."""
        mock_repo.get_all_students.return_value = []

        result = service.get_all_students()

        assert result == []
        mock_repo.get_all_students.assert_called_once()

    def test_returns_all_students_from_repository(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """Service returns all students exactly as the repository provides them."""
        students = [
            Student_response_model(id=1, name="A", age=18, city="X", email="a@x.com"),
            Student_response_model(id=2, name="B", age=19, city="Y", email="b@y.com"),
        ]
        mock_repo.get_all_students.return_value = students

        result = service.get_all_students()

        assert len(result) == 2
        assert result[0].name == "A"
        assert result[1].name == "B"


class TestDeleteStudent:
    """Unit tests for StudentService.delete_student()."""

    def test_delete_student_success(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        When repository reports deletion succeeded (True), service completes silently.
        No exception should be raised.
        """
        mock_repo.delete_student.return_value = True

        # Should not raise
        service.delete_student(1)

        mock_repo.delete_student.assert_called_once_with(1)

    def test_delete_student_raises_not_found_when_missing(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        When repository returns False (student not found), service raises
        StudentNotFoundException.  This mirrors the get_student_by_id behaviour.
        """
        mock_repo.delete_student.return_value = False

        with pytest.raises(StudentNotFoundException) as exc_info:
            service.delete_student(99)

        assert exc_info.value.student_id == 99
