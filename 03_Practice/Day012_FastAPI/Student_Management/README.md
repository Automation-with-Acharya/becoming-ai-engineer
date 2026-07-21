# Day 12 FastAPI Practice - Student Management

This project demonstrates a cleaner FastAPI structure for managing student records using:

- an APIRouter for endpoints
- a service layer for business logic
- Pydantic models for request/response validation

## Project Structure

```text
Student_Management/
├── main.py
├── models/
│   └── models.py
├── routers/
│   └── students.py
├── services/
│   └── student_service.py
├── repository/
└── README.md
```

## Key Components

- `main.py` — creates the FastAPI application and includes the student router
- `routers/students.py` — contains the student API endpoints
- `services/student_service.py` — handles student operations such as fetching, filtering, and adding students
- `models/models.py` — defines the `Student_model` and `StudentResponse` schemas

## Features

- `GET /students` — returns all students
- `GET /students/{student_id}` — returns a single student by index
- `GET /students?city=<city>` — filters students by city
- `POST /students` — adds a new student

## API Behavior

- The app uses an in-memory list of sample students.
- The router delegates the logic to the service layer.
- FastAPI validates incoming JSON automatically using Pydantic models.

## Run the App

From the `03_Practice/Day012_FastAPI` directory, run:

```bash
uvicorn Student_Management.main:app --reload
```

## API Documentation

FastAPI provides interactive docs at:

- `http://127.0.0.1:8000/docs` — Swagger UI
- `http://127.0.0.1:8000/redoc` — ReDoc

## Example Requests

### Get all students

```http
GET /students
```

### Get a student by ID

```http
GET /students/0
```

### Filter students by city

```http
GET /students?city=Ahmedabad
```

### Add a student

```http
POST /students
Content-Type: application/json

{
  "name": "Riya",
  "age": 21,
  "city": "Ahmedabad"
}
```

### Response

```json
{
  "message": "Student Added"
}
```
