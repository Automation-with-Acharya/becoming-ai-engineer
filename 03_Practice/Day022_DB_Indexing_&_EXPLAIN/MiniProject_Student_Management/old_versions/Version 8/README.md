# Student Management System

A modular Python **REST API** built using **FastAPI**, **Clean Architecture principles**, the **Repository Pattern**, and **Dependency Injection** — backed by **PostgreSQL** via `psycopg`.

---

## 📋 Version History

| Version | Key Theme |
|---|---|
| **v3–v6** | CLI-based student manager (terminal menu loop) |
| **v7** | Migrated to FastAPI REST API; added `age`, `city`; introduced Repository Pattern + DI |
| **v8 (today)** | Split request/response models; added `email` field with `pydantic-email-validator`; added `Field` validation constraints |

---

## 🆕 What Changed Today (v7 → v8)

| Area | Before (v7) | After (v8) |
|---|---|---|
| **Student Fields** | `id`, `name`, `age`, `city` | `id`, `name`, `age`, `city`, **`email`** |
| **Pydantic Model** | Single `Student` class (request + response combined) | Split into `Student_model` (request) and `Student_response_model` (response) |
| **Request `id` field** | `id: int \| None = None` (optional, could be sent by client) | Removed from `Student_model` — client never sends an `id` |
| **Response `id` field** | `id: int \| None` (could be `None`) | `id: int` (required; guaranteed by DB before response is sent) |
| **Field Validation** | No constraints on `name`, `age`, `city` | `Field(min_length=1, max_length=100)` on `name`, `city`; `Field(ge=0)` on `age` |
| **Email Validation** | Not present | `email: EmailStr` with Pydantic `EmailStr` type (requires `pydantic[email]`) |
| **Database Table** | `id`, `name`, `age`, `city` columns | Added `email VARCHAR(100)` column |
| **SQL Queries** | `INSERT ... VALUES (%s, %s, %s, %s)` | `INSERT ... VALUES (%s, %s, %s, %s, %s)` (includes `email`) |
| **Repository signatures** | Used `Student` for both input and output | `add_student` accepts `Student_model`; all return types use `Student_response_model` |
| **Service signatures** | `add_student(name, age, city)` | `add_student(name, age, city, email)` |
| **Router signatures** | Used `Student` for request/response models | Uses `Student_model` for request body, `Student_response_model` for response |

### 🏗️ Why Split Request/Response Models?

> This is a key API design best practice:
> - **`Student_model`** (request) — client sends only `name`, `age`, `city`, `email`. The `id` is intentionally absent because the database always assigns it; clients have no role in choosing it.
> - **`Student_response_model`** (response) — server sends back `id`, `name`, `age`, `city`, `email`. The `id` is a required `int`, never `None`, because by the time the server responds the record already exists in the DB.
> - This makes the **API contract explicit**, prevents leaking `None` ids into responses, and lets FastAPI generate cleaner OpenAPI docs for each direction.

---

## ⬅️ What Changed Previously (v6 → v7)

| Area | Before (v6) | After (v7) |
|---|---|---|
| **Interface** | CLI (terminal menu) | REST API (HTTP endpoints via FastAPI) |
| **Entry Point** | `main.py` (CLI loop) | `main.py` (FastAPI app) + `app.py` (Uvicorn runner) |
| **Student Model** | `id`, `name` | `id`, `name`, `age`, `city` |
| **Database Table** | `id`, `name` only | `id`, `name`, `age`, `city` |
| **Dependency Wiring** | Manual instantiation | FastAPI `Depends()` injection chain |
| **Error Handling** | `print()` / bare exceptions | Global `ValueError` → HTTP 400 handler |
| **App Lifecycle** | No lifecycle management | `@asynccontextmanager` lifespan (startup/shutdown) |
| **Search** | Basic string scan | Case-insensitive PostgreSQL `ILIKE` query |
| **API Docs** | None | Auto-generated Swagger UI at `/docs` |

---

## 📁 Project Structure

```text
MiniProject_Student_Management/
│
├── app.py                          # Uvicorn runner: launches the FastAPI server with hot-reload
├── main.py                         # FastAPI app: lifespan hooks, router registration, error handlers
├── dependencies.py                 # DI module: wires DatabaseHelper → Repository → Service
│
├── routers/
│   └── students.py                 # Router layer: HTTP routes & request/response handling
│
├── services/
│   └── student_service.py          # Service layer: business logic & schema validation orchestration
│
├── repositories/
│   └── student_repository.py       # Repository layer: abstract interface + PostgreSQL implementation
│
├── database/
│   └── database_helper.py          # DB helper: connection management & query execution via psycopg
│
├── models/
│   └── student.py                  # Domain models: Student_model (request) & Student_response_model (response)
│
├── schemas/
│   └── student_schema.py           # Input validation: sanitizes & validates student name
│
└── README.md                       # Project documentation
```

---

## 💡 Architecture Overview

```
HTTP Request
     │
     ▼
┌─────────────────┐
│  Router Layer   │  routers/students.py       ← maps HTTP verbs to service calls
│  (FastAPI)      │
└────────┬────────┘
         │  FastAPI Depends()
         ▼
┌─────────────────┐
│ Service Layer   │  services/student_service.py  ← business logic + schema validation
└────────┬────────┘
         │  depends on abstract interface
         ▼
┌─────────────────┐
│ Repository      │  repositories/student_repository.py
│ (Abstract ABC)  │      StudentRepository (ABC)
│ + Postgres Impl │      PostgresStudentRepository (concrete)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Database Helper │  database/database_helper.py  ← psycopg connection + SQL execution
└─────────────────┘
         │
         ▼
    PostgreSQL DB
```

