# Day 013 — CRUD APIs, HTTP Status Codes & Exception Handling

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 22 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand CRUD operations in REST APIs.
- Understand HTTP methods and their purpose.
- Use appropriate HTTP Status Codes.
- Handle errors using `HTTPException`.
- Design APIs that follow REST principles.
- Explain the complete lifecycle of an API request.
- Compare FastAPI implementation with ASP.NET Core.

---

# Big Picture

Until yesterday our API could receive requests.

Today it learns how to **communicate success and failure correctly.**

---

# Evolution of Our Backend

## Day 11

```text
Browser

↓

FastAPI

↓

JSON Response
```

---

## Day 12

```text
Browser

↓

APIRouter

↓

Depends()

↓

Service

↓

Repository
```

---

## Day 13

```text
Browser

↓

HTTP Request

↓

APIRouter

↓

Depends()

↓

Service

↓

Repository

↓

Database

↓

HTTP Status Code

↓

JSON Response

↓

Browser
```

---

# 1. What is CRUD?

CRUD represents the four basic operations performed on data.

| Operation | HTTP Method | Description                            |
| --------- | ----------- | -------------------------------------- |
| Create    | POST        | Create a new resource                  |
| Read      | GET         | Retrieve one or more resources         |
| Update    | PUT         | Replace or update an existing resource |
| Delete    | DELETE      | Remove a resource                      |

Almost every backend API is fundamentally built around these four operations.

---

# CRUD Flow

```text
Client

↓

POST

↓

Create Student

──────────────

GET

↓

Read Student

──────────────

PUT

↓

Update Student

──────────────

DELETE

↓

Delete Student
```

---

# 2. REST API Principles

A REST API revolves around **resources**, not actions.

Good examples:

```text
GET    /students

GET    /students/5

POST   /students

PUT    /students/5

DELETE /students/5
```

Bad examples:

```text
/createStudent

/deleteStudent

/updateStudent
```

The HTTP method already tells the server what action is being performed.

---

# Resource-Oriented Design

Think about nouns instead of verbs.

```text
Student

Course

Employee

Order

Invoice
```

The HTTP method defines the operation.

---

# 3. HTTP Methods

## GET

Purpose:

Retrieve data.

Example:

```http
GET /students
```

Safe:

✅ Yes

Modifies data:

❌ No

---

## POST

Purpose:

Create new data.

Example:

```http
POST /students
```

Modifies data:

✅ Yes

Usually returns:

```text
201 Created
```

---

## PUT

Purpose:

Update an existing resource.

Example:

```http
PUT /students/5
```

Returns:

```text
200 OK
```

or

```text
204 No Content
```

---

## DELETE

Purpose:

Remove data.

Example:

```http
DELETE /students/5
```

Returns:

```text
204 No Content
```

---

# 4. HTTP Status Codes

HTTP Status Codes tell the client **what happened** before it even reads the response body.

---

## 200 OK

Everything succeeded.

Example:

```http
GET /students
```

Response:

```text
200 OK
```

---

## 201 Created

A new resource has been created.

Example:

```http
POST /students
```

Response:

```text
201 Created
```

---

## 204 No Content

Operation succeeded but nothing needs to be returned.

Typically used for:

```text
DELETE
```

Example:

```http
DELETE /students/5
```

---

## 400 Bad Request

The client sent invalid data.

Example:

Missing required fields.

Invalid values.

Wrong format.

---

## 401 Unauthorized

Authentication required.

Example:

JWT token missing.

---

## 403 Forbidden

User is authenticated but lacks permission.

---

## 404 Not Found

Requested resource doesn't exist.

Example:

```text
GET /students/100
```

Student 100 isn't found.

Return:

```text
404 Not Found
```

---

## 500 Internal Server Error

Unexpected server failure.

Usually indicates a programming bug or infrastructure problem.

---

# HTTP Status Code Families

```text
1xx

Information

↓

2xx

Success

↓

3xx

Redirection

↓

4xx

Client Errors

↓

5xx

Server Errors
```

Most backend work focuses on **2xx**, **4xx**, and **5xx** responses.

---

# 5. What is HTTPException?

`HTTPException` allows FastAPI to immediately stop processing and return an appropriate HTTP response.

Example:

```python
from fastapi import HTTPException

raise HTTPException(
    status_code=404,
    detail="Student not found"
)
```

---

# Request Lifecycle with HTTPException

```text
Client

↓

GET /students/100

↓

Router

↓

Service

↓

Repository

↓

Database

↓

No Record Found

↓

HTTPException(404)

↓

JSON Response

↓

Client
```

---

# Response Example

```json
{
  "detail": "Student not found"
}
```

Status:

```text
404
```

---

# 6. Why Use HTTPException?

Without it:

```text
Server crashes

or

Returns meaningless data
```

With it:

```text
Client immediately knows

• What failed

• Why it failed

• Correct HTTP status
```

---

# 7. CRUD Request Flow

## CREATE

```text
POST

↓

Router

↓

Service

↓

Repository

↓

INSERT

↓

201 Created
```

---

## READ

```text
GET

↓

SELECT

↓

200 OK
```

---

## UPDATE

```text
PUT

↓

UPDATE

↓

200 OK
```

---

## DELETE

```text
DELETE

↓

DELETE

↓

204 No Content
```

---

# 8. Production Architecture

```text
Browser

↓

HTTP Request

↓

APIRouter

↓

Dependency Injection

↓

Service

↓

Repository

↓

Database

↓

HTTP Status

↓

JSON

↓

Browser
```

