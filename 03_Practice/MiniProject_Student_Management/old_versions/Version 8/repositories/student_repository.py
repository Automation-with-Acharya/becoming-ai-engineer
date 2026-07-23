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
"""

from abc import ABC, abstractmethod
from models.student import Student_model, Student_response_model
from database.database_helper import DatabaseHelper


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

        Args:
            student (Student_model): Student object with name, age, city (id is None at this point).

        Returns:
            Student_response_model: Student object with the database-assigned id.
        """
        # Calculate next available ID
        next_id_row = self.db_helper.fetch_one(
            "SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM students"
        )
        assigned_id = next_id_row[0] if next_id_row else 1

        # Insert student into database
        self.db_helper.execute_query(
            "INSERT INTO students (id, name, age, city, email) VALUES (%s, %s, %s, %s, %s)",
            (assigned_id, student.name, student.age, student.city, student.email),
            commit=True,
        )
        # Return a Student_response_model (id is now a required int — guaranteed by the DB insert)
        return Student_response_model(id=assigned_id, name=student.name, age=student.age, city=student.city, email=student.email)

    def get_all_students(self) -> list[Student_response_model]:
        """
        Retrieve all student records from PostgreSQL database.

        Returns:
            list[Student_response_model]: List of Student response model objects.
        """
        rows = self.db_helper.fetch_all("SELECT * FROM students ORDER BY id")
        return [Student_response_model(id=row[0], name=row[1], age=row[2], city=row[3], email=row[4]) for row in rows]

    def get_student_by_id(self, student_id: int) -> Student_response_model | None:
        """
        Retrieve a student by their unique ID.

        Args:
            student_id (int): Student ID to look up.

        Returns:
            Student_response_model | None: Student instance if found, otherwise None.
        """
        row = self.db_helper.fetch_one(
            "SELECT * FROM students WHERE id = %s",
            (student_id,),
        )
        if row is None:
            return None
        return Student_response_model(id=row[0], name=row[1], age=row[2], city=row[3], email=row[4])

    def search_students(self, name_input: str) -> list[Student_response_model]:
        """
        Search students by name using case-insensitive ILIKE pattern matching.

        Args:
            name_input (str): Name query string.

        Returns:
            list[Student_response_model]: List of matching Student response objects.
        """
        rows = self.db_helper.fetch_all(
            "SELECT * FROM students WHERE name ILIKE %s ORDER BY id",
            (f"%{name_input}%",),
        )
        return [Student_response_model(id=row[0], name=row[1], age=row[2], city=row[3], email=row[4]) for row in rows]

    def delete_student(self, student_id: int) -> bool:
        """
        Delete a student record from PostgreSQL database by ID.

        Args:
            student_id (int): ID of student to delete.

        Returns:
            bool: True if student was deleted, False if student not found.
        """
        student = self.get_student_by_id(student_id)
        if student is None:
            return False

        self.db_helper.execute_query(
            "DELETE FROM students WHERE id = %s",
            (student_id,),
            commit=True,
        )
        return True
