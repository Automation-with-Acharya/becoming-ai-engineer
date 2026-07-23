"""
Student Model Module.

This module defines the Student entity class representing the student data model.
A domain model represents the core business entity with its attributes.
"""

from pydantic import BaseModel



class Student(BaseModel):
    """
    Represents a Student entity in the system.

    Attributes:
        id (int | None): The unique identifier for the student.
        name (str): The full name of the student.
    """
    id: int | None = None
    name: str
    age: int | None = None
    city: str | None = ""
