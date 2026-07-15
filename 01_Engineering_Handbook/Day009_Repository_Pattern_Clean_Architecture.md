# Day 009 — Repository Pattern, Data Access Layer & Clean Architecture

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 15 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Explain Separation of Concerns.
- Understand Layered Architecture.
- Explain Repository Pattern.
- Differentiate Database Helper vs Repository.
- Understand Data Access Layer (DAL).
- Understand Service Layer.
- Understand Clean Architecture.
- Design maintainable backend applications.

---

# Big Picture

Today is not about writing more code.

It's about learning **how professional software is organized**.

This is one of the biggest differences between:

```text
Junior Developer
```

and

```text
Senior / Principal Engineer
```

Junior engineers ask:

> "How do I write this feature?"

Senior engineers ask:

> "Where should this feature belong?"

---

# 1. Evolution of Our Project

## Day 03

```text
+---------------------+
| Student CLI         |
+---------------------+
           |
           v
+---------------------+
| students.txt        |
+---------------------+
```

Everything was inside one application.

---

## Day 07

```text
+---------------------+
| Student CLI         |
+---------------------+
           |
           v
+---------------------+
| PostgreSQL          |
+---------------------+
```

We replaced text files with a database.

---

## Day 08

```text
+---------------------+
| Student CLI         |
+---------------------+
           |
           v
+---------------------+
| Database Helper     |
+---------------------+
           |
           v
+---------------------+
| PostgreSQL          |
+---------------------+
```

Database access became reusable.

---

## Day 09

```text
+----------------------+
| Presentation (CLI)   |
+----------------------+
            |
            v
+----------------------+
| Service Layer        |
+----------------------+
            |
            v
+----------------------+
| Repository Layer     |
+----------------------+
            |
            v
+----------------------+
| Database Helper      |
+----------------------+
            |
            v
+----------------------+
| PostgreSQL           |
+----------------------+
```

Now every layer has a single responsibility.

---

# 2. Separation of Concerns (SoC)

## Definition

Each layer should have **one responsibility**.

Bad example:

```text
CLI

↓

SQL

↓

Validation

↓

Business Logic

↓

Printing

↓

Everything mixed together
```

Good example:

```text
CLI
↓

Service
↓

Repository
↓

Database
```

Every layer does only one job.

---

# Why?

Imagine changing PostgreSQL to SQL Server.

If SQL exists everywhere:

❌ Hundreds of files change.

If SQL exists only in Repository:

✅ One place changes.

---

# 3. Layered Architecture

A Layered Architecture separates the application into logical layers.

```text
+-----------------------------+
| Presentation Layer          |
| CLI / Web / API             |
+-----------------------------+
              |
              v
+-----------------------------+
| Service Layer               |
| Business Rules              |
+-----------------------------+
              |
              v
+-----------------------------+
| Repository Layer            |
| Database Operations         |
+-----------------------------+
              |
              v
+-----------------------------+
| Database                    |
+-----------------------------+
```

Each layer only communicates with the layer directly below it.

---

# 4. Database Helper

## Purpose

The Database Helper manages:

- Opening connections
- Closing connections
- Executing SQL
- Committing transactions

Example:

```python
db.execute(...)
```

It knows **how to talk to PostgreSQL**.

It does **not** know anything about Students, Courses, or Business Rules.

---

# 5. Repository Pattern

## Definition

A Repository represents a collection of domain objects.

Instead of:

```python
cursor.execute(...)
```

the application says:

```python
student_repository.get_all()
```

The Repository hides SQL.

---

## Repository Diagram

```text
Application

↓

StudentRepository

↓

SQL

↓

PostgreSQL
```

The application never writes SQL directly.

---

# Repository Responsibilities

✔ Execute SQL

✔ Convert database rows into objects

✔ Retrieve data

✔ Save data

Should NOT:

❌ Print output

❌ Ask user input

❌ Validate business rules

---

# 6. Service Layer

The Service Layer contains business logic.

Example:

Requirement:

Students under 18 cannot enroll.

Where should this rule go?

NOT:

```text
CLI
```

NOT:

```text
Repository
```

Correct:

```text
Service Layer
```

Because it is a business rule.

---

# Service Layer Diagram

```text
CLI

↓

StudentService

↓

StudentRepository

↓

Database
```

---

# Responsibilities

Service:

✔ Validation

✔ Business Rules

✔ Decision Making

Repository:

✔ SQL

✔ Data Access

---

# 7. Data Access Layer (DAL)

The Data Access Layer is the part of the application responsible for communicating with the database.

Our Repository belongs inside the DAL.

```text
Application

↓

DAL

↓

Database
```

