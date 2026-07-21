
from fastapi import FastAPI
from models import Student_model, StudentResponse



app = FastAPI()

# A small in-memory student list to demonstrate the endpoints.
students = [
    Student_model(name="Asha", age=20, city="Ahmedabad"),
    Student_model(name="Vikram", age=22, city="Mumbai"),
    Student_model(name="Leena", age=19, city="Ahmedabad"),
]


@app.get("/students", response_model=list[StudentResponse])
def get_students(city: str | None = None):
    """Return all students or only those in the requested city."""
    if city is None:
        return students

    filtered_students = [
        student for student in students if student.city.lower() == city.lower()
    ]
    return filtered_students


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int):
    """Return a single student by their numeric index ID."""
    return students[student_id]


@app.post("/students", response_model=StudentResponse)
def add_student(student: Student_model):
    """Add a new student and return a success message."""
    students.append(student)
    return {"message": "Student Added", **student.model_dump()}
