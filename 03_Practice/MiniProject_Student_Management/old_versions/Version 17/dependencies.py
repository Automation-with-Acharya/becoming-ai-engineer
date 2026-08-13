"""
Dependency Injection Module.

This module defines FastAPI dependency providers for all layers of our clean architecture:
Database (DatabaseHelper) -> Repository (StudentRepository) -> Service (StudentService).

Why is Dependency Injection (DI) required and beneficial?
---------------------------------------------------------
1. Decoupling: Components do not instantiate their own dependencies. For example, StudentService 
   doesn't need to know how PostgresStudentRepository is created or how DatabaseHelper connects.
2. Single Responsibility: Each class focuses solely on its own business or data logic, not 
   on wire-up logic or configuration parsing.
3. Testability (Mocking/Stubbing): By using FastAPI's dependency injection system, we can 
   override any dependency during testing. For example, during a test we can override 
   `get_student_repository` to return a mock database or an in-memory repository without 
   altering the router or service implementation.
4. Lifetime Management: FastAPI manages the lifecycle of resources. A connection or helper 
   can be created once and shared safely, or a session can be opened and closed per request.
"""

from fastapi import Depends
from database.database_helper import DatabaseHelper
from repositories.student_repository import StudentRepository, PostgresStudentRepository
from services.student_service import StudentService

# Initialize a single, global DatabaseHelper instance (singleton pattern).
# This single instance will hold our database connection pool or persistent connection.
# We will manage its connection state (connect/close) during the application lifespan in main.py.
_db_helper = DatabaseHelper()


def get_db_helper() -> DatabaseHelper:
    """
    Dependency provider to retrieve the application-wide DatabaseHelper instance.

    Why is this required?
    --------------------
    It acts as a single point of access to the database configuration. Any database operation
    will require access to the helper. Rather than importing a global helper directly in the 
    repository, injecting it via this function allows us to substitute it (e.g., with a test db helper)
    during test runs.
    """
    return _db_helper


def get_student_repository(
    db_helper: DatabaseHelper = Depends(get_db_helper)
) -> StudentRepository:
    """
    Dependency provider to retrieve a StudentRepository instance.

    Why is this required?
    --------------------
    Following the SOLID Dependency Inversion Principle, components should depend on abstractions,
    not concretions. This function returns the abstract StudentRepository interface but instantiates
    the concrete PostgresStudentRepository under the hood. 
    This enables us to swap out PostgresStudentRepository with another repository implementation 
    (e.g., MongoStudentRepository) by only modifying this single function.
    """
    return PostgresStudentRepository(db_helper)


def get_student_service(
    repository: StudentRepository = Depends(get_student_repository)
) -> StudentService:
    """
    Dependency provider to retrieve a StudentService instance.

    Why is this required?
    --------------------
    The API router layer handles incoming HTTP requests and responses, but should not contain business logic.
    Instead, it delegates business tasks to the StudentService. Injecting StudentService via this function 
    ensures the router is provided with a service that has its repository layer already correctly wired.
    """
    return StudentService(repository)
