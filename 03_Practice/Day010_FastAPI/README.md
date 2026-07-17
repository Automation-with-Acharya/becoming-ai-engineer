# Student API v1

This mini project creates a simple FastAPI application with an in-memory student list.

## Features

- Get all students
- Get a single student by ID
- Create a new student
- Validate request data with Pydantic

## Run the app

From this folder, run:

```bash
uvicorn main:app --reload
```

Then open:

- Home: http://127.0.0.1:8000/
- Swagger docs: http://127.0.0.1:8000/docs

## Example requests

### Get all students

```bash
GET /students
```

### Get one student

```bash
GET /students/1
```

### Create a student

```bash
POST /students
Content-Type: application/json
```

```json
{
  "name": "Charlie",
  "age": 23,
  "city": "Chennai"
}
```

## Notes

- This version uses an in-memory list only.
- No database or repository layer is connected yet.
- The repository layer will be added in a future version.
