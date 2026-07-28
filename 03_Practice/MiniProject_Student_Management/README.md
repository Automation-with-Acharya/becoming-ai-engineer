# Student Management System

A modular Python **REST API** built using **FastAPI**, **Clean Architecture principles**, the **Repository Pattern**, and **Dependency Injection** — backed by **PostgreSQL** via `psycopg`.

> 📖 For a full breakdown of every version change (what, why, how, where, when), see [version_history.md](version_history.md).

---

## 📁 Project Structure

```text
MiniProject_Student_Management/
│
├── app.py                          # Uvicorn runner: launches the FastAPI server with hot-reload
├── main.py                         # FastAPI app: lifespan hooks, middleware, routers, error handlers
├── dependencies.py                 # DI module: wires DatabaseHelper → Repository → Service
├── logger_config.py                # Logging config: central Logger, FileHandler, StreamHandler, Formatter
│
├── logs/                           # Auto-created log output directory (Day 017)
│   └── application.log             # All application log records (DEBUG+) written here
│
├── middleware/                     # HTTP Middleware (Day 016)
│   ├── __init__.py
│   └── request_middleware.py       # Request logging, execution time, console log, order demo
│
├── auth/                           # JWT Authentication (Day 015)
│   ├── __init__.py
│   ├── password_utils.py           # bcrypt password hashing & verification via passlib
│   ├── jwt_utils.py                # JWT generation, decoding, and inspection
│   └── jwt_bearer.py               # OAuth2PasswordBearer dependency (get_current_user)
│
├── routers/
│   ├── students.py                 # Router layer: HTTP routes & request/response handling
│   └── auth.py                     # Auth router: login, demo, inspect-token, profile endpoints
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
├── version_history.md              # Full changelog: what/why/how/where/when for every version
└── README.md                       # This file
```

---

## 💡 Architecture Overview

```
HTTP Request
     │
     ▼
┌─────────────────┐
│   Middleware    │  middleware/request_middleware.py  ← logging, timing, CORS, order demo
└────────┬────────┘
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
| **Logging Config** | `logger_config.py` | Configures `student_management` root logger — `FileHandler` (DEBUG → `logs/application.log`) + `StreamHandler` (INFO → console) + shared `Formatter`; exposes `get_logger()` |
| **Middleware** | `middleware/request_middleware.py` | Request logging, execution timing, console logging, CORS, order demo |
| **Model** | `models/student.py` | Two Pydantic models: `Student_model` (request body) and `Student_response_model` (response body) |
| **Schema** | `schemas/student_schema.py` | Validates & sanitizes raw user input (e.g. non-empty name) |
| **Database Helper** | `database/database_helper.py` | Manages connection lifecycle, executes raw SQL via `psycopg` |
| **Repository** | `repositories/student_repository.py` | Abstracts storage; `PostgresStudentRepository` implements CRUD |
| **Service** | `services/student_service.py` | Orchestrates validation + repository calls; pure business logic |
| **Router** | `routers/students.py` | Maps HTTP endpoints to service operations; raises `HTTPException` |
| **Auth Utils** | `auth/password_utils.py` | bcrypt password hashing (`hash_password`) and verification (`verify_password`) via `passlib` |
| **JWT Utils** | `auth/jwt_utils.py` | JWT creation (`create_access_token`), decoding (`decode_token`), inspection (`inspect_token_parts`) |
| **JWT Bearer** | `auth/jwt_bearer.py` | `get_current_user` FastAPI dependency; `OAuth2PasswordBearer` extraction + validation |
| **Auth Router** | `routers/auth.py` | Login, demo hash, demo token, inspect-token, and protected profile endpoints |
| **DI Module** | `dependencies.py` | Single-responsibility wiring via `Depends()` chain |
| **Main App** | `main.py` | Bootstraps FastAPI, registers middleware + routers, defines lifespan & error handlers |
| **Runner** | `app.py` | Launches Uvicorn server with hot-reload enabled |

---

## ✨ Features

### REST API Endpoints

#### Student Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root health check & welcome message |
| `POST` | `/students/` | Create a new student (validates name) |
| `GET` | `/students/` | Retrieve all registered students |
| `GET` | `/students/search?query=<name>` | Case-insensitive name search via PostgreSQL `ILIKE` |
| `GET` | `/students/{student_id}` | Get a specific student by ID |
| `DELETE` | `/students/{student_id}` | Delete a student by ID |

#### Authentication Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/auth/login` | ❌ No | Authenticate with username + password (form); receive a signed JWT |
| `GET` | `/auth/demo/hash` | ❌ No | Live demo of bcrypt hashing + salt proof + verification |
| `GET` | `/auth/demo/token` | ❌ No | Generate a demo JWT and inspect Header/Payload/Signature |
| `POST` | `/auth/inspect-token` | ❌ No | Paste any JWT to decode its three parts (no sig verification) |
| `GET` | `/auth/profile` | ✅ Yes | Protected endpoint — returns claims from the verified JWT |

