"""FastAPI experiments for learning basic API development.

This file contains six small experiments that cover:
1. Creating a basic FastAPI app
2. Creating a GET endpoint for a list of students
3. Creating a GET endpoint with a path parameter
4. Defining a Pydantic model for request validation
5. Creating a POST endpoint that accepts JSON data
6. Exploring auto-generated Swagger documentation
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="FastAPI Student Experiments",
    description="A simple learning project for FastAPI basics.",
    version="1.0.0",
)


class Student(BaseModel):
    """Request model for student data."""

    name: str
    age: int
    city: str


students = [
    {"id": 1, "name": "Alice", "age": 20, "city": "Delhi"},
    {"id": 2, "name": "Bob", "age": 22, "city": "Mumbai"},
]


@app.get("/")
def home() -> dict[str, str]:
    """Experiment 1: return a simple welcome message."""
    return {"message": "Hello Project 50L!"}


@app.get("/students")
def get_students() -> list[dict[str, object]]:
    """Experiment 2: return a list of sample students."""
    return students


@app.get("/students/{student_id}")
def get_student(student_id: int) -> dict[str, object]:
    """Experiment 3: return one student using a path parameter."""
    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(status_code=404, detail="Student not found")


@app.post("/students", status_code=201)
def create_student(student: Student) -> dict[str, object]:
    """Experiment 5: accept student data and return it."""
    new_student = {
        "id": max(student["id"] for student in students) + 1,
        "name": student.name,
        "age": student.age,
        "city": student.city,
    }
    students.append(new_student)
    return new_student
