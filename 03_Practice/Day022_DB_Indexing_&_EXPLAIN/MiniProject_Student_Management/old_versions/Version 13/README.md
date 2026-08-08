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
├── config.py                       # Configuration: Pydantic Settings reads .env into typed attributes
├── logger_config.py                # Logging config: central Logger, FileHandler, StreamHandler, Formatter
├── .env                            # Local environment variables (never commit — add to .gitignore)
├── .env.example                    # Safe template for .env — commit this instead
│
├── exceptions/                     # Custom exceptions package (Day 018)
│   ├── __init__.py
│   └── student_exceptions.py       # StudentNotFoundException — raised by service, caught by global handler
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
| **Config** | `config.py` + `.env` | Pydantic `Settings` class loads all environment variables from `.env`; single `settings` singleton imported by all modules that need config |
| **Logging Config** | `logger_config.py` | Configures `student_management` root logger — `FileHandler` (DEBUG → `logs/application.log`) + `StreamHandler` (level from `settings.log_level`) + shared `Formatter`; exposes `get_logger()` |
| **Exceptions** | `exceptions/student_exceptions.py` | Custom domain exceptions (`StudentNotFoundException`) raised by the service layer and caught by global handlers in `main.py` |
| **Middleware** | `middleware/request_middleware.py` | Request logging, execution timing, console logging, CORS, order demo |
| **Model** | `models/student.py` | Two Pydantic models: `Student_model` (request body) and `Student_response_model` (response body) |
| **Schema** | `schemas/student_schema.py` | Validates & sanitizes raw user input (e.g. non-empty name) |
| **Database Helper** | `database/database_helper.py` | Manages connection lifecycle, executes raw SQL via `psycopg`; reads DB credentials from `settings` |
| **Repository** | `repositories/student_repository.py` | Abstracts storage; `PostgresStudentRepository` implements CRUD |
| **Service** | `services/student_service.py` | Orchestrates validation + repository calls; raises `StudentNotFoundException` for missing records |
| **Router** | `routers/students.py` | Maps HTTP endpoints to service operations; no manual not-found checks needed |
| **Auth Utils** | `auth/password_utils.py` | bcrypt password hashing (`hash_password`) and verification (`verify_password`) via `passlib` |
| **JWT Utils** | `auth/jwt_utils.py` | JWT creation (`create_access_token`), decoding (`decode_token`), inspection (`inspect_token_parts`); reads secret from `settings` |
| **JWT Bearer** | `auth/jwt_bearer.py` | `get_current_user` FastAPI dependency; `OAuth2PasswordBearer` extraction + validation |
| **Auth Router** | `routers/auth.py` | Login, demo hash, demo token, inspect-token, and protected profile endpoints |
| **DI Module** | `dependencies.py` | Single-responsibility wiring via `Depends()` chain |
| **Main App** | `main.py` | Bootstraps FastAPI, registers middleware + routers, defines lifespan & global exception handlers; reads app name/version from `settings` |
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

**Configuration (Day 019)**
- ⚙️ **Pydantic Settings** — `config.py` defines a typed `Settings` class; reads from `.env` automatically via `pydantic-settings`
- 🔐 **JWT Secret from `.env`** — `JWT_SECRET_KEY` moved out of `jwt_utils.py` hardcode; `auth/jwt_utils.py` reads it via `settings.jwt_secret_key`
- 🗄️ **DB Config from `.env`** — `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` consolidated into `settings`; `database_helper.py` reads from `settings` (no more scattered `os.getenv()`)
- 📋 **Log Level from `.env`** — `LOG_LEVEL=INFO` controls console output; change to `DEBUG` to see trace-level detail without touching source code
- 🏷️ **App Metadata from `.env`** — `APP_NAME` and `APP_VERSION` shown in Swagger UI title and startup log
- 🛡️ **`.env.example`** — safe template committed to version control; `.env` contains real secrets and should be in `.gitignore`