Inside DAL:

```text
StudentRepository

CourseRepository

EnrollmentRepository

DatabaseHelper
```

---

# 8. Clean Architecture

Clean Architecture organizes software into layers that depend inward.

```text
+--------------------------------------+
| Presentation                         |
| CLI / FastAPI / React                |
+--------------------------------------+
                 |
                 v
+--------------------------------------+
| Application                          |
| Services                             |
+--------------------------------------+
                 |
                 v
+--------------------------------------+
| Domain                              |
| Models / Business Rules             |
+--------------------------------------+
                 |
                 v
+--------------------------------------+
| Infrastructure                      |
| Repository / PostgreSQL / Files     |
+--------------------------------------+
```

---

# Dependency Rule

Dependencies always point inward.

```text
Presentation
      ↓
Application
      ↓
Domain

Infrastructure
      ↑
```

The Domain never depends on the Database.

The Database depends on the Domain.

---

# 9. Future Project Structure

```text
StudentManagement/

│
├── app.py
│
├── models/
│      student.py
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
├── sql/
│      schema.sql
│
├── tests/
│
└── README.md
```

This is the structure we'll gradually build.

---

# 10. Complete Request Flow

Imagine adding a student.

```text
User

↓

CLI

↓

StudentService

↓

StudentRepository

↓

DatabaseHelper

↓

PostgreSQL

↓

DatabaseHelper

↓

Repository

↓

Service

↓

CLI

↓

User
```

Every layer has one responsibility.

---

# Bad Architecture

```text
CLI

↓

SQL

↓

Validation

↓

Printing

↓

Database

↓

Everything Together
```

Problems:

❌ Hard to maintain

❌ Difficult testing

❌ Duplicate code

❌ Tight coupling

---

# Good Architecture

```text
CLI

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

✅ Modular

✅ Testable

✅ Maintainable

✅ Reusable

✅ Easy to extend

---

# Real-World Mapping

| Our Project     | Enterprise Equivalent        |
| --------------- | ---------------------------- |
| CLI             | React / Angular / Mobile App |
| Service         | Business Logic Layer         |
| Repository      | Data Access Layer            |
| Database Helper | Database Client              |
| PostgreSQL      | Production Database          |

---

# Interview Questions

### Q1. What is Separation of Concerns?

A design principle that divides an application into distinct parts, where each part has a single responsibility. This improves maintainability, readability, and testability.

---

### Q2. What is the Repository Pattern?

A design pattern that abstracts data access by providing methods to retrieve and persist domain objects without exposing SQL to the rest of the application.

---

### Q3. Difference between Repository and Database Helper?

| Repository                    | Database Helper                                  |
| ----------------------------- | ------------------------------------------------ |
| Knows about business entities | Knows only how to communicate with the database  |
| Contains data access methods  | Manages connections, execution, and transactions |
| Returns domain objects        | Executes generic SQL                             |

---

### Q4. What is the Service Layer?

A layer that contains business rules and coordinates application behavior. It sits between the presentation layer and the repository layer.

---

### Q5. What is Clean Architecture?

A software architecture that organizes code into layers with clear responsibilities and inward dependencies, making systems easier to maintain, test, and scale.

---

# Cheat Sheet

```text
Presentation
↓

Service
↓

Repository
↓

Database Helper
↓

PostgreSQL
```

---

```text
Presentation
↓

Application

↓

Domain

↑

Infrastructure
```

---

```text
Repository

↓

Data Access

Service

↓

Business Logic

Database Helper

↓

Database Connection
```

---

# Key Takeaways

- Separation of Concerns keeps each layer focused on a single responsibility.
- Layered Architecture improves maintainability and readability.
- Repository Pattern hides SQL from the rest of the application.
- Service Layer contains business rules and application logic.
- Database Helper centralizes connection and query execution.
- Clean Architecture organizes software into independent layers with clear dependencies.
- Well-structured applications are easier to test, extend, and maintain than tightly coupled codebases.

---

# Revision Checklist

- [ ] Can explain Separation of Concerns.
- [ ] Can draw Layered Architecture from memory.
- [ ] Understand Repository Pattern.
- [ ] Know the difference between Repository and Database Helper.
- [ ] Understand Service Layer responsibilities.
- [ ] Understand the Data Access Layer.
- [ ] Can explain Clean Architecture.
- [ ] Can trace the complete request flow through the application.

---

# Tomorrow's Preview

- FastAPI Fundamentals
- Creating your first REST API
- GET and POST endpoints
- Request & Response models
- Interactive API documentation with Swagger
- Preparing the Student Management project for a web API
