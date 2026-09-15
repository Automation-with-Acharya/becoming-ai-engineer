"""
test_student_service.py - Unit tests for StudentService.

Day 033 Exercises: 3, 4, 5, 6.
Day 035 Exercises: 2 (@pytest.mark.unit), 3 (parametrize), 6 (regression test).

WHY unit tests?
---------------
A unit test isolates exactly one class (StudentService) and replaces all
collaborators (StudentRepository) with controlled fakes (MagicMock).

Result: tests run in milliseconds, require NO database, NO Docker, NO network,
and NO environment variables.  They only test the business logic inside
StudentService itself.

Architecture reminder:
  Test
    |
  StudentService          <- what we are testing
    |
  MagicMock (repository)  <- controlled fake
    |
  (no database)           <- PostgreSQL is completely absent

Day 035 additions:
  - @pytest.mark.unit applied to every test class.
  - Exercise 3: TestValidationParametrize proves "one rule, many invalid inputs"
    with @pytest.mark.parametrize instead of one test per case.
  - Exercise 6: TestRegressionBlankNameNotPersistedToDB — permanent regression
    guard preventing the blank-name-leaks-to-DB bug from being re-introduced.
"""

import pytest
from unittest.mock import MagicMock

from services.student_service import StudentService
from models.student import Student_response_model
from exceptions import StudentNotFoundException


# ---------------------------------------------------------------------------
# Local fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_repo() -> MagicMock:
    """
    Return a MagicMock acting as a StudentRepository.

    MagicMock automatically creates attributes/methods on first access,
    so we only need to configure the return values we care about per test.
    The real PostgresStudentRepository (and therefore PostgreSQL) is never
    instantiated.
    """
    return MagicMock()


@pytest.fixture
def service(mock_repo: MagicMock) -> StudentService:
    """
    Return a StudentService wired with the mock repository.

    Mirrors the production wiring:
      StudentService(repository=PostgresStudentRepository(db_helper))
    but the repository is a mock - no DB connection is made.
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


# ---------------------------------------------------------------------------
# Day 033 Exercise 3: Service returns student when repository finds one
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetStudentById:
    """
    Unit tests for StudentService.get_student_by_id().

    Day 035 Exercise 2: @pytest.mark.unit — run with `pytest -m unit -v`.
    """

    def test_returns_student_when_found(
        self,
        service: StudentService,
        mock_repo: MagicMock,
        existing_student: Student_response_model,
    ):
        """
        Exercise 3: Happy path - repository returns a student, service passes it through.

        Flow:
          Test configures mock_repo.get_student_by_id(1) -> existing_student
          |
          service.get_student_by_id(1) calls mock_repo
          |
          Service returns the student unchanged (no transformation needed here)
          |
          Assert: returned object equals the expected student

        PostgreSQL: NOT involved.  The mock replaces the entire repository.
        """
        # ARRANGE - tell the mock what to return when called with id=1
        mock_repo.get_student_by_id.return_value = existing_student

        # ACT - call the real service method
        result = service.get_student_by_id(1)

        # ASSERT - service should return whatever the repository gave it
        assert result == existing_student
        assert result.id == 1
        assert result.name == "Alice Test"

    def test_raises_student_not_found_when_missing(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Exercise 4: Not-found path - repository returns None, service raises.

        Contract proven here:
          Repository says:  None  (student does not exist)
          Service says:     StudentNotFoundException
          Global handler:   HTTP 404  (tested separately in api/ tests)

        This is Clean Architecture separation in action:
          - The service does NOT return None to the caller.
          - It raises a domain exception instead.
          - The router stays free of manual None-checks.
          - The global handler converts the domain exception to an HTTP response.
        """
        # ARRANGE - simulate "student not in database"
        mock_repo.get_student_by_id.return_value = None

        # ACT + ASSERT - the service must raise StudentNotFoundException
        with pytest.raises(StudentNotFoundException) as exc_info:
            service.get_student_by_id(999)

        # Verify the exception carries the correct student_id
        assert exc_info.value.student_id == 999

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
        without touching real storage.
        """
        mock_repo.get_student_by_id.return_value = existing_student

        result = service.get_student_by_id(1)

        # Verify the mock was called (service reached out to the repository)
        assert mock_repo.get_student_by_id.called, (
            "Service should have called repository.get_student_by_id - "
            "but the mock was never invoked."
        )
        assert result.id == 1

    def test_calls_repository_with_correct_id(
        self,
        service: StudentService,
        mock_repo: MagicMock,
        existing_student: Student_response_model,
    ):
        """
        Exercise 6: Interaction test - was the repository called correctly?

        Beyond testing the returned value, we also test:
          - Was get_student_by_id called?   -> assert_called_once_with
          - Was it called with the right argument (id=1)?
          - Was it called exactly ONCE (not zero times, not twice)?

        This establishes the Service <-> Repository interaction contract.
        If a future refactor accidentally passes the wrong id or calls the
        wrong method, this test will catch it.
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

        Call service with id=42 -> mock should be called with 42, not 1 or anything else.
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


