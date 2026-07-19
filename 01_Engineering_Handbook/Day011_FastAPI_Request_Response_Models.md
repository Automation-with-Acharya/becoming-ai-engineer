# Day 011 — FastAPI Request & Response Models, Path & Query Parameters

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 19 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand Request Models using Pydantic.
- Understand Response Models.
- Differentiate Path Parameters and Query Parameters.
- Understand automatic request validation.
- Build REST APIs with FastAPI.
- Read and test APIs using Swagger UI.
- Explain the request lifecycle in a FastAPI application.

---

# Big Picture

FastAPI is more than an API framework.

It automatically:

- validates incoming requests,
- converts data types,
- generates API documentation,
- serializes responses,
- returns meaningful error messages.

This reduces boilerplate code and improves reliability.

---

# 1. Evolution of Our Backend

## Day 09

```text
CLI

↓

Service Layer

↓

Repository

↓

Database Helper

↓

PostgreSQL
```

---

## Day 10

```text
Browser

↓

FastAPI Endpoint

↓

Service Layer

↓

Repository

↓

Database
```

---

## Day 11

```text
Client

↓

HTTP Request

↓

FastAPI

↓

Pydantic Validation

↓

Service Layer

↓

Repository

↓

Database Helper

↓

PostgreSQL

↓

JSON Response

↓

Client
```

Today we learned what happens **between the client and our application**.

---

# 2. REST API Refresher

A REST API exposes application functionality through HTTP endpoints.

Example:

```text
GET /students
```

Retrieve students.

```text
POST /students
```

Create a student.

```text
PUT /students/5
```

Update student.

```text
DELETE /students/5
```

Delete student.

---

# 3. Request Flow

```text
Client

↓

HTTP Request

↓

FastAPI Router

↓

Validation

↓

Business Logic

↓

Repository

↓

Database

↓

Repository

↓

JSON Response

↓

Client
```

Each layer has one responsibility.

---

# 4. What is Pydantic?

Pydantic is FastAPI's data validation library.

Instead of manually checking values:

```python
if age < 0:
    ...
```

FastAPI validates requests automatically using Pydantic models.

---

## Example

```python
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    age: int
    city: str
```

Whenever a client sends JSON, FastAPI converts it into this model.

---

# Pydantic Architecture

```text
Incoming JSON

↓

Pydantic Model

↓

Validation

↓

Python Object

↓

FastAPI Endpoint
```

---

# 5. Request Model

A Request Model defines the expected structure of incoming data.

Example request:

```json
{
  "name": "Mayank",
  "age": 27,
  "city": "Ahmedabad"
}
```

Model:

```python
class Student(BaseModel):
    name: str
    age: int
    city: str
```

Benefits:

- Automatic validation
- Automatic documentation
- Type conversion
- Cleaner code

---

# 6. Response Model

A Response Model defines what the API returns.

Example:

```python
class StudentResponse(BaseModel):
    id: int
    name: str
    age: int
```

Benefits:

- Consistent API responses
- Hides unnecessary fields
- Improves documentation
- Better client integration

---

# Request vs Response

```text
Client

↓

Request Model

↓

Business Logic

↓

Response Model

↓

Client
```

---

# 7. Path Parameters

Path Parameters identify a specific resource.

Example:

```text
/students/5
```

Here:

```text
5
```

is the Path Parameter.

FastAPI:

```python
@app.get("/students/{student_id}")
def get_student(student_id: int):
    ...
```

FastAPI automatically converts:

```text
"5"
```

into

```python
5
```

---

# Path Parameter Flow

```text
GET /students/10

↓

student_id = 10

↓

Service Layer

↓

Repository
```

---

# 8. Query Parameters

Query Parameters filter or modify the request.

Example:

```text
/students?city=Ahmedabad
```

Another example:

```text
/students?age=25
```

Multiple parameters:

```text
/students?city=Ahmedabad&age=25
```

FastAPI:

```python
@app.get("/students")
def get_students(city: str | None = None):
    ...
```

---

# Query Parameter Flow

```text
GET /students?city=Ahmedabad

↓

city = Ahmedabad

↓

Filter Data

↓

Return Matching Students
```

---

# Path vs Query Parameters

| Path Parameter        | Query Parameter             |
| --------------------- | --------------------------- |
| Identifies a resource | Filters or modifies results |
| Required              | Usually optional            |
| `/students/5`         | `/students?city=Ahmedabad`  |

---

# 9. Automatic Validation

One of FastAPI's strongest features.

Suppose:

```python
class Student(BaseModel):
    age: int
```

Client sends:

```json
{
  "age": "twenty"
}
```

FastAPI immediately returns:

```text
422 Unprocessable Entity
```

without executing your code.

---

# Validation Flow

```text
Client

↓

JSON

↓

Pydantic

↓

Valid?

↓

Yes

↓

Endpoint Executes

──────────────

No

↓

422 Error
```

