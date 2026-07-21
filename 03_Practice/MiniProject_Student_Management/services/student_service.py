"""
Student Service Module.

This module contains business logic for Student operations.
Coordinates schema validation and delegates persistence tasks to StudentRepository.
"""

from models.student import Student
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

    def add_student(self, name: str) -> Student:
        """
        Validate student name and add student to storage.

        Args:
            name (str): Raw student name input.

        Returns:
            Student: Created Student model instance.

        Raises:
            ValueError: If student name is empty or invalid.
        """
        cleaned_name = StudentSchema.validate_student_name(name)
        student = Student(name=cleaned_name)
        return self.repository.add_student(student)

    def get_all_students(self) -> list[Student]:
        """
        Retrieve all registered students.

        Returns:
            list[Student]: List of all student records.
        """
        return self.repository.get_all_students()

    def get_student_by_id(self, student_id: int) -> Student | None:
        """
        Retrieve a student by unique ID.

        Args:
            student_id (int): Student ID.

        Returns:
            Student | None: Student object if found, otherwise None.
        """
        return self.repository.get_student_by_id(student_id)

    def search_students(self, query: str) -> list[Student]:
        """
        Search for students by name query.

        Args:
            query (str): Search string.

        Returns:
            list[Student]: List of matching Student objects.
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
