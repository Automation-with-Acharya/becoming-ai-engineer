"""
Student Service Module.

This module contains business logic for Student operations.
Coordinates schema validation and delegates persistence tasks to StudentRepository.

Return types use Student_response_model (not Student_model) because:
  - After a student is saved/retrieved from the database, it always has a valid, non-None id.
  - Student_response_model enforces id as a required int, accurately reflecting that guarantee.
  - Student_model (with id: int | None) is only used for the incoming request body shape.

Day 017 Update: Structured logging added for all service operations and exception paths.
"""

from models.student import Student_model, Student_response_model
from schemas.student_schema import StudentSchema
from repositories.student_repository import StudentRepository
from logger_config import get_logger

logger = get_logger(__name__)


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
        logger.info(
            "Service: add_student called — name='%s', age=%s, city='%s', email='%s'",
            name, age, city, email,
        )
        try:
            cleaned_name = StudentSchema.validate_student_name(name)
            # Build a Student_model (id=None) to pass down to the repository.
            # The repository will assign the id and return a Student_response_model.
            student = Student_model(name=cleaned_name, age=age, city=city, email=email)
            result = self.repository.add_student(student)
            logger.info("Service: Student added successfully — id=%d, name='%s'", result.id, result.name)
            return result
        except ValueError as exc:
            # Exercise 4: Log validation failures as warnings (these are user errors, not system errors)
            logger.warning("Service: Validation failed for add_student — %s", str(exc))
            raise
        except Exception:
            # Exercise 4: Unexpected errors get full stack trace via logger.exception()
            logger.exception("Service: Unexpected error in add_student — name='%s'", name)
            raise

    def get_all_students(self) -> list[Student_response_model]:
        """
        Retrieve all registered students.

        Returns:
            list[Student_response_model]: List of all student records, each with a valid id.
        """
        logger.debug("Service: get_all_students called.")
        try:
            result = self.repository.get_all_students()
            logger.info("Service: get_all_students returned %d student(s).", len(result))
            return result
        except Exception:
            logger.exception("Service: Unexpected error in get_all_students.")
            raise

    def get_student_by_id(self, student_id: int) -> Student_response_model | None:
        """
        Retrieve a student by unique ID.

        Args:
            student_id (int): Student ID.

        Returns:
            Student_response_model | None: Student object with valid id if found, otherwise None.
        """
        logger.debug("Service: get_student_by_id called — id=%d.", student_id)
        try:
            result = self.repository.get_student_by_id(student_id)
            if result is None:
                logger.warning("Service: Student with id=%d not found.", student_id)
            else:
                logger.debug("Service: Found student id=%d, name='%s'.", result.id, result.name)
            return result
        except Exception:
            logger.exception("Service: Unexpected error in get_student_by_id — id=%d.", student_id)
            raise

    def search_students(self, query: str) -> list[Student_response_model]:
        """
        Search for students by name query.

        Args:
            query (str): Search string.

        Returns:
            list[Student_response_model]: List of matching Student objects, each with a valid id.
        """
        cleaned_query = query.strip() if query else ""
        logger.info("Service: search_students called — query='%s'.", cleaned_query)
        try:
            result = self.repository.search_students(cleaned_query)
            logger.info("Service: Search '%s' returned %d match(es).", cleaned_query, len(result))
            return result
        except Exception:
            logger.exception("Service: Unexpected error in search_students — query='%s'.", cleaned_query)
            raise

    def delete_student(self, student_id: int) -> bool:
        """
        Delete a student by unique ID.

        Args:
            student_id (int): Student ID to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        logger.info("Service: delete_student called — id=%d.", student_id)
        try:
            result = self.repository.delete_student(student_id)
            if result:
                logger.info("Service: Student id=%d deleted successfully.", student_id)
            else:
                logger.warning("Service: Delete skipped — student id=%d not found.", student_id)
            return result
        except Exception:
            logger.exception("Service: Unexpected error in delete_student — id=%d.", student_id)
            raise