**Demo credentials:** `admin/admin123` · `alice/student456` · `bob/teacher789`

### Key Design Features

**Core API**
- ➕ **Create Student** — auto-assigns next available ID; stores `name`, `age`, `city`, `email`
- 📋 **List All Students** — ordered by ID; returns empty list if none exist
- 🔍 **Case-Insensitive Search** — `ILIKE` pattern matching on name
- 🎯 **Get by ID** — returns `404 Not Found` if student does not exist
- ❌ **Delete by ID** — returns `404 Not Found` if student does not exist
- 📨 **Split Request/Response Models** — `Student_model` for client input, `Student_response_model` for server output
- ✅ **Field-Level Validation** — Pydantic `Field` constraints enforce `min_length`, `max_length`, and `ge=0` at the model layer
- 📧 **Email Validation** — `EmailStr` type ensures the email field is a valid email address format

**Infrastructure**
- 🌐 **Swagger UI** — interactive API docs auto-generated at `/docs`
- 🔒 **Global Error Handler** — `ValueError` anywhere in the stack → clean HTTP `400 Bad Request`
- ⚡ **Lifespan Management** — DB connects on startup, disconnects gracefully on shutdown
- 💉 **Dependency Injection** — `DatabaseHelper → Repository → Service` wired via `Depends()`
- 🔄 **Swappable Repository** — swap `PostgresStudentRepository` for any other backend with zero service-layer changes

**Authentication**
- 🔑 **JWT Authentication** — HS256 signed tokens with `sub`, `role`, `exp`, `iat` claims via `python-jose`
- 🛡️ **Bearer Token Protection** — `OAuth2PasswordBearer` + `get_current_user` dependency guards protected routes
- 🔐 **Password Hashing** — bcrypt via `passlib`; constant-time verification prevents timing attacks
- 🧪 **Auth Demo Endpoints** — educational endpoints to explore hashing, token structure, and Swagger Bearer auth

**Logging (Day 017)**
- 📋 **Centralized Logger** — `logger_config.py` sets up the `student_management` root logger with `FileHandler` + `StreamHandler` + shared `Formatter`
- 📄 **File Logging** — All records (`DEBUG` and above) written to `logs/application.log`; console shows `INFO` and above only
- 🔁 **Structured Log Levels** — `DEBUG` for trace details, `INFO` for operations, `WARNING` for missing resources & auth failures, `ERROR`/`EXCEPTION` for server errors
- 🧩 **Exception Logging** — `logger.exception()` inside every `try/except` block captures full Python stack traces in the log file
- 🔌 **Consistent Format** — All log lines share the format: `timestamp | LEVEL | module.name | message`
- ♻️ **Zero `print()` Statements** — Every `print()` across all layers replaced with appropriate logger calls

**Middleware**
- 📝 **Request Logging** — logs `Incoming Request: METHOD /path` on every request (`logger.info()`)
- ⏱️ **Execution Time** — measures round-trip ms; adds `X-Process-Time-Ms` response header; timing logged at `DEBUG` level
- 🖥️ **Console Logging** — logs `METHOD /path -> STATUS` after each request; level varies by status code (INFO/WARNING/ERROR)
- 🌍 **CORS** — `http://localhost:5173` allowed; all methods & headers
- 🔀 **Middleware Order Demo** — two sequential middleware (A & B) show LIFO pipeline execution; steps logged at `DEBUG` level

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
| **python-jose** | JWT generation, signing (HS256), and decoding |
| **passlib[bcrypt]** | Secure password hashing with bcrypt + `CryptContext` abstraction |
| **logging** (stdlib) | Python standard library logging — `Logger`, `FileHandler`, `StreamHandler`, `Formatter` |

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
   pip install fastapi uvicorn psycopg pydantic pydantic[email] python-jose passlib[bcrypt]
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

### Why Middleware as Classes?

All middleware subclass `BaseHTTPMiddleware` (Starlette). This is required when registering via `app.add_middleware()` — the method expects a class, not a function. Classes also allow middleware to hold state (e.g. config, counters) in `__init__` if needed. The equivalent function-based approach uses the `@app.middleware("http")` decorator and produces identical runtime behaviour.
