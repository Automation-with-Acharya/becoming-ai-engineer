"""
Student Service Module.

This module contains business logic for Student operations.
Coordinates schema validation and delegates persistence tasks to StudentRepository.

Return types use Student_response_model (not Student_model) because:
  - After a student is saved/retrieved from the database, it always has a valid, non-None id.
  - Student_response_model enforces id as a required int, accurately reflecting that guarantee.
  - Student_model (with id: int | None) is only used for the incoming request body shape.
"""

from models.student import Student_model, Student_response_model
from schemas.student_schema import StudentSchema
from repositories.student_repository import StudentRepository


class StudentService:
    """
    Service class managing business logic for Student entity operations.
    """

    def __init__(self, repository: StudentRepository):
        """
        Initialize StudentService with a StudentRepository.

        Args:
            repository (StudentRepository): Repository instance handling storage.
        """
        self.repository = repository

    def add_student(self, name: str, age: int, city: str, email: str) -> Student_response_model:
        """
        Validate student name and add student to storage.

        Args:
            name (str): Raw student name input.
            age (int): Student's age.
            city (str): Student's city.
            email (str): Student's email address.

        Returns:
            Student_response_model: Created Student instance with database-assigned id.

        Raises:
            ValueError: If student name is empty or invalid.
        """
        cleaned_name = StudentSchema.validate_student_name(name)
        # Build a Student_model (id=None) to pass down to the repository.
        # The repository will assign the id and return a Student_response_model.
        student = Student_model(name=cleaned_name, age=age, city=city, email=email)
        return self.repository.add_student(student)

    def get_all_students(self) -> list[Student_response_model]:
        """
        Retrieve all registered students.

        Returns:
            list[Student_response_model]: List of all student records, each with a valid id.
        """
        return self.repository.get_all_students()

    def get_student_by_id(self, student_id: int) -> Student_response_model | None:
        """
        Retrieve a student by unique ID.

        Args:
            student_id (int): Student ID.

        Returns:
            Student_response_model | None: Student object with valid id if found, otherwise None.
        """
        return self.repository.get_student_by_id(student_id)

    def search_students(self, query: str) -> list[Student_response_model]:
        """
        Search for students by name query.

        Args:
            query (str): Search string.

        Returns:
            list[Student_response_model]: List of matching Student objects, each with a valid id.
        """
        cleaned_query = query.strip() if query else ""
        return self.repository.search_students(cleaned_query)

    def delete_student(self, student_id: int) -> bool:
        """
        Delete a student by unique ID.

        Args:
            student_id (int): Student ID to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        return self.repository.delete_student(student_id)
