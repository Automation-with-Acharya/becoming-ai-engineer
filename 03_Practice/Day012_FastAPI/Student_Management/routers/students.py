from fastapi import APIRouter, Depends, HTTPException

try:
    from Student_Management.models import Student_model, StudentResponse
    from Student_Management.services.student_service import StudentService, get_student_service
except ImportError:  # pragma: no cover - allows running the module directly
    from models.models import Student_model, StudentResponse
    from services.student_service import StudentService, get_student_service

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentResponse])
def get_students(
    city: str | None = None,
    service: StudentService = Depends(get_student_service),
):
    """Return all students or only those in the requested city."""
    return service.get_all_students(city)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student_by_id(
    student_id: int,
    service: StudentService = Depends(get_student_service),
):
    """Return a single student by numeric index ID."""
    student = service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("", response_model=dict)
def add_student(
    student: Student_model,
    service: StudentService = Depends(get_student_service),
):
    """Add a new student and return a success message."""
    return service.add_student(student)
