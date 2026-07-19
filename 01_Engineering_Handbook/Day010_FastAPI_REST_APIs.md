# Day 010 — FastAPI & REST APIs

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 17 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand what FastAPI is.
- Understand REST APIs.
- Build your first FastAPI application.
- Understand API Endpoints.
- Understand HTTP Methods.
- Create GET and POST APIs.
- Use Path Parameters.
- Create Request Models using Pydantic.
- Use Swagger UI.
- Understand how FastAPI fits into Clean Architecture.

---

# Big Picture

Until yesterday our application looked like this:

```text
User

↓

CLI Application

↓

Service Layer

↓

Repository

↓

Database Helper

↓

PostgreSQL
```

Only someone sitting on the same computer could use the application.

Today we expose our application through the Web.

```text
Browser

↓

FastAPI

↓

Service Layer

↓

Repository

↓

Database Helper

↓

PostgreSQL
```

Now any application can communicate with our backend.

---

# What is FastAPI?

FastAPI is a modern Python web framework used for building APIs.

It is:

- Fast
- Lightweight
- Easy to learn
- Automatically generates API documentation
- Uses Python type hints
- Performs automatic validation

It is one of the most popular frameworks for AI applications and modern backend systems.

---

# Why FastAPI?

Compared to Flask:

| Flask                       | FastAPI                         |
| --------------------------- | ------------------------------- |
| Minimal framework           | Modern API-first framework      |
| Validation is manual        | Automatic validation            |
| Manual documentation        | Automatic Swagger documentation |
| Less type-aware             | Full type hint support          |
| Slower development for APIs | Faster API development          |

---

# What is an API?

API stands for:

> **Application Programming Interface**

It allows two software applications to communicate.

Example:

```text
Mobile App

↓

API

↓

Database
```

The mobile app never talks directly to the database.

Everything goes through the API.

---

# REST API

REST (Representational State Transfer) is an architectural style for building web services.

Each resource has its own URL.

Example:

```text
/students
/courses
/enrollments
```

---

# HTTP Request Flow

```text
Client

↓

HTTP Request

↓

FastAPI

↓

Service Layer

↓

Repository

↓

Database

↓

HTTP Response

↓

Client
```

---

# HTTP Methods

| Method | Purpose                      |
| ------ | ---------------------------- |
| GET    | Retrieve data                |
| POST   | Create data                  |
| PUT    | Replace existing data        |
| PATCH  | Update part of existing data |
| DELETE | Delete data                  |

Example:

```text
GET /students
```

Retrieve all students.

---

```text
POST /students
```

Create a new student.

---

```text
DELETE /students/5
```

Delete student with ID 5.

---

# Installing FastAPI

```bash
pip install fastapi
```

---

# Installing Uvicorn

```bash
pip install uvicorn
```

---

# What is Uvicorn?

FastAPI is only your application.

Uvicorn is the web server that runs it.

Think of it like this:

```text
Your Code

↓

FastAPI

↓

Uvicorn

↓

Browser
```

---

# Your First FastAPI Application

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello Project ₹50L!"}
```

Run:

```bash
uvicorn main:app --reload
```

Visit:

```text
http://127.0.0.1:8000
```

---

# Project Structure

```text
Day010/

│
├── main.py
├── models.py
├── README.md
└── practice_day10.md
```

Soon this will become:

```text
StudentManagement/

│
├── app.py
├── api/
├── models/
├── services/
├── repositories/
├── database/
└── tests/
```

---

# API Endpoints

An endpoint is simply a URL exposed by the server.

Example:

```python
@app.get("/students")
```

Request:

```text
GET /students
```

Response:

```json
[
  {
    "name": "Mayank",
    "age": 27
  }
]
```

---

# Path Parameters

Dynamic values can be passed in the URL.

Example:

```python
@app.get("/students/{student_id}")
```

If the user visits:

```text
/students/15
```

then

```python
student_id = 15
```

automatically.

---

# Request Body

When creating data we send JSON.

Example:

```json
{
  "name": "Mayank",
  "age": 27,
  "city": "Ahmedabad"
}
```

---

# Pydantic

Pydantic validates incoming data.

Example:

```python
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    age: int
    city: str
```

Now FastAPI automatically checks:

✔ Required fields

✔ Data types

✔ Invalid input

No extra code required.

## 1. What is Pydantic?

Pydantic is a widely used Python library for data validation and settings management.

At its core, it enforces type hints at runtime and provides clear error messages when data is invalid. Instead of assuming that incoming data is in the right format, Pydantic ensures that it matches the structure you define.

### How it works

You define the structure of your data by creating a class that inherits from Pydantic's `BaseModel`:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True
```

If you pass a dictionary like this:

```python
{"id": "123", "name": "Alice", "email": "alice@example.com"}
```

Pydantic will:

- Validate the data and ensure required fields are present.
- Coerce types automatically, such as converting the string `"123"` into the integer `123`.
- Fail safely by raising a structured error if the data is invalid.

---

## 2. Why do we use request models?

Request models are Pydantic models used to define the exact shape of incoming payload data, such as a JSON body in a POST request.

We use them for several important reasons:

### Automatic validation and type safety

Without request models, you would need to manually check incoming data, which is repetitive and error-prone.

```python
# Manual validation approach
if "username" not in request.json:
    return "Missing username", 400
if not isinstance(request.json["age"], int):
    return "Age must be an integer", 400
```

With a Pydantic request model, the framework handles this automatically. If the client sends invalid data, the server rejects it with a clear `422 Unprocessable Entity` response before your core logic runs.

### Parsing instead of just validating

