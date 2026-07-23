# Day 014 — Pydantic Validation & Request/Response Models

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 23 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand why validation is required in backend applications.
- Use Pydantic models for request validation.
- Use `Field()` for validation rules and documentation.
- Create separate Request and Response models.
- Understand response serialization.
- Build clean, production-ready FastAPI endpoints.
- Explain how validation fits into enterprise backend architecture.

---

# Big Picture

Until yesterday, our API could receive requests and return proper HTTP responses.

Today, we ensure that **only valid data is allowed into the application**.

---

# Evolution of Our Backend

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

Router

↓

HTTP Status Code

↓

Browser
```

---

## Day 14

```text
Browser

↓

JSON Request

↓

Pydantic Validation

↓

APIRouter

↓

Service

↓

Repository

↓

Database

↓

Response Model

↓

JSON Response

↓

Browser
```

---

# 1. Why Validation Matters

Imagine a client sends:

```json
{
  "name": "",
  "age": -5,
  "email": "abc"
}
```

Should this reach the database?

**No.**

Bad data should be rejected immediately.

Validation prevents invalid data from entering the business logic.

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

YES

↓

Router

↓

Service

↓

Repository

↓

Database
```

Invalid data never reaches the Service Layer.

---

# 2. What is Pydantic?

Pydantic is the data validation library used by FastAPI.

It provides:

- Automatic validation
- Type conversion
- Error messages
- API documentation generation
- Serialization

Everything happens automatically.

---

# Example

```python
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    age: int
```

If the client sends:

```json
{
  "name": "Mayank",
  "age": "27"
}
```

Pydantic automatically converts:

```text
"27"

↓

27
```

---

# 3. Request Models

A Request Model defines the data the client is allowed to send.

Example:

```python
from pydantic import BaseModel

class StudentCreate(BaseModel):
    name: str
    age: int
    city: str
```

Every incoming request must match this structure.

---

# Request Lifecycle

```text
Client

↓

StudentCreate

↓

Validation

↓

Router
```

---

# 4. Response Models

A Response Model defines what the API sends back.

Example:

```python
class StudentResponse(BaseModel):
    id: int
    name: str
    city: str
```

Even if the Service returns extra fields, FastAPI filters them.

---

# Why Separate Request & Response Models?

Imagine a User API.

Request:

```json
{
  "username": "mayank",
  "password": "secret123"
}
```

Response:

```json
{
  "id": 1,
  "username": "mayank"
}
```

The password should never be returned.

Separate models make this easy and secure.

---

# 5. Field()

`Field()` adds validation rules and documentation.

Example:

```python
from pydantic import Field

name: str = Field(
    min_length=2,
    max_length=50,
    description="Student Name"
)
```

---

# Common Constraints

## String

```python
name: str = Field(
    min_length=2,
    max_length=50
)
```

---

## Integer

```python
age: int = Field(
    gt=0,
    lt=100
)
```

---

## Decimal

```python
price: float = Field(
    gt=0
)
```

---

## Examples

```python
city: str = Field(
    examples=["Ahmedabad"]
)
```

Swagger automatically displays these examples.

- In Pydantic (both v1 and v2), passing examples=["Ahmedabad"] to Field is purely for documentation metadata (such as OpenAPI/Swagger schemas and JSON Schema exports).

- It does not perform any data validation or check incoming values against the example provided.

- If you want to restrict to a specific list of allowed cities, then use Enum or Literal:

```python
from typing import Literal
from pydantic import BaseModel, Field

class Address(BaseModel):
    # Strictly validates that input must be one of these exact strings
    city: Literal["Ahmedabad", "Mumbai", "Delhi"] = Field(
        examples=["Ahmedabad"]
    )
```

---

# 6. Optional Fields

Not every field must be required.

Example:

```python
from typing import Optional

phone: Optional[str] = None
```

Now the client may omit the field.

---

# 7. Default Values

Example:

```python
country: str = "India"
```

If the client doesn't provide it:

```text
country = India
```

---

# 8. Email Validation

Pydantic provides built-in email validation.

```python
from pydantic import EmailStr

email: EmailStr
```

Example:

Valid:

```text
mayank@gmail.com
```

Invalid:

```text
abc
```

The request is rejected automatically.

---

# 9. Response Serialization

Suppose your Service returns:

```python
{
    "id":1,
    "name":"Mayank",
    "password":"123",
    "city":"Ahmedabad"
}
```

Response Model:

```python
class StudentResponse(BaseModel):
    id:int
    name:str
    city:str
```

Actual API Response:

```json
{
  "id": 1,
  "name": "Mayank",
  "city": "Ahmedabad"
}
```

Password disappears automatically.

---

# Serialization Flow

```text
Service

↓

Python Object

↓

Response Model

↓

JSON

↓

Client
```

---

# 10. Validation Errors

Suppose:

