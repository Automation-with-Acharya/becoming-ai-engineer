"""
Student Repository Module.

This module implements the Repository Pattern for Student entity data access on PostgreSQL.
Decouples database operations from higher-level business logic.

Return types use Student_response_model (not Student_model) because:
  - The repository is responsible for persisting data and fetching it from the database.
  - Once a record is inserted or fetched, it always has a database-assigned id (never None).
  - Student_response_model enforces id as a required int, accurately reflecting that guarantee.
  - Student_model (with id: int | None) is accepted as input (for add_student) because the
    caller (service layer) constructs it before the id is known.

Day 017 Update: Structured logging added for all CRUD operations and exception paths.
Day 020 Update: Write operations (add_student, delete_student) now use explicit ACID transactions
                via execute_write_transaction() and execute_write() in DatabaseHelper.
                - add_student: ID-fetch + INSERT run atomically in one transaction (no race condition).
                - delete_student: DELETE wrapped in execute_write() for guaranteed rollback on failure.
"""

from abc import ABC, abstractmethod
from models.student import Student_model, Student_response_model
from database.database_helper import DatabaseHelper
from logger_config import get_logger

logger = get_logger(__name__)


class StudentRepository(ABC):
    """
    Abstract interface defining the contract for Student repository operations.

    WHY IS THIS REQUIRED? (Architectural Context)
    --------------------------------------------
    1. Dependency Inversion Principle (DIP): High-level modules (e.g., StudentService)
       should not depend directly on low-level database details (like PostgresStudentRepository).
       Instead, they must depend on this abstraction. This decouples business logic from specific
       storage technologies.
    2. Modularity & Swappability: If we decide to swap our storage backend in the future (e.g.,
       moving from PostgreSQL to MongoDB, Firestore, or an in-memory database), we only need to
       write a new implementation of StudentRepository. The service layer stays untouched.
    3. Testability (Mocking): During unit testing of the service layer, we can easily inject
       a mock repository that inherits from StudentRepository, avoiding actual database connection setup
       during testing.
    """

    @abstractmethod
    def add_student(self, student: Student_model) -> Student_response_model:
        """
        Add a new student to storage.

        Args:
            student (Student_model): Request-shaped student data (id may be None).

        Returns:
            Student_response_model: The persisted student with a database-assigned id.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_students(self) -> list[Student_response_model]:
        """
        Retrieve all students from storage.

        Returns:
            list[Student_response_model]: List of all student records, each with a valid id.
        """
        raise NotImplementedError

    @abstractmethod
    def get_student_by_id(self, student_id: int) -> Student_response_model | None:
        """
        Retrieve a student by their unique ID from storage.

        Args:
            student_id (int): The student's unique identifier.

        Returns:
            Student_response_model | None: Found student (with valid id), or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def search_students(self, query: str) -> list[Student_response_model]:
        """
        Search for students using a name/query string.

        Args:
            query (str): Name search string.

        Returns:
            list[Student_response_model]: Matching students, each with a valid id.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_student(self, student_id: int) -> bool:
        """
        Delete a student from storage.

        Args:
            student_id (int): ID of the student to delete.

        Returns:
            bool: True if deleted successfully, False if not found.
        """
        raise NotImplementedError


class PostgresStudentRepository(StudentRepository):
    """
    PostgreSQL repository implementation managing CRUD operations for Students.
    """

    def __init__(self, db_helper: DatabaseHelper):
        """
        Initialize PostgresStudentRepository with DatabaseHelper instance.

        Args:
            db_helper (DatabaseHelper): Instance of DatabaseHelper for DB operations.
        """
        self.db_helper = db_helper

    def add_student(self, student: Student_model) -> Student_response_model:
        """
        Add a new student to PostgreSQL database and generate unique ID.

        Day 020: The ID-generation SELECT and the INSERT are now wrapped in a single
        ACID transaction via execute_write_transaction(). This means:
          - Both statements either succeed together or are rolled back together.
          - No other concurrent writer can claim the same ID between the SELECT and INSERT.
          - If the INSERT violates a constraint (e.g., duplicate ID), the whole transaction
            is rolled back cleanly, leaving the DB in its prior state.

        Args:
            student (Student_model): Student object with name, age, city (id is None at this point).

        Returns:
            Student_response_model: Student object with the database-assigned id.

        Raises:
            Exception: Re-raises any database error after logging and rolling back.
        """
        logger.info("Repository: Creating student — name='%s'", student.name)
        try:
            # Day 020: Both steps run inside one atomic transaction.
            # `execute_write_transaction` opens BEGIN, runs the lambda with a cursor,
            # then issues COMMIT on success or ROLLBACK on any exception.
            def _create(cur):
                # Step 1: Calculate the next available ID
                cur.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM students")
                assigned_id = cur.fetchone()[0]

                # Step 2: Insert the new student record — same cursor, same transaction
                cur.execute(
                    "INSERT INTO students (id, name, age, city, email) VALUES (%s, %s, %s, %s, %s)",
                    (assigned_id, student.name, student.age, student.city, student.email),
                )
                return assigned_id

            assigned_id = self.db_helper.execute_write_transaction(_create)

            logger.info(
                "Repository: Student created successfully — id=%d, name='%s'",
                assigned_id, student.name,
            )
            return Student_response_model(
                id=assigned_id, name=student.name,
                age=student.age, city=student.city, email=student.email,
            )
        except Exception:
            logger.exception(
                "Repository: Failed to create student — name='%s'", student.name
            )
            raise

    def get_all_students(self) -> list[Student_response_model]:
        """
        Retrieve all student records from PostgreSQL database.

        Returns:
            list[Student_response_model]: List of Student response model objects.
        """
        logger.debug("Repository: Fetching all students.")
        try:
            rows = self.db_helper.fetch_all("SELECT * FROM students ORDER BY id")
            logger.info("Repository: Retrieved %d student(s).", len(rows))
            return [
                Student_response_model(id=row[0], name=row[1], age=row[2], city=row[3], email=row[4])
                for row in rows
            ]
        except Exception:
            logger.exception("Repository: Failed to fetch all students.")
            raise

    def get_student_by_id(self, student_id: int) -> Student_response_model | None:
        """
        Retrieve a student by their unique ID.

        Args:
            student_id (int): Student ID to look up.

        Returns:
            Student_response_model | None: Student instance if found, otherwise None.
        """
        logger.debug("Repository: Looking up student with id=%d.", student_id)
        try:
            row = self.db_helper.fetch_one(
                "SELECT * FROM students WHERE id = %s",
                (student_id,),
            )
            if row is None:
                logger.warning("Repository: Student with id=%d not found.", student_id)
                return None
            logger.debug("Repository: Found student id=%d, name='%s'.", row[0], row[1])
            return Student_response_model(id=row[0], name=row[1], age=row[2], city=row[3], email=row[4])
        except Exception:
            logger.exception("Repository: Failed to fetch student with id=%d.", student_id)
            raise

    def search_students(self, name_input: str) -> list[Student_response_model]:
        """
        Search students by name using case-insensitive ILIKE pattern matching.

        Args:
            name_input (str): Name query string.

        Returns:
            list[Student_response_model]: List of matching Student response objects.
        """
        logger.debug("Repository: Searching students with query='%s'.", name_input)
        try:
            rows = self.db_helper.fetch_all(
                "SELECT * FROM students WHERE name ILIKE %s ORDER BY id",
                (f"%{name_input}%",),
            )
            logger.info(
                "Repository: Search '%s' returned %d result(s).", name_input, len(rows)
            )
            return [
                Student_response_model(id=row[0], name=row[1], age=row[2], city=row[3], email=row[4])
                for row in rows
            ]
        except Exception:
            logger.exception("Repository: Failed to search students with query='%s'.", name_input)
            raise

    def delete_student(self, student_id: int) -> bool:
        """
        Delete a student record from PostgreSQL database by ID.

        Day 020: The DELETE is executed via execute_write(), which wraps it in an explicit
        ACID transaction with automatic rollback on failure. The existence check (SELECT)
        intentionally remains outside the transaction — it is a read-only guard, and
        performing it inside the same transaction offers no additional benefit here since
        the service layer already raises StudentNotFoundException before we reach this point.

        Args:
            student_id (int): ID of student to delete.

        Returns:
            bool: True if student was deleted, False if student not found.
        """
        logger.info("Repository: Attempting to delete student with id=%d.", student_id)
        try:
            student = self.get_student_by_id(student_id)
            if student is None:
                logger.warning(
                    "Repository: Delete failed — student with id=%d does not exist.", student_id
                )
                return False

            # Day 020: DELETE inside an explicit transaction — rolled back automatically on failure.
            self.db_helper.execute_write(
                "DELETE FROM students WHERE id = %s",
                (student_id,),
            )
            logger.info("Repository: Student id=%d deleted successfully.", student_id)
            return True
        except Exception:
            logger.exception("Repository: Failed to delete student with id=%d.", student_id)
            raise