Pydantic does more than validate; it parses raw input into native Python types. For example, a date provided as a string can be converted into a Python `date` object.

### Auto-generated API documentation

Frameworks like FastAPI use request models to generate interactive API documentation such as Swagger UI or ReDoc.

This helps frontend developers and API consumers understand exactly what schema the request should follow.

### Better editor support

Once data is parsed into a request model, your IDE can provide better autocomplete, type checking, and linting, reducing bugs and typos in your application logic.

---

# Request Flow

Creating a Student

```text
Browser

↓

POST /students

↓

FastAPI

↓

Pydantic Validation

↓

StudentService

↓

Repository

↓

Database

↓

Response

↓

Browser
```

---

# Response Flow

Reading Students

```text
Browser

↓

GET /students

↓

FastAPI

↓

StudentService

↓

Repository

↓

Database

↓

JSON Response

↓

Browser
```

---

# Swagger UI

One of FastAPI's biggest advantages.

Visit:

```text
http://127.0.0.1:8000/docs
```

You automatically get:

- API documentation
- Interactive testing
- Request examples
- Response examples
- JSON schemas

No additional coding required.

---

# ReDoc

FastAPI also provides another documentation page.

Visit:

```text
http://127.0.0.1:8000/redoc
```

Useful for cleaner API documentation.

---

# JSON

APIs usually communicate using JSON.

Example:

```json
{
  "name": "Mayank",
  "age": 27,
  "city": "Ahmedabad"
}
```

Advantages:

- Human readable
- Lightweight
- Supported by almost every programming language

---

# How FastAPI Fits into Clean Architecture

Yesterday:

```text
CLI

↓

Service

↓

Repository

↓

Database
```

Today:

```text
FastAPI

↓

Service

↓

Repository

↓

Database Helper

↓

PostgreSQL
```

Notice:

FastAPI replaces the CLI.

Everything below the Service Layer remains unchanged.

This is exactly why we learned Clean Architecture first.

---

# Real-World Architecture

```text
React Frontend

↓

HTTP Request

↓

FastAPI

↓

Service Layer

↓

Repository

↓

Database Helper

↓

PostgreSQL
```

This is the architecture used by thousands of production applications.

---

# Bad API Design

```text
FastAPI

↓

SQL Queries

↓

Database
```

Problems:

❌ SQL inside endpoints

❌ Hard to maintain

❌ Duplicate logic

❌ Difficult testing

---

# Good API Design

```text
FastAPI

↓

Service Layer

↓

Repository

↓

Database Helper

↓

PostgreSQL
```

Benefits:

✔ Separation of Concerns

✔ Easy testing

✔ Reusable logic

✔ Scalable architecture

✔ Easier maintenance

---

# FastAPI vs Yesterday's CLI

| CLI               | FastAPI            |
| ----------------- | ------------------ |
| Local application | Web application    |
| Keyboard input    | HTTP Requests      |
| Print output      | JSON Response      |
| Single user       | Multiple users     |
| Runs in terminal  | Runs on web server |

---

# Interview Questions

### Q1. What is FastAPI?

FastAPI is a modern, high-performance Python framework for building RESTful APIs with automatic validation and interactive documentation.

---

### Q2. Why is FastAPI faster than Flask?

FastAPI is built on Starlette and Pydantic, supports asynchronous programming, automatic validation, and efficient request handling.

---

### Q3. What is an API Endpoint?

An endpoint is a specific URL exposed by an API to perform an operation on a resource.

Example:

```text
GET /students
```

---

### Q4. What is Uvicorn?

Uvicorn is an ASGI web server that runs FastAPI applications and handles incoming HTTP requests.

---

### Q5. What is Pydantic?

Pydantic is a Python library used by FastAPI to validate and serialize request and response data using Python type hints.

---

### Q6. What is Swagger?

Swagger UI is an automatically generated interactive API documentation page that allows developers to test API endpoints directly from the browser.

---

# Cheat Sheet

```text
Browser

↓

FastAPI

↓

Service

↓

Repository

↓

Database
```

---

```text
GET

↓

Read Data
```

```text
POST

↓

Create Data
```

```text
PUT

↓

Replace Data
```

```text
PATCH

↓

Update Data
```

```text
DELETE

↓

Delete Data
```

---

```text
FastAPI

↓

Uvicorn

↓

Browser
```

---

```text
/docs

↓

Swagger UI
```

```text
/redoc

↓

ReDoc Documentation
```

---

# Key Takeaways

- FastAPI is a modern framework for building high-performance REST APIs.
- APIs allow different applications to communicate over HTTP.
- REST APIs expose resources using endpoints and HTTP methods.
- Uvicorn runs FastAPI applications as an ASGI server.
- Pydantic automatically validates incoming request data.
- Swagger UI and ReDoc provide interactive API documentation with zero extra effort.
- Clean Architecture allows FastAPI to replace the CLI without changing the Service or Repository layers.

---

# Revision Checklist

- [ ] Can explain what FastAPI is.
- [ ] Understand REST API fundamentals.
- [ ] Know all five HTTP methods.
- [ ] Can create GET endpoints.
- [ ] Can create POST endpoints.
- [ ] Understand Path Parameters.
- [ ] Can create Pydantic models.
- [ ] Can explain Uvicorn.
- [ ] Can use Swagger UI.
- [ ] Understand how FastAPI integrates with Clean Architecture.

---

# Tomorrow's Preview

- Connecting FastAPI with PostgreSQL.
- Using the Repository and Service layers from our Student Management project.
- Dependency Injection fundamentals.
- CRUD APIs backed by a real database.
- Returning real data instead of in-memory objects.