Every production backend follows this same logical flow.

---

# 9. Responsibility of Each Layer

| Layer            | Responsibility                            |
| ---------------- | ----------------------------------------- |
| Router           | Accept HTTP requests and return responses |
| Service          | Business rules                            |
| Repository       | Data access                               |
| Database         | Store persistent data                     |
| HTTP Status Code | Describe the outcome of the request       |
| HTTPException    | Report failures clearly                   |

---

# 10. Good API Behaviour

Suppose:

```text
GET /students/5
```

Student exists.

Return:

```text
200 OK
```

---

Suppose:

```text
GET /students/999
```

Student missing.

Return:

```text
404 Not Found
```

---

Suppose:

```text
POST /students
```

Successfully created.

Return:

```text
201 Created
```

---

Suppose:

```text
DELETE /students/5
```

Deleted successfully.

Return:

```text
204 No Content
```

---

# 11. FastAPI vs ASP.NET Core

## FastAPI

```python
raise HTTPException(
    status_code=404,
    detail="Student not found"
)
```

---

## ASP.NET Core

```csharp
return NotFound();
```

---

FastAPI

```python
status_code=201
```

ASP.NET Core

```csharp
return Created(...);
```

---

FastAPI

```python
status_code=200
```

ASP.NET Core

```csharp
return Ok();
```

The concepts are identical.

Only the syntax differs.

---

# 12. Common Beginner Mistakes

❌ Returning `200 OK` for every response.

❌ Returning empty lists when a single resource is missing.

❌ Ignoring HTTP status codes.

❌ Returning plain strings instead of structured JSON.

❌ Mixing exception handling with business logic.

---

# Production Best Practices

✅ Use the correct HTTP method.

✅ Return the correct status code.

✅ Raise `HTTPException` for expected client errors.

✅ Keep error messages meaningful.

✅ Validate requests before processing.

✅ Keep routers thin and delegate logic to services.

---

# Interview Questions

### Q1. What is CRUD?

CRUD represents Create, Read, Update, and Delete—the four fundamental operations performed on data.

---

### Q2. Difference between GET and POST?

GET retrieves data without modifying the server.

POST creates new resources and changes server state.

---

### Q3. Why return 201 instead of 200 after POST?

`201 Created` explicitly tells the client that a new resource has been successfully created.

---

### Q4. Why use 204 after DELETE?

The deletion succeeded, and there is no response body to return.

---

### Q5. What is HTTPException?

`HTTPException` is FastAPI's built-in mechanism for returning appropriate HTTP error responses with status codes and messages.

---

### Q6. Difference between 401 and 403?

401 means the client is **not authenticated**.

403 means the client **is authenticated but lacks permission**.

---

# Cheat Sheet

```text
POST

↓

201 Created
```

---

```text
GET

↓

200 OK
```

---

```text
PUT

↓

200 OK
```

---

```text
DELETE

↓

204 No Content
```

---

```text
Resource Missing

↓

404 Not Found
```

---

```text
Invalid Request

↓

400 Bad Request
```

---

```python
raise HTTPException(
    status_code=404,
    detail="Student not found"
)
```

---

# Key Takeaways

- CRUD forms the foundation of nearly every REST API.
- REST APIs are designed around resources rather than actions.
- HTTP methods define the operation being performed.
- HTTP Status Codes communicate the outcome of a request before the response body is processed.
- `HTTPException` enables FastAPI to return meaningful, standards-compliant error responses.
- Correct status codes improve API usability, debugging, and interoperability.
- These REST principles are shared across frameworks such as FastAPI, ASP.NET Core, Spring Boot, and Express.

---

# Revision Checklist

- [ ] Can explain CRUD operations.
- [ ] Know the purpose of GET, POST, PUT, and DELETE.
- [ ] Can identify when to use 200, 201, 204, 400, 401, 403, 404, and 500.
- [ ] Can use `HTTPException` correctly.
- [ ] Understand the complete request lifecycle.
- [ ] Can compare FastAPI and ASP.NET Core implementations.

---

# 🏗 Why does this exist?

## What problem does it solve?

HTTP Status Codes and `HTTPException` provide a standard way for APIs to communicate the result of an operation. Instead of guessing whether something succeeded or failed, clients immediately know the outcome through the status code.

---

## Who depends on it?

```text
Client

↓

Router

↓

Service

↓

Repository

↓

Database

↓

HTTP Status Code

↓

Client
```

Every API endpoint depends on correct HTTP semantics to communicate reliably with web applications, mobile apps, and other services.

---

## Who should never depend on it?

The **Service Layer** and **Repository Layer** should not know about HTTP.

They should only return data or indicate success/failure.

Only the **Router (Presentation Layer)** should convert those outcomes into HTTP responses or raise `HTTPException`.

This separation keeps the architecture clean and framework-independent.

---

## How does ASP.NET Core implement the same concept?

```csharp
return Ok();
return Created(...);
return NotFound();
return BadRequest();
return NoContent();
```

The controller converts business outcomes into HTTP responses.

---

## How does FastAPI implement it?

```python
return student

raise HTTPException(
    status_code=404,
    detail="Student not found"
)
```

The router performs the same responsibility using FastAPI's response handling and `HTTPException`.

---

# Tomorrow's Preview

- Advanced Pydantic Models
- Request validation
- Response serialization
- API documentation customization
- Building cleaner, production-grade FastAPI endpoints
