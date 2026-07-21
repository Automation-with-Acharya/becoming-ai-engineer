from pydantic import BaseModel


class Student_model(BaseModel):
    """A student record with a name, age, and city."""
    name: str
    age: int
    city: str

class StudentResponse(BaseModel):
    name: str
    age: int
    city: str