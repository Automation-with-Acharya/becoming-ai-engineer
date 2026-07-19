from fastapi import FastAPI, HTTPException

from models import Student, StudentCreate

app = FastAPI(
    title="Student API v1",
    description="A simple in-memory Student API for learning FastAPI basics.",
    version="1.0.0",
)

students: list[Student] = [
    Student(id=1, name="Alice", age=20, city="Delhi"),
    Student(id=2, name="Bob", age=22, city="Mumbai"),
]


@app.get("/", tags=["General"])
async def root() -> dict[str, str]:
    """Return a welcome message for the API."""
    return {"message": "Welcome to Student API v1"}


@app.get("/students", response_model=list[Student], tags=["Students"])
async def get_students() -> list[Student]:
    """Return all students stored in memory."""
    return students


@app.get("/students/{student_id}", response_model=Student, tags=["Students"])
async def get_student(student_id: int) -> Student:
    """Return one student by ID."""
    for student in students:
        if student.id == student_id:
            return student
    raise HTTPException(status_code=404, detail="Student not found")


@app.post("/students", response_model=Student, status_code=201, tags=["Students"])
async def create_student(student: StudentCreate) -> Student:
    """Create a new student and store it in memory."""
    new_student = Student(
        id=max(student.id for student in students) + 1,
        name=student.name,
        age=student.age,
        city=student.city,
    )
    students.append(new_student)
    return new_student

