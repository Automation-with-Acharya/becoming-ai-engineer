# Day 018 — Global Exception Handling & Custom Exceptions

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 29 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand why global exception handling is necessary.
- Use FastAPI's `HTTPException`.
- Create custom exception classes.
- Configure global exception handlers.
- Return standardized API error responses.
- Integrate exception handling with structured logging.
- Understand where exceptions should be raised in Clean Architecture.
- Compare FastAPI exception handling with ASP.NET Core.

---

# Big Picture

Yesterday our backend looked like this:

```text
Client

↓

Middleware

↓

Logger

↓

Router

↓

Service

↓

Repository

↓

Database
```

Today we introduce centralized exception handling.

```text
Client

↓

Middleware

↓

Logger

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Exception

↓

Global Exception Handler

↓

JSON Error Response

↓

Client
```

Instead of crashing the application, exceptions are handled in one central location.

---

# 1. What is an Exception?

An exception is an unexpected situation that interrupts the normal flow of a program.

Examples:

- Student not found
- Invalid ID
- Database unavailable
- Duplicate email
- Unauthorized user

Without exception handling, the application usually returns:

```text
500 Internal Server Error
```

with very little useful information.

---

# Why Global Exception Handling?

Without a global handler:

Every router has to repeat:

```python
try:
    ...
except Exception:
    ...
```

This creates:

- duplicate code
- inconsistent responses
- difficult maintenance

A global exception handler solves this by handling errors in one place.

---

# Exception Flow

```text
Request

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Exception Raised

↓

Global Exception Handler

↓

JSON Response

↓

Client
```

---

# 2. HTTPException

FastAPI provides:

```python
from fastapi import HTTPException
```

Example:

```python
raise HTTPException(

status_code=404,

detail="Student not found"

)
```

FastAPI automatically converts this into an HTTP response.

---

# Response

```json
{
  "detail": "Student not found"
}
```

Simple and useful.

---

# 3. Why Custom Exceptions?

Large applications usually avoid scattering `HTTPException` throughout the business layer.

Instead of:

```python
raise HTTPException(...)
```

they create domain-specific exceptions.

Example:

```python
class StudentNotFoundException(Exception):

    pass
```

Now the business layer communicates in business language.

---

# Domain Exception Flow

```text
Service

↓

raise StudentNotFoundException

↓

Global Exception Handler

↓

HTTP 404

↓

Client
```

The Service layer never needs to know FastAPI exists.

---

# 4. Clean Architecture Responsibility

Repository:

```text
Retrieve data.
```

Returns:

- object
- list
- None

No business decisions.

---

Service:

```text
Apply business rules.
```

Example:

```python
student = repository.get_student(id)

if student is None:

    raise StudentNotFoundException(id)
```

The Service owns business decisions.

---

Router:

```text
Receive HTTP request.

↓

Call Service.

↓

Return Response.
```

Routers should stay thin.

They should not contain business rules.

---

Global Exception Handler:

```text
Convert exceptions

↓

HTTP Responses
```

---

# Architecture Diagram

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

StudentNotFoundException

↓

Global Exception Handler

↓

JSON Response
```

---

# 5. Creating Custom Exceptions

Example:

```python
class StudentNotFoundException(Exception):

    def __init__(self, student_id):

        self.student_id = student_id

        super().__init__(
            f"Student {student_id} not found."
        )
```

Advantages:

- reusable
- meaningful
- testable
- framework independent

---

# 6. Global Exception Handler

Example:

```python
@app.exception_handler(

StudentNotFoundException

)

async def student_not_found_handler(

request,

exc

):

    ...
```

This handler executes automatically whenever the exception is raised.

---

# Standardized Error Response

Instead of:

```json
{
  "detail": "Student not found"
}
```

Production APIs often return:

```json
{
  "success": false,

  "error": {
    "code": "STUDENT_NOT_FOUND",

    "message": "Student 10 not found."
  }
}
```

Advantages:

- easier for frontend
- consistent format
- easier testing
- predictable APIs

---

# 7. Logging + Exception Handling

Yesterday we learned:

```python
logger.exception(...)
```

Today:

```text
Exception Raised

↓

Logger

↓

Global Handler

↓