```json
{
  "name": "A",
  "age": -5
}
```

FastAPI automatically returns:

```text
422 Unprocessable Entity
```

Along with detailed validation messages.

You don't write any validation code yourself.

---

# 11. Architecture

```text
Client

↓

JSON

↓

Pydantic

↓

Router

↓

Dependency Injection

↓

Service

↓

Repository

↓

Database

↓

Repository

↓

Service

↓

Response Model

↓

JSON

↓

Client
```

This is a production-grade request flow.

---

# 12. Responsibilities

| Layer          | Responsibility         |
| -------------- | ---------------------- |
| Pydantic       | Validate incoming data |
| Router         | Handle HTTP requests   |
| Service        | Business logic         |
| Repository     | Database operations    |
| Database       | Persistent storage     |
| Response Model | Filter outgoing data   |

---

# 13. Good vs Bad Design

## ❌ Bad

```text
Router

↓

Manual Validation

↓

Service

↓

Database
```

Problems:

- Duplicate validation
- Hard to maintain
- Easy to forget

---

## ✅ Good

```text
Router

↓

Pydantic

↓

Service

↓

Repository

↓

Database
```

Validation is centralized.

---

# 14. Enterprise Comparison

## ASP.NET Core

```csharp
public class StudentRequest
{
    [Required]
    [StringLength(50)]
    public string Name { get; set; }

    [Range(1,100)]
    public int Age { get; set; }
}
```

---

## FastAPI

```python
class StudentRequest(BaseModel):

    name: str = Field(min_length=2)

    age: int = Field(gt=0)
```

Same idea.

Different syntax.

---

# 15. Production Best Practices

✅ Separate Request and Response models.

✅ Validate data before it reaches business logic.

✅ Use `Field()` instead of manual checks.

✅ Hide sensitive fields in responses.

✅ Let Pydantic perform automatic serialization.

---

# Common Beginner Mistakes

❌ Using one model for everything.

❌ Returning database objects directly.

❌ Writing manual validation.

❌ Exposing internal fields.

❌ Skipping Response Models.

---

# Interview Questions

### Q1. Why does FastAPI use Pydantic?

To validate, parse, and serialize request and response data automatically.

---

### Q2. Why separate Request and Response Models?

To control what clients can send and what the API exposes back, improving security and maintainability.

---

### Q3. What does `Field()` do?

It defines validation constraints, metadata, descriptions, and examples for model fields.

---

### Q4. What happens if validation fails?

FastAPI automatically returns **422 Unprocessable Entity** with detailed validation errors.

---

### Q5. Why use `EmailStr`?

It validates email addresses automatically without writing custom validation logic.

---

# Cheat Sheet

```text
Client

↓

Request Model

↓

Validation

↓

Router

↓

Service

↓

Repository
```

---

```python
name: str = Field(
    min_length=2,
    max_length=50
)
```

---

```python
age: int = Field(
    gt=0,
    lt=100
)
```

---

```python
email: EmailStr
```

---

```python
response_model=StudentResponse
```

---

# 🏗 Why does this exist?

## What problem does it solve?

Without validation, invalid or malicious data could reach your business logic and database.

Pydantic ensures only well-formed, validated data enters the application.

---

## Who depends on it?

```text
Client

↓

Pydantic Validation

↓

Router

↓

Service
```

Every incoming request passes through validation before reaching the application's core logic.

---

## Who should NOT depend on it?

The **Repository Layer**.

Repositories should work with already validated domain objects or data and remain independent of HTTP or API-specific validation concerns.

---

## ASP.NET Core Equivalent

```csharp
[Required]
[StringLength(50)]
[Range(1,100)]
```

Model validation occurs before the controller action executes.

---

## FastAPI Equivalent

```python
class StudentRequest(BaseModel):

    name: str = Field(min_length=2)

    age: int = Field(gt=0)
```

Validation happens automatically before the router function is called.

---

# Key Takeaways

- Pydantic provides automatic validation, parsing, and serialization.
- Request Models define accepted input.
- Response Models define exposed output.
- `Field()` adds validation rules and documentation.
- Validation should happen before business logic.
- Separate Request and Response models improve security and maintainability.
- The same architectural principle exists across FastAPI, ASP.NET Core, Spring Boot, and other enterprise frameworks.

---

# Revision Checklist

- [ ] Can explain why validation is important.
- [ ] Know the difference between Request and Response Models.
- [ ] Can use `Field()` for validation.
- [ ] Understand Optional fields and default values.
- [ ] Can use `EmailStr`.
- [ ] Know why FastAPI returns **422** for validation failures.
- [ ] Can explain the complete validation lifecycle.

---

# Tomorrow's Preview

- Authentication vs Authorization
- JWT (JSON Web Tokens)
- Password hashing with `passlib`
- Login & protected endpoints
- Building secure APIs with FastAPI