### Layer Responsibilities

| Layer | File | Responsibility |
|---|---|---|
| **Model** | `models/student.py` | Two Pydantic models: `Student_model` (request body) and `Student_response_model` (response body) |
| **Schema** | `schemas/student_schema.py` | Validates & sanitizes raw user input (e.g. non-empty name) |
| **Database Helper** | `database/database_helper.py` | Manages connection lifecycle, executes raw SQL via `psycopg` |
| **Repository** | `repositories/student_repository.py` | Abstracts storage; `PostgresStudentRepository` implements CRUD |
| **Service** | `services/student_service.py` | Orchestrates validation + repository calls; pure business logic |
| **Router** | `routers/students.py` | Maps HTTP endpoints to service operations; raises `HTTPException` |
| **DI Module** | `dependencies.py` | Single-responsibility wiring via `Depends()` chain |
| **Main App** | `main.py` | Bootstraps FastAPI, registers router, defines lifespan & error handlers |
| **Runner** | `app.py` | Launches Uvicorn server with hot-reload enabled |

---

## ✨ Features

### REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root health check & welcome message |
| `POST` | `/students/` | Create a new student (validates name) |
| `GET` | `/students/` | Retrieve all registered students |
| `GET` | `/students/search?query=<name>` | Case-insensitive name search via PostgreSQL `ILIKE` |
| `GET` | `/students/{student_id}` | Get a specific student by ID |
| `DELETE` | `/students/{student_id}` | Delete a student by ID |

### Key Design Features

- ➕ **Create Student** — auto-assigns next available ID; stores `name`, `age`, `city`, `email`
- 📋 **List All Students** — ordered by ID; returns empty list if none exist
- 🔍 **Case-Insensitive Search** — `ILIKE` pattern matching on name
- 🎯 **Get by ID** — returns `404 Not Found` if student does not exist
- ❌ **Delete by ID** — returns `404 Not Found` if student does not exist
- 🌐 **Swagger UI** — interactive API docs auto-generated at `/docs`
- 🔒 **Global Error Handler** — `ValueError` anywhere in the stack → clean HTTP `400 Bad Request`
- ⚡ **Lifespan Management** — DB connects on startup, disconnects gracefully on shutdown
- 💉 **Dependency Injection** — `DatabaseHelper → Repository → Service` wired via `Depends()`
- 🔄 **Swappable Repository** — swap `PostgresStudentRepository` for any other backend with zero service-layer changes
- 📨 **Split Request/Response Models** — `Student_model` for client input, `Student_response_model` for server output
- ✅ **Field-Level Validation** — Pydantic `Field` constraints enforce `min_length`, `max_length`, and `ge=0` at the model layer
- 📧 **Email Validation** — `EmailStr` type ensures the email field is a valid email address format

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Core language |
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server with hot-reload |
| **Pydantic** | Request/response model validation + `Field` constraints |
| **pydantic[email]** | `EmailStr` type for email format validation |
| **psycopg** | PostgreSQL database driver (v3) |
| **PostgreSQL** | Relational database backend |

---

## 🚀 How to Run

### Prerequisites

1. Ensure **PostgreSQL** is running locally on port `5432`.
2. Create the target database (or use an existing one):
   ```sql
   CREATE DATABASE student_db;
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn psycopg pydantic pydantic[email]
   ```

### Configuration

The `DatabaseHelper` reads connection settings from **environment variables** (falling back to defaults):

| Variable | Default | Description |
|---|---|---|
| `DB_NAME` | `student_db` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL username |
| `DB_PASSWORD` | `password@postgres` | PostgreSQL password |
| `DB_HOST` | `localhost` | Database server host |
| `DB_PORT` | `5432` | Database server port |

> **Note:** The `students` table now includes an `email VARCHAR(100)` column (added in v8). If upgrading from v7, run:
> ```sql
> ALTER TABLE students ADD COLUMN IF NOT EXISTS email VARCHAR(100);
> ```

### Start the Server

```bash
python app.py
```

The server starts at **`http://127.0.0.1:8000`** with hot-reload enabled.

> **Note:** The `students` table is auto-created on first startup if it doesn't exist.

### Access the API

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger UI (interactive API explorer) |
| `http://127.0.0.1:8000/redoc` | ReDoc API documentation |
| `http://127.0.0.1:8000/` | Root health check |

---

## 📖 Architectural Concepts

### Why Dependency Injection?

FastAPI's `Depends()` system is used to build a declarative injection chain:

```
get_db_helper() → get_student_repository() → get_student_service()
```

- **Decoupling**: Router has no knowledge of how `StudentService` or `DatabaseHelper` are created.
- **Testability**: Override any provider in tests without touching production code.
- **Single Responsibility**: Each class focuses on its own logic, not on wiring.

### Why Abstract Repository?

`StudentRepository` (ABC) enforces the **Dependency Inversion Principle**:
- `StudentService` depends on the *interface*, not `PostgresStudentRepository`.
- Swap storage backends (MongoDB, SQLite, in-memory) by only modifying `dependencies.py`.

### Why a Lifespan Handler?

The `@asynccontextmanager lifespan` in `main.py`:
- **Startup**: Connects to PostgreSQL and verifies/creates the table schema once.
- **Shutdown**: Closes the connection cleanly, preventing socket leaks.
- **Efficiency**: A single persistent connection serves all incoming requests.

### Why a Global `ValueError` Handler?

Schema validation and business logic raise `ValueError` for bad inputs. Instead of wrapping every endpoint in `try/except`, a single global handler in `main.py` catches all `ValueError`s and returns a consistent `HTTP 400 Bad Request` JSON response.
