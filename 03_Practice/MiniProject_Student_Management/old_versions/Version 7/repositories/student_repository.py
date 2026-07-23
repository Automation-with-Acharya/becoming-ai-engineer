"""
Student Repository Module.

This module implements the Repository Pattern for Student entity data access on PostgreSQL.
Decouples database operations from higher-level business logic.
"""

from abc import ABC, abstractmethod
from models.student import Student
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
    def add_student(self, student: Student) -> Student:
        """
        Add a new student to storage.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_students(self) -> list[Student]:
        """
        Retrieve all students from storage.
        """
        raise NotImplementedError

    @abstractmethod
    def get_student_by_id(self, student_id: int) -> Student | None:
        """
        Retrieve a student by their unique ID from storage.
        """
        raise NotImplementedError

    @abstractmethod
    def search_students(self, query: str) -> list[Student]:
        """
        Search for students using a name/query string.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_student(self, student_id: int) -> bool:
        """
        Delete a student from storage.
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

    def add_student(self, student: Student) -> Student:
        """
        Add a new student to PostgreSQL database and generate unique ID.

        Args:
            student (Student): Student object containing student name.

        Returns:
            Student: Student object with assigned ID.
        """
        # Calculate next available ID
        next_id_row = self.db_helper.fetch_one(
            "SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM students"
        )
        student.id = next_id_row[0] if next_id_row else 1

        # Insert student into database
        self.db_helper.execute_query(
            "INSERT INTO students (id, name, age, city) VALUES (%s, %s, %s, %s)",
            (student.id, student.name, student.age, student.city),
            commit=True,
        )
        return student

    def get_all_students(self) -> list[Student]:
        """
        Retrieve all student records from PostgreSQL database.

        Returns:
            list[Student]: List of Student model objects.
        """
        rows = self.db_helper.fetch_all("SELECT * FROM students ORDER BY id")
        return [Student(id=row[0], name=row[1], age=row[2], city=row[3]) for row in rows]

    def get_student_by_id(self, student_id: int) -> Student | None:
        """
        Retrieve a student by their unique ID.

        Args:
            student_id (int): Student ID to look up.

        Returns:
            Student | None: Student instance if found, otherwise None.
        """
        row = self.db_helper.fetch_one(
            "SELECT * FROM students WHERE id = %s",
            (student_id,),
        )
        if row is None:
            return None
        return Student(id=row[0], name=row[1], age=row[2], city=row[3])

    def search_students(self, name_input: str) -> list[Student]:
        """
        Search students by name using case-insensitive ILIKE pattern matching.

        Args:
            name_input (str): Name query string.

        Returns:
            list[Student]: List of matching Student objects.
        """
        rows = self.db_helper.fetch_all(
            "SELECT * FROM students WHERE name ILIKE %s ORDER BY id",
            (f"%{name_input}%",),
        )
        return [Student(id=row[0], name=row[1], age=row[2], city=row[3]) for row in rows]

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