# ---------------------------------------------------------------------------
# Day 033 + Day 035: add_student tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddStudent:
    """
    Unit tests for StudentService.add_student().

    Day 035 Exercise 2: @pytest.mark.unit applied.
    """

    def test_add_student_returns_created_student(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Service delegates to repository and returns the created student.

        The schema validation (StudentSchema.validate_student_name) runs for real
        here - only the repository is mocked.  This tests both the validation
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
        # Repository must have been called once (with a Student_model)
        assert mock_repo.add_student.call_count == 1

    def test_add_student_raises_value_error_for_empty_name(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Name validation inside StudentSchema raises ValueError for blank names.

        The repository should NOT be called - validation failure is caught before
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


# ---------------------------------------------------------------------------
# Day 033 + Day 035: get_all_students tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetAllStudents:
    """
    Unit tests for StudentService.get_all_students().

    Day 035 Exercise 2: @pytest.mark.unit applied.
    """

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


# ---------------------------------------------------------------------------
# Day 033 + Day 035: delete_student tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDeleteStudent:
    """
    Unit tests for StudentService.delete_student().

    Day 035 Exercise 2: @pytest.mark.unit applied.
    """

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


# ---------------------------------------------------------------------------
# Day 035 Exercise 3: Parametrized validation tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestValidationParametrize:
    """
    Day 035 Exercise 3: "One behavior, many examples" via @pytest.mark.parametrize.

    Instead of writing a separate test method for each invalid name, we
    express the single rule — blank names are rejected — with a list of
    representative invalid inputs.

    This is not about reducing line count.  It is about making the test
    document the complete set of cases that share the same rule, and making
    it trivial to add new edge cases in the future.

    Rule: name is whitespace-only or empty -> ValueError, repository not called.
    """

    @pytest.mark.parametrize("invalid_name", [
        "",           # completely empty string
        " ",          # single space
        "   ",        # multiple spaces
        "\t",         # tab character
        "\n",         # newline
        "\t\n  \t",    # mixed whitespace
    ], ids=[
        "empty_string",
        "single_space",
        "multi_space",
        "tab",
        "newline",
        "mixed_whitespace",
    ])
    def test_blank_name_raises_value_error(
        self,
        invalid_name: str,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Exercise 3: Any whitespace-only or empty name must raise ValueError.

        Each parametrize case runs as its own named test, e.g.:
          test_blank_name_raises_value_error[empty_string]
          test_blank_name_raises_value_error[single_space]
          ...

        If any one of these inputs slips through validation and reaches the
        repository, the assert_not_called() assertion below will catch it.
        """
        with pytest.raises(ValueError):
            service.add_student(
                name=invalid_name,
                age=20,
                city="City",
                email="valid@example.com",
            )

        # The repository must NEVER be called for any invalid name
        mock_repo.add_student.assert_not_called()

    @pytest.mark.parametrize("valid_name,expected_clean", [
        ("Alice", "Alice"),             # already clean
        ("  Bob  ", "Bob"),             # leading/trailing whitespace stripped
        ("  Carol Smith  ", "Carol Smith"),  # internal whitespace preserved
    ], ids=["plain_name", "padded_name", "name_with_space"])
    def test_valid_name_is_accepted(
        self,
        valid_name: str,
        expected_clean: str,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Exercise 3: Valid (non-blank) names are accepted and cleaned.

        Complements the invalid-name parametrize test to document the full
        rule boundary: blank -> error, non-blank -> cleaned and forwarded.
        """
        expected = Student_response_model(
            id=1, name=expected_clean, age=20, city="City",
            email="valid@example.com",
        )
        mock_repo.add_student.return_value = expected

        result = service.add_student(
            name=valid_name, age=20, city="City", email="valid@example.com"
        )

        assert result.name == expected_clean
        assert mock_repo.add_student.call_count == 1


# ---------------------------------------------------------------------------
# Day 035 Exercise 6: High-value regression test
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRegressionBlankNameNotPersistedToDb:
    """
    Day 035 Exercise 6: Permanent regression guard for the blank-name bug.

    BUG SCENARIO:
      If StudentSchema.validate_student_name() failed silently (returned the
      blank string instead of raising ValueError), the blank name would reach
      the repository and be persisted to the database.  A student with
      name='' or name='   ' would then exist in PostgreSQL, violating the
      NOT NULL + meaningful-content invariant of the business domain.

    This test answers the regression question:
      "If someone accidentally removes the validation from StudentSchema or
      StudentService six months from now, will pytest catch it?"

    The answer is YES - this test directly verifies the exact call path:
      add_student(name='   ') -> ValueError raised BEFORE repository.add_student()

    What this test protects:
      - The validation guard in StudentSchema.validate_student_name().
      - The fact that StudentService calls the schema BEFORE the repository.
      - The fact that a ValueError propagates UP without being swallowed.

    Without this test, removing or silencing the validation would go
    undetected until someone queries the database or hits the API with a
    blank name manually.
    """

    def test_blank_name_does_not_reach_repository(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Regression: blank name raises ValueError; repository.add_student() is never called.

        This is the core regression assertion:
          service.add_student(name='   ')
            -> StudentSchema.validate_student_name('   ')
            -> ValueError: "Name cannot be empty."
            -> add_student() returns (exception propagates)
          repository.add_student() was NEVER called.

        If the validation is removed/broken in the future, this test fails with:
          AssertionError: Expected 'add_student' to not have been called.
        """
        with pytest.raises(ValueError, match="(?i)empty"):
            service.add_student(
                name="   ",   # blank name - the regression trigger
                age=25,
                city="Regression City",
                email="regression@example.com",
            )

        mock_repo.add_student.assert_not_called()

    def test_whitespace_only_name_never_inserted_to_db(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Regression variant: tab/newline characters also prevented from reaching DB.

        Real-world input is messy.  A tab character or newline in a name field
        is just as problematic as a pure space.  This regression test locks in
        that the validation covers these cases too.
        """
        for bad_name in ["\t", "\n", "  \t  "]:
            with pytest.raises(ValueError):
                service.add_student(
                    name=bad_name,
                    age=20,
                    city="City",
                    email="bad@example.com",
                )

        # Repository must have received ZERO calls across all iterations
        mock_repo.add_student.assert_not_called()

    def test_empty_string_name_raises_not_falls_through(
        self,
        service: StudentService,
        mock_repo: MagicMock,
    ):
        """
        Regression: an empty string '' also triggers ValueError (not silently accepted).

        An empty string is distinct from whitespace — both are invalid, but
        the code path through validate_student_name() differs slightly
        (first check: `if not name` catches '', second check catches whitespace).
        This test locks in both paths.
        """
        with pytest.raises(ValueError):
            service.add_student(
                name="",
                age=20,
                city="City",
                email="empty@example.com",
            )
        mock_repo.add_student.assert_not_called()
