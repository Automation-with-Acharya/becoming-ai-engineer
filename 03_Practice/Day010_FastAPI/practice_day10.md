# Student API v1 Notes

This file documents the mini project for building a Student API using FastAPI and an in-memory list.

## Goal

Create a simple API today without connecting to PostgreSQL or a repository layer.

## What we built

- A FastAPI app with a home route
- A GET endpoint to fetch all students
- A GET endpoint to fetch one student by ID
- A POST endpoint to create a new student
- Pydantic models for request and response validation

## Run the app

```bash
uvicorn main:app --reload
```

## Endpoints

### GET /

Returns a welcome message.

### GET /students

Returns the full list of students stored in memory.

### GET /students/{student_id}

Returns one student by ID.

### POST /students

Creates a new student using JSON input.

Example body:

```json
{
  "name": "Charlie",
  "age": 23,
  "city": "Chennai"
}
```

## Next step

Tomorrow, this in-memory list will be replaced by a repository layer and later connected to PostgreSQL.