Client Response
```

This gives:

- user-friendly response
- detailed developer logs

The client sees only necessary information.

Developers see the complete stack trace.

---

# 8. What Should Be Logged?

Good candidates:

- unexpected exceptions
- database failures
- authentication failures
- authorization failures
- external API failures

Avoid logging:

- passwords
- API keys
- JWT secrets
- sensitive personal information

---

# 9. Exception Types

Business Exceptions

Examples:

- StudentNotFoundException
- DuplicateEmailException
- InvalidEnrollmentException

---

System Exceptions

Examples:

- Database unavailable
- Network timeout
- File not found

---

Validation Exceptions

Examples:

- Missing field
- Invalid email
- Wrong data type

---

# 10. FastAPI vs ASP.NET Core

ASP.NET Core

```csharp
app.UseExceptionHandler();
```

↓

Middleware

↓

Exception Handler

↓

Response

---

FastAPI

```python
@app.exception_handler(...)
```

↓

Exception Handler

↓

JSON Response

Different syntax.

Same architectural idea.

---

# Production Strategy

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

Exception

↓

Logger

↓

Global Exception Handler

↓

JSON Response
```

Every exception follows one predictable path.

---

# Best Practices

✅ Raise exceptions in the Service layer.

✅ Keep Routers thin.

✅ Use domain-specific exceptions.

✅ Log exceptions.

✅ Return consistent JSON responses.

✅ Never expose internal stack traces to users.

---

# Common Beginner Mistakes

❌ Raising `HTTPException` inside repositories.

❌ Writing business logic inside routers.

❌ Returning different error formats from different endpoints.

❌ Catching every exception everywhere.

❌ Exposing database errors directly to clients.

---

# Why Raise Exceptions in the Service Layer?

Repository:

Returns reality.

Example:

```python
return None
```

Service:

Applies business rules.

Example:

```python
if student is None:

    raise StudentNotFoundException(...)
```

Router:

Simply calls the Service.

The Global Exception Handler converts the exception into an HTTP response.

This separation keeps business logic independent of FastAPI and follows Clean Architecture principles.

---

# Interview Questions

### Q1. Why use global exception handling?

It centralizes error handling, avoids duplicate code, and provides consistent API responses.

---

### Q2. Why create custom exceptions?

They represent business concepts, improve readability, and decouple business logic from framework-specific code.

---

### Q3. Where should exceptions be raised in Clean Architecture?

Business-related exceptions should be raised in the Service layer, where business rules are enforced.

---

### Q4. Why shouldn't repositories raise business exceptions?

Repositories are responsible only for data access. They should return data (or `None`) and allow the Service layer to decide whether a missing record is an error.

---

### Q5. Why shouldn't routers contain business logic?

Routers should only translate HTTP requests into service calls. Keeping them thin improves maintainability and prevents duplicated business rules.

---

# Cheat Sheet

```text
Repository

↓

Return Data / None

↓

Service

↓

Raise Business Exception

↓

Global Exception Handler

↓

HTTP Response
```

---

```python
raise StudentNotFoundException(...)
```

↓

```python
@app.exception_handler(...)
```

↓

```json
{
  "success": false,
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

---

# 🏗 Why does this exist?

## What problem does it solve?

Without centralized exception handling:

- every endpoint handles errors differently,
- responses become inconsistent,
- maintenance becomes difficult.

Global exception handling creates one predictable error pipeline for the entire application.

---

## Who depends on it?

```text
Client

↓

Router

↓

Service

↓

Global Exception Handler

↓

Frontend

↓

Developers
```

Both frontend developers and backend developers benefit from standardized error handling.

---

## Who should NOT depend on it?

Repositories.

Repositories should only access data.

They should never know how HTTP responses are generated.

---

## ASP.NET Core Equivalent

```csharp
UseExceptionHandler()
```

---

## FastAPI Equivalent

```python
@app.exception_handler(...)
```

---

# Key Takeaways

- Exceptions represent abnormal situations in the application.
- Business exceptions belong in the Service layer.
- Global exception handlers provide consistent API responses.
- Logging and exception handling complement each other.
- Clean Architecture separates data access, business logic, and HTTP concerns.
- Never expose internal implementation details to API clients.

---

# Revision Checklist

- [ ] Understand why global exception handling is needed.
- [ ] Can use `HTTPException`.
- [ ] Can create custom exceptions.
- [ ] Know where exceptions should be raised.
- [ ] Understand the responsibility of Repository, Service, Router, and Global Exception Handler.
- [ ] Can explain the complete exception flow.
- [ ] Can compare FastAPI and ASP.NET Core exception handling.

---

# Tomorrow's Preview

- Application Configuration Management
- Environment Variables
- `.env` Files
- Pydantic Settings
- Secure Secret Management
- Production Configuration Strategies
