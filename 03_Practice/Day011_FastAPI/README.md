# Day 11 FastAPI Practice

This practice implements a simple FastAPI application for managing student records.
The project is split into:

- `models.py` — defines the `Student_model` Pydantic model
- `student_api.py` — creates the FastAPI app and the student endpoints

## Features

- `GET /students` — returns a list of all students
- `GET /students/{student_id}` — returns a single student by index ID
- `POST /students` — accepts a `Student_model` body and adds it to the list
- `GET /students?city=<city>` — filters students by city using a query parameter

## Model

`models.py` contains:

```python
from pydantic import BaseModel


class Student_model(BaseModel):
    name: str
    age: int
    city: str


class StudentResponse(BaseModel):
    name: str
    age: int
    city: str
```

`Student_model` is used for incoming POST data, while `StudentResponse` is used as the FastAPI `response_model` for the endpoints.

## API behavior

- The app uses an in-memory list of sample students.
- The `POST /students` endpoint validates incoming JSON against the `Student_model`.
- If invalid data is sent (for example `name` as a number or `age` as a string), FastAPI rejects it automatically.

## Run the app

From the `03_Practice/Day011_FastAPI` directory, run:

```bash
uvicorn student_api:app --reload
```

## API documentation

FastAPI automatically generates interactive API docs at:

- `http://127.0.0.1:8000/docs` (Swagger UI)
- `http://127.0.0.1:8000/redoc` (ReDoc)

## Example requests

1. Get all students:

```http
GET /students
```

2. Get a student by ID:

```http
GET /students/0
```

3. Filter students by city:

```http
GET /students?city=Ahmedabad
```

4. Add a student:

```http
POST /students
Content-Type: application/json

{
  "name": "Riya",
  "age": 21,
  "city": "Ahmedabad"
}
```

Response:

```json
{
  "message": "Student Added"
}
```
