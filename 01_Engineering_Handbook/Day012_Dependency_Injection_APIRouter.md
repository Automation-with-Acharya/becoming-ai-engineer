# Day 012 — Dependency Injection (DI), Depends() & APIRouter

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 21 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand Dependency Injection (DI).
- Understand why DI is important in enterprise applications.
- Learn how FastAPI implements DI using `Depends()`.
- Understand APIRouter and modular API design.
- Organize a FastAPI project using routers, services, and repositories.
- Explain the request lifecycle in a production-style FastAPI application.

---

# Big Picture

As applications grow, putting everything into one file becomes impossible.

Instead of writing:

```text
main.py
│
├── API
├── Business Logic
├── SQL
├── Validation
└── Everything Else
```

Professional applications separate responsibilities.

---

# Evolution of Our Project

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

## Day 11

```text
Browser

↓

FastAPI

↓

Service Layer

↓

Repository

↓

Database
```

---

## Day 12

```text
Browser

↓

APIRouter

↓

Dependency Injection

↓

Service Layer

↓

Repository

↓

Database Helper

↓

PostgreSQL
```

Today's learning focuses on **how these layers communicate**.

---

# 1. What is Dependency Injection?

## Definition

Dependency Injection (DI) is a design pattern where an object receives its required dependencies from an external source instead of creating them itself.

Instead of:

```python
service = StudentService()
```

inside every endpoint,

FastAPI provides it automatically.

---

# Why is DI Needed?

Without DI:

```text
Router

↓

Creates StudentService

↓

Creates Repository

↓

Creates Database
```

Everything becomes tightly coupled.

---

With DI:

```text
Router

↓

Requests StudentService

↓

FastAPI Provides It

↓

Service

↓

Repository

↓

Database
```

The Router no longer worries about object creation.

---

# Real-Life Analogy

Imagine a restaurant.

Without DI:

Customer goes into the kitchen.

Finds ingredients.

Cooks the meal.

Serves themselves.

---

With DI:

Customer orders food.

↓

Waiter receives order.

↓

Kitchen prepares food.

↓

Waiter serves food.

The customer simply receives what they need.

Dependency Injection works the same way.

---

# Benefits of DI

- Loose coupling
- Better testing
- Easier maintenance
- Reusable components
- Cleaner architecture
- Easier dependency replacement

---

# 2. FastAPI Dependency Injection

FastAPI provides dependencies using:

```python
Depends()
```

Example:

```python
from fastapi import Depends

@app.get("/students")
def get_students(service: StudentService = Depends(get_student_service)):
    return service.get_all_students()
```

FastAPI automatically creates and injects the required object.

---

# Dependency Flow

```text
Request

↓

FastAPI

↓

Depends()

↓

StudentService

↓

Repository

↓

Database
```

---

# 3. What is Depends()?

`Depends()` tells FastAPI:

> "I need this object. Please provide it."

Instead of manually writing:

```python
service = StudentService()
```

FastAPI manages it for you.

---

# Depends() Example

```python
def get_student_service():
    return StudentService()

@app.get("/students")
def get_students(
    service: StudentService = Depends(get_student_service)
):
    return service.get_all_students()
```

---

# 4. Why Dependency Injection Matters

Imagine changing PostgreSQL to MongoDB.

Without DI:

```text
Router

↓

StudentRepository()

↓

Postgres
```

Every endpoint changes.

---

With DI:

```text
Router

↓

StudentRepository Interface

↓

MongoRepository

or

↓

PostgresRepository
```

Only one dependency changes.

The Router remains untouched.

---

# 5. What is APIRouter?

As applications grow:

```text
main.py

↓

5000 Lines
```

Not maintainable.

Instead:

```text
routers/

students.py

courses.py

users.py

reports.py
```

Each router manages a single area.

---

# APIRouter Diagram

```text
FastAPI App

│

├── Student Router

├── Course Router

├── User Router

└── Report Router
```

Each router contains only related endpoints.

---

# APIRouter Example

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/students")
def get_students():
    ...
```

Then in `main.py`:

```python
from routers.students import router

app.include_router(router)
```

---

# 6. Modular Project Structure

A professional FastAPI project typically looks like:

```text
StudentManagement/

│
├── main.py
│
├── routers/
│      students.py
│
├── services/
│      student_service.py
│
├── repositories/
│      student_repository.py
│
├── database/
│      database_helper.py
│
├── models/
│      student.py
│
├── schemas/
│      student_schema.py
│
└── README.md
```

Every folder has one responsibility.

---

# 7. Request Lifecycle

```text
Browser

↓

HTTP Request

↓

FastAPI

↓

APIRouter

↓

Depends()

↓

StudentService

↓

StudentRepository

↓

DatabaseHelper

↓

PostgreSQL

↓

Repository

↓

Service

↓

JSON Response

