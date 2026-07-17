from pydantic import BaseModel, Field


class StudentBase(BaseModel):
    """Base student schema shared by create/update operations."""

    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=1, le=100)
    city: str = Field(..., min_length=2, max_length=100)


class StudentCreate(StudentBase):
    """Schema used for creating a new student."""


class Student(StudentBase):
    """Schema used for returning a student from the API."""

    id: int