---

# 10. Swagger UI

FastAPI automatically creates API documentation.

Default URL:

```text
http://127.0.0.1:8000/docs
```

Features:

- Interactive testing
- Request examples
- Response examples
- Schema documentation

No additional coding required.

---

# Swagger Architecture

```text
FastAPI

↓

Pydantic Models

↓

OpenAPI Specification

↓

Swagger UI
```

---

# 11. Real Project Architecture

Current Student Management project:

```text
Browser

↓

Swagger UI

↓

FastAPI

↓

StudentService

↓

StudentRepository

↓

DatabaseHelper

↓

PostgreSQL
```

This is the same layered pattern used in enterprise backend applications.

---

# 12. Complete Request Lifecycle

Example:

Create Student.

```text
Client

↓

POST /students

↓

Request JSON

↓

Pydantic Validation

↓

StudentService

↓

StudentRepository

↓

DatabaseHelper

↓

PostgreSQL

↓

StudentRepository

↓

StudentService

↓

Response Model

↓

JSON Response

↓

Client
```

---

# Common HTTP Methods

| Method | Purpose        |
| ------ | -------------- |
| GET    | Read data      |
| POST   | Create data    |
| PUT    | Replace data   |
| PATCH  | Partial update |
| DELETE | Delete data    |

---

# Common HTTP Status Codes

| Code | Meaning               |
| ---: | --------------------- |
|  200 | OK                    |
|  201 | Created               |
|  400 | Bad Request           |
|  401 | Unauthorized          |
|  404 | Not Found             |
|  422 | Validation Error      |
|  500 | Internal Server Error |

---

# Bad API Design

```text
Endpoint

↓

SQL

↓

Validation

↓

JSON

↓

Everything Together
```

Problems:

- Hard to test
- Hard to maintain
- Duplicate validation

---

# Good API Design

```text
Endpoint

↓

Pydantic

↓

Service

↓

Repository

↓

Database
```

Benefits:

- Clean architecture
- Automatic validation
- Better testing
- Reusable business logic

---

# Real-World Mapping

| Our Project | Enterprise Equivalent        |
| ----------- | ---------------------------- |
| Browser     | React / Angular / Mobile App |
| FastAPI     | Backend API Gateway          |
| Pydantic    | Validation Layer             |
| Service     | Business Logic               |
| Repository  | Data Access Layer            |
| PostgreSQL  | Enterprise Database          |

---

# Interview Questions

### Q1. Why does FastAPI use Pydantic?

Pydantic validates incoming request data, performs type conversion, and automatically generates API schemas for documentation.

---

### Q2. Difference between Path and Query Parameters?

Path Parameters identify a specific resource.

Query Parameters filter or customize the returned results.

---

### Q3. What is a Request Model?

A Pydantic model describing the expected structure of incoming request data.

---

### Q4. What is a Response Model?

A Pydantic model that defines the structure of data returned by the API, ensuring consistency and hiding unnecessary fields.

---

### Q5. Why is FastAPI considered faster to develop than many frameworks?

Because it provides automatic validation, dependency injection, OpenAPI documentation, Swagger UI, and type-based serialization with very little boilerplate code.

---

### Q6. What happens if invalid JSON is sent?

Pydantic validation fails and FastAPI automatically returns a **422 Unprocessable Entity** response without executing the endpoint logic.

---

# Cheat Sheet

```text
Client

↓

FastAPI

↓

Pydantic

↓

Service

↓

Repository

↓

Database
```

---

```text
Path Parameter

/students/10

↓

Specific Resource
```

---

```text
Query Parameter

/students?city=Ahmedabad

↓

Filter Results
```

---

```text
Request

↓

Validation

↓

Business Logic

↓

Response
```

---

# Key Takeaways

- FastAPI uses Pydantic for automatic request validation and type conversion.
- Request Models define the structure of incoming data, while Response Models define the structure of outgoing data.
- Path Parameters identify resources; Query Parameters filter or customize results.
- Swagger UI is generated automatically from FastAPI endpoints and Pydantic models.
- Automatic validation reduces boilerplate code and improves API reliability.
- Combining FastAPI with Service and Repository layers results in a clean, maintainable backend architecture.

---

# Revision Checklist

- [ ] Understand Pydantic models.
- [ ] Can create Request Models.
- [ ] Can create Response Models.
- [ ] Know the difference between Path and Query Parameters.
- [ ] Understand automatic validation.
- [ ] Can explain Swagger UI generation.
- [ ] Can trace a complete API request through the application layers.

---

# Tomorrow's Preview

- Dependency Injection in FastAPI
- APIRouter for modular APIs
- CRUD endpoints with PostgreSQL
- Connecting FastAPI directly to the Student Management project
- Preparing the application for production-style backend development