↓

Browser
```

This is almost identical to many enterprise backend systems.

---

# 8. Responsibility of Each Layer

| Layer                | Responsibility                            |
| -------------------- | ----------------------------------------- |
| Router               | Accept HTTP requests and return responses |
| Dependency Injection | Provide required objects                  |
| Service              | Business rules and application logic      |
| Repository           | Database operations                       |
| Database Helper      | Connection and SQL execution              |
| Database             | Persistent storage                        |

---

# 9. Folder Responsibilities

## main.py

Application entry point.

Initializes FastAPI.

Registers routers.

---

## routers/

Contains API endpoints.

Should NOT contain business logic.

---

## services/

Contains business rules.

Coordinates repositories.

---

## repositories/

Reads and writes data.

Should NOT contain HTTP logic.

---

## database/

Database connection and query execution.

---

## models/

Represents domain entities.

---

# 10. Bad Architecture

```text
main.py

↓

SQL

↓

Validation

↓

Business Rules

↓

JSON

↓

Everything Together
```

Problems:

- Difficult testing
- Duplicate code
- Hard maintenance
- Tight coupling

---

# Good Architecture

```text
Router

↓

Depends()

↓

Service

↓

Repository

↓

Database Helper

↓

PostgreSQL
```

Benefits:

- Modular
- Testable
- Scalable
- Maintainable
- Easy to extend

---

# 11. Enterprise Comparison

## ASP.NET Core

```text
Controller

↓

Dependency Injection

↓

Service

↓

Repository

↓

Entity Framework

↓

SQL Server
```

---

## FastAPI

```text
Router

↓

Depends()

↓

Service

↓

Repository

↓

DatabaseHelper

↓

PostgreSQL
```

The architecture is nearly identical.

Only the framework syntax changes.

---

# 12. Future Architecture

Soon our project will evolve into:

```text
React Frontend

↓

FastAPI

↓

Authentication

↓

APIRouter

↓

Dependency Injection

↓

Service Layer

↓

Repository Layer

↓

Database Helper

↓

PostgreSQL
```

This closely resembles modern production backend systems.

---

# Common Beginner Mistakes

❌ Putting SQL directly inside API routes.

❌ Writing all endpoints in `main.py`.

❌ Creating database connections inside every function.

❌ Mixing validation with business logic.

❌ Ignoring project structure until the application becomes large.

---

# Production Best Practices

✅ One responsibility per layer.

✅ Keep routers thin.

✅ Put business rules inside services.

✅ Keep repositories focused on data access.

✅ Use Dependency Injection instead of manually creating objects.

✅ Group endpoints using APIRouter.

---

# Interview Questions

### Q1. What is Dependency Injection?

A design pattern where objects receive their dependencies from an external provider instead of creating them themselves, reducing coupling and improving testability.

---

### Q2. What is `Depends()` in FastAPI?

`Depends()` is FastAPI's Dependency Injection mechanism that automatically provides required objects or services to route handlers.

---

### Q3. Why use APIRouter?

APIRouter helps organize endpoints into modular files, improving maintainability, readability, and scalability.

---

### Q4. Why should routers be thin?

Routers should only handle HTTP requests and responses. Business logic belongs in the Service layer.

---

### Q5. How is FastAPI's DI similar to ASP.NET Core?

Both frameworks have built-in Dependency Injection containers that automatically create and provide required services, promoting loose coupling and clean architecture.

---

# Cheat Sheet

```text
Browser

↓

Router

↓

Depends()

↓

Service

↓

Repository

↓

Database
```

---

```text
Router

↓

HTTP

Service

↓

Business Logic

Repository

↓

Database

Database Helper

↓

SQL Execution
```

---

```text
main.py

↓

include_router()

↓

students.py

↓

Service

↓

Repository
```

---

# Key Takeaways

- Dependency Injection separates object creation from object usage.
- FastAPI implements Dependency Injection using `Depends()`.
- APIRouter organizes endpoints into modular, maintainable files.
- Routers should remain thin and delegate business logic to services.
- Services contain business rules, while repositories handle data access.
- Clean project structure improves scalability, readability, and testing.
- The architectural principles learned today are shared across frameworks such as FastAPI, ASP.NET Core, Spring Boot, and NestJS.

---

# Revision Checklist

- [ ] Understand Dependency Injection.
- [ ] Can explain `Depends()`.
- [ ] Know why DI reduces coupling.
- [ ] Understand APIRouter.
- [ ] Can organize a FastAPI project into modules.
- [ ] Can explain the complete request lifecycle.
- [ ] Understand the responsibilities of each layer.

---

# Tomorrow's Preview

- Full CRUD APIs with FastAPI
- Connecting FastAPI to PostgreSQL through the Repository layer
- HTTP Exception handling
- Status codes and error responses
- Building a production-style Student Management REST API