**Infrastructure**
- 🌐 **Swagger UI** — interactive API docs auto-generated at `/docs`
- 🔒 **Global Error Handlers** — `ValueError` → HTTP `400`; `StudentNotFoundException` → HTTP `404`; catch-all `Exception` → HTTP `500` with structured JSON
- ⚡ **Lifespan Management** — DB connects on startup, disconnects gracefully on shutdown
- 💉 **Dependency Injection** — `DatabaseHelper → Repository → Service` wired via `Depends()`
- 🔄 **Swappable Repository** — swap `PostgresStudentRepository` for any other backend with zero service-layer changes

**Exception Handling (Day 018)**
- 🎯 **Custom Exception** — `StudentNotFoundException` carries `student_id`; raised by service layer, keeping routers clean
- 🌍 **Global Handler: 404** — `@app.exception_handler(StudentNotFoundException)` → consistent `{error, message, student_id}` JSON
- 🛡️ **Global Handler: 400** — `@app.exception_handler(ValueError)` → consistent `{error, message, detail}` JSON
- 🚨 **Global Handler: 500** — `@app.exception_handler(Exception)` catch-all → `{error, message, exception_type}` JSON; full stack trace logged server-side only
- 📋 **Exception Logging** — all handlers log via centralized logger (`WARNING` for client errors, `EXCEPTION` for server errors)

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
| **pydantic-settings** | `BaseSettings` for typed .env / environment variable loading |
| **pydantic[email]** | `EmailStr` type for email format validation |
| **python-dotenv** | Reads `.env` file into the process environment |
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
   pip install fastapi uvicorn psycopg pydantic pydantic[email] python-jose passlib[bcrypt] pydantic-settings python-dotenv
   ```
4. Copy the environment template and fill in your values:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and secret key
   ```

### Configuration

All settings are managed in the **`.env`** file (loaded by `config.py` via Pydantic Settings):

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` |  *(set in .env)*  | Application name shown in Swagger UI |
| `APP_VERSION` |  *(set in .env)*  | API version shown in Swagger UI |
| `DEBUG` | `false` | Debug mode flag |
| `JWT_SECRET_KEY` | *(set in .env)* | HMAC-SHA256 signing secret for JWTs |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry duration in minutes |
| `DB_HOST` |  *(set in .env)*  | PostgreSQL server host |
| `DB_PORT` |  *(set in .env)*  | PostgreSQL server port |
| `DB_NAME` | *(set in .env)*  | PostgreSQL database name |
| `DB_USER` |  *(set in .env)*  | PostgreSQL username |
| `DB_PASSWORD` | *(set in .env)* | PostgreSQL password |
| `LOG_LEVEL` | `INFO` | Console log level (`DEBUG`/`INFO`/`WARNING`/`ERROR`) |

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

### Why a Configuration Module?

`config.py` uses Pydantic `BaseSettings` to define every setting as a typed Python attribute. Pydantic reads values from the `.env` file automatically (via `python-dotenv`) and falls back to declared defaults.

- **Type safety**: `DEBUG=yes` in `.env` raises a validation error at startup rather than silently misbehaving.
- **Single source of truth**: `from config import settings` gives any module access to all config — no scattered `os.getenv()` calls.
- **Separation of environments**: Change `.env` for dev/staging/prod without touching source code.
- **Security**: Real secrets stay in `.env` (not committed); `.env.example` is the safe, committable template.

### Why a Global Exception Handler?

Instead of scattering `try/except` blocks inside every route function, a global handler in `main.py` catches each exception type at a single point and returns a consistent, structured JSON response.

- **`StudentNotFoundException`** → HTTP 404 with `{error, message, student_id}` — raised by the service layer, never by the router
- **`ValueError`** → HTTP 400 with `{error, message, detail}` — raised by schema validation
- **`Exception` (catch-all)** → HTTP 500 with `{error, message, exception_type}` — no raw error details leak to the client; full stack trace goes to the log file only

### Why Middleware as Classes?

All middleware subclass `BaseHTTPMiddleware` (Starlette). This is required when registering via `app.add_middleware()` — the method expects a class, not a function. Classes also allow middleware to hold state (e.g. config, counters) in `__init__` if needed. The equivalent function-based approach uses the `@app.middleware("http")` decorator and produces identical runtime behaviour.
