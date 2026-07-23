"""
Student Router Module.

This module defines the REST API routes for the Student entity using FastAPI's APIRouter.
It maps incoming HTTP requests to corresponding business operations in the StudentService
and handles HTTP exception mapping.

Why is Dependency Injection (DI) used here?
------------------------------------------
In this router, we inject `StudentService` into each path operation function using FastAPI's `Depends`.
This means:
1. The route handlers do not need to know how to instantiate `StudentService`, `StudentRepository`, or `DatabaseHelper`.
2. It makes path operations easy to unit test by overriding the dependency providers.
3. Decouples the routing layer entirely from the creation and lifecycle of service resources.

Request vs. Response Models:
-----------------------------
- Student_model          : Used for REQUEST bodies (client → server). 'id' is optional/None.
- Student_response_model : Used for RESPONSE bodies (server → client). 'id' is always a required int.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from models.student import Student_model, Student_response_model
from services.student_service import StudentService
from dependencies import get_student_service

# Initialize the router. We prefix all endpoints with '/students' to group related actions together.
router = APIRouter(
    prefix="/students",
    tags=["Students"],
)


@router.post(
    "/",
    response_model=Student_response_model,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Creates a new student profile in the database. Validates the student name prior to insertion."
)
def create_student(
    student_data: Student_model,
    service: StudentService = Depends(get_student_service)
) -> Student_response_model:
    """
    HTTP POST Route to register a new student.

    REQUEST body  : Student_model  (client sends name, age, city, email).
    RESPONSE body : Student_response_model (server sends back the created record with its assigned id).

    Args:
        student_data (Student_model): The request body containing student details.
        service (StudentService): The injected StudentService instance.

    Returns:
        Student_response_model: The created student record populated with database-generated ID.

    HTTP Error Handling:
        - 400 Bad Request: Raised via global exception handlers if student name validation fails.
        - 500 Internal Server Error: Raised if database insert fails.
    """
    # Delegate name validation and insertion to service layer.
    # Any ValueError raised by validation will propagate and be caught by the global
    # exception handler in main.py, producing a consistent HTTP 400 response.
    return service.add_student(
        name=student_data.name,
        age=student_data.age,
        city=student_data.city,
        email=student_data.email
    )


@router.get(
    "/",
    response_model=list[Student_response_model],
    status_code=status.HTTP_200_OK,
    summary="Get all students",
    description="Retrieve a complete list of all registered students."
)
def get_all_students(
    service: StudentService = Depends(get_student_service)
) -> list[Student_response_model]:
    """
    HTTP GET Route to retrieve all student records.

    RESPONSE body : list[Student_response_model] (each student has a guaranteed id).

    Args:
        service (StudentService): The injected StudentService instance.

    Returns:
        list[Student_response_model]: A list of all students. Returns empty list if none registered.
    """
    return service.get_all_students()


@router.get(
    "/search",
    response_model=list[Student_response_model],
    status_code=status.HTTP_200_OK,
    summary="Search students by name",
    description="Search for students with names matching a query using case-insensitive search."
)
def search_students(
    query: str,
    service: StudentService = Depends(get_student_service)
) -> list[Student_response_model]:
    """
    HTTP GET Route to search students by name.

    RESPONSE body : list[Student_response_model] (each matched student has a guaranteed id).

    Args:
        query (str): The search query parameter.
        service (StudentService): The injected StudentService instance.

    Returns:
        list[Student_response_model]: List of students matching the search query.
    """
    return service.search_students(query)


@router.get(
    "/{student_id}",
    response_model=Student_response_model,
    status_code=status.HTTP_200_OK,
    summary="Get a student by ID",
    description="Retrieve a specific student's profile details using their unique integer ID."
)
def get_student_by_id(
    student_id: int,
    service: StudentService = Depends(get_student_service)
) -> Student_response_model:
    """
    HTTP GET Route to find a specific student.

    RESPONSE body : Student_response_model (the found student always has a valid id).

    Args:
        student_id (int): The unique identifier of the student.
        service (StudentService): The injected StudentService.

    Returns:
        Student_response_model: The found student model.

    HTTP Error Handling:
        - 404 Not Found: Raised if a student with the given ID does not exist in the database.
    """
    student = service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return student


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a student by ID",
    description="Permanently delete a student's profile record from the database."
)
def delete_student(
    student_id: int,
    service: StudentService = Depends(get_student_service)
):
    """
    HTTP DELETE Route to remove a student.

    No request body is needed (student_id comes from the URL path).
    No Student response model is used here — the response is a plain confirmation dict.

    Args:
        student_id (int): Unique identifier of the student to delete.
        service (StudentService): Injected StudentService.

    Returns:
        dict: Confirmation message of successful deletion.

    HTTP Error Handling:
        - 404 Not Found: Raised if a student with the given ID does not exist.
    """
    deleted = service.delete_student(student_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found. Deletion failed."
        )
    return {"message": f"Student with ID {student_id} deleted successfully."}
