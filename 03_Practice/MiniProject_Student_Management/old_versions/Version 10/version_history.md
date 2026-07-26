# Version History — Student Management System

Full changelog for every version of this project: **what** changed, **why** it was changed, **how** it was implemented, **where** in the codebase, and **when** (which day of the course).

---

## v10 — Day 016: Middleware Practice

**When:** Day 016  
**Theme:** HTTP Middleware layer — request pipeline observability and cross-cutting concerns

### What Changed

| Area | Before (v9) | After (v10) |
|---|---|---|
| **Middleware** | None | Five middleware registered via `add_middleware()` in `main.py` |
| **Request Logging** | Not present | `LogIncomingRequestMiddleware` — prints `METHOD /path` on every request |
| **Execution Time** | Not present | `ExecutionTimeMiddleware` — prints duration & adds `X-Process-Time-Ms` response header |
| **Console Logging** | Not present | `ConsoleRequestLogMiddleware` — prints `METHOD /path -> STATUS` after each request |
| **CORS** | Not enabled | `CORSMiddleware` — allows origin `http://localhost:5173`, all methods & headers |
| **Order Demo** | Not present | `MiddlewareOrderDemoA` & `MiddlewareOrderDemoB` — illustrates LIFO middleware pipeline |
| **New Module** | Not present | `middleware/` package: `__init__.py` + `request_middleware.py` |
| **App Version** | `2.0.0` | `3.0.0` |

### Why

Middleware is how real-world APIs handle **cross-cutting concerns** — things that apply to every request without polluting individual route handlers. Logging, timing, CORS, and auth checks all belong in the middleware pipeline, not inside route functions.

### How (Five Exercises)

| Exercise | Class | Mechanism |
|---|---|---|
| **Ex 1** | `LogIncomingRequestMiddleware` | `BaseHTTPMiddleware` subclass; prints before `call_next()` |
| **Ex 2** | `ExecutionTimeMiddleware` | Records `time.time()` before/after `call_next()`; writes `X-Process-Time-Ms` header |
| **Ex 3** | `ConsoleRequestLogMiddleware` | Calls `call_next()`, then prints `response.status_code` |
| **Ex 4** | `CORSMiddleware` | FastAPI built-in; configured with `allow_origins=["http://localhost:5173"]` |
| **Ex 5** | `MiddlewareOrderDemoA` + `MiddlewareOrderDemoB` | Both print on request entry and response exit to show LIFO order |

### Key Concept: LIFO Middleware Stack

FastAPI middleware is a **Last In, First Out** stack. The *last* `add_middleware()` call runs *first* on the incoming request, then response unwinding happens in reverse.

```text
Registration order in main.py → Runtime execution order (request)
──────────────────────────────────────────────────────────────────
1. CORSMiddleware          (added first)  →  runs last on request
2. MiddlewareOrderDemoA                  →  runs 5th on request
3. MiddlewareOrderDemoB                  →  runs 4th on request
4. LogIncomingRequestMiddleware          →  runs 3rd on request
5. ExecutionTimeMiddleware               →  runs 2nd on request
6. ConsoleRequestLogMiddleware (last)    →  runs 1st on request
```

### Where

```
middleware/
├── __init__.py
└── request_middleware.py   ← all five middleware classes
main.py                     ← add_middleware() registration block
```

---

## v9 — Day 015: JWT Authentication

**When:** Day 015  
**Theme:** Security — password hashing, JWT issuance, protected endpoints

### What Changed

| Area | Before (v8) | After (v9) |
|---|---|---|
| **Authentication** | None — all endpoints open | JWT Bearer authentication added |
| **Password Hashing** | Not present | `passlib` + `bcrypt` via `hash_password()` / `verify_password()` |
| **Token Generation** | Not present | `python-jose` HS256 signed JWTs with `sub`, `role`, `exp`, `iat` claims |
| **Token Decoding** | Not present | `decode_token()` verifies signature + expiry; `inspect_token_parts()` for education |
| **Protected Endpoint** | Not present | `GET /auth/profile` — requires valid `Authorization: Bearer <token>` header |
| **Auth Dependency** | Not present | `get_current_user` FastAPI dependency; `OAuth2PasswordBearer` wires Swagger padlock |
| **Login Endpoint** | Not present | `POST /auth/login` — accepts `OAuth2PasswordRequestForm`; returns `TokenResponse` |
| **Demo Endpoints** | Not present | `GET /auth/demo/hash`, `GET /auth/demo/token`, `POST /auth/inspect-token` |
| **New Module** | Not present | `auth/` package: `password_utils.py`, `jwt_utils.py`, `jwt_bearer.py` |
| **New Router** | Not present | `routers/auth.py` registered as `auth_router` in `main.py` |
| **App Version** | `1.0.0` | `2.0.0` |

### Why

All API endpoints were completely open — anyone could create or delete students. Real systems need authentication. JWT (JSON Web Token) is the industry-standard stateless auth mechanism for REST APIs; it doesn't require server-side session storage, scales horizontally, and self-describes the user's identity and role.

bcrypt is used for password hashing because it is intentionally slow (work-factor based), making brute-force attacks computationally expensive.

### How

**Authentication Flow (OAuth2 Bearer pattern):**

1. **Login** — Client POSTs `username` + `password` (form data) to `POST /auth/login`. Server verifies the bcrypt hash with `verify_password()`, then mints a signed JWT using `create_access_token()`.
2. **Token** — The JWT contains `sub` (username), `role`, `exp` (30-min expiry), and `iat` claims, signed with HS256. The client stores this token.
3. **Protected Request** — Client sends `Authorization: Bearer <token>` header. The `get_current_user` dependency (via `OAuth2PasswordBearer`) extracts the token, calls `decode_token()` to verify the signature and expiry, and injects the payload into the route handler.
4. **Rejection** — Any missing, tampered, or expired token returns `HTTP 401 Unauthorized` before the route function even runs.

**Five Exercises:**

| Exercise | Endpoint | What it demonstrates |
|---|---|---|
| **Ex 1** | `GET /auth/demo/hash` | bcrypt hashing + salt proof + `verify_password()` |
| **Ex 1+2** | `POST /auth/login` | Credential check + JWT issuance |
| **Ex 2+3** | `GET /auth/demo/token` | JWT generation + structural inspection |
| **Ex 3** | `POST /auth/inspect-token` | Decode any JWT Header/Payload/Signature (no verification) |
| **Ex 4+5** | `GET /auth/profile` | Protected endpoint + Swagger Bearer auth testing |

### Where

```
auth/
├── __init__.py
├── password_utils.py   ← hash_password(), verify_password() via passlib/bcrypt
├── jwt_utils.py        ← create_access_token(), decode_token(), inspect_token_parts()
└── jwt_bearer.py       ← get_current_user FastAPI dependency + OAuth2PasswordBearer

routers/
└── auth.py             ← all auth endpoints (login, demo/hash, demo/token, inspect-token, profile)

main.py                 ← app.include_router(auth_router)
```

**Demo credentials:** `admin/admin123` · `alice/student456` · `bob/teacher789`

---

## v8 — Day 014: Split Models & Email Validation

**When:** Day 014  
**Theme:** Pydantic model discipline — separate request and response schemas + email field

### What Changed

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

### Why

Using one model for both request and response is a bad practice. It leaks server-generated fields (like `id`) into the request contract and makes the API surface ambiguous. Splitting into `Student_model` (what the client sends) and `Student_response_model` (what the server returns) enforces proper boundaries and makes validation intent explicit.

`EmailStr` was added to demonstrate Pydantic's specialised type validators beyond simple `str`.

### How

- `Student_model` — request body: `name`, `age`, `city`, `email` (no `id`; id is DB-generated)
- `Student_response_model` — response body: `id: int`, `name`, `age`, `city`, `email` (id is guaranteed non-None because it's read from the DB after INSERT)
- `Field(...)` constraints added at model layer so Pydantic rejects invalid data before it even reaches the service

### Where

```
models/student.py       ← Student_model + Student_response_model defined here
routers/students.py     ← request body type changed to Student_model; response_model changed to Student_response_model
services/student_service.py  ← add_student() signature updated to include email
repositories/student_repository.py  ← SQL INSERT updated; all return types use Student_response_model
database/database_helper.py  ← no change (executes whatever SQL is passed)
```

> **DB migration note:** If upgrading from v7, run:
> ```sql
> ALTER TABLE students ADD COLUMN IF NOT EXISTS email VARCHAR(100);
> ```

---

## v7 — Day 013: FastAPI REST API Migration

**When:** Day 013  
**Theme:** CLI → REST API; introduced Repository Pattern, Dependency Injection, and Clean Architecture

### What Changed

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

### Why

The CLI interface was a learning exercise. REST APIs are the real-world standard for backend services. FastAPI was chosen because it provides automatic schema validation (via Pydantic), interactive Swagger docs, async support, and a clean `Depends()` injection system — making it ideal for demonstrating clean architecture concepts.

The Repository Pattern and Dependency Injection were introduced to enforce separation of concerns and make the storage layer swappable without touching business logic.

### How

- **Repository Pattern**: `StudentRepository` (ABC) defines the contract; `PostgresStudentRepository` implements it. `StudentService` only knows about the interface.
- **Dependency Injection**: `get_db_helper() → get_student_repository() → get_student_service()` wired via `Depends()`.
- **Lifespan**: `@asynccontextmanager` manages PostgreSQL connect on startup, disconnect on shutdown.
- **Global Error Handler**: `@app.exception_handler(ValueError)` catches all `ValueError`s and returns a clean `HTTP 400` JSON response.

### Where

```
app.py                          ← NEW: Uvicorn runner (separates server config from app logic)
main.py                         ← rewrote: FastAPI app, lifespan, routers, error handler
dependencies.py                 ← NEW: DI wiring module
routers/students.py             ← NEW: HTTP route definitions
services/student_service.py     ← NEW: business logic layer
repositories/student_repository.py  ← NEW: abstract + PostgreSQL implementation
database/database_helper.py     ← refactored: now managed by lifespan, not called directly
models/student.py               ← NEW: Pydantic Student model
schemas/student_schema.py       ← NEW: input sanitization
```

---

## v3–v6 — CLI Student Manager

**When:** Days 001–012  
**Theme:** Core Python fundamentals — data structures, OOP, file I/O, PostgreSQL basics

These versions were a terminal-based interactive menu application built purely in Python. They do not exist in the current codebase (superseded by v7).

| Version | Key Addition |
|---|---|
| **v3** | Basic list-based student storage; terminal menu loop |
| **v4** | OOP refactor — `Student` class introduced |
| **v5** | File persistence (JSON / pickle) |
| **v6** | PostgreSQL backend via `psycopg`; basic CRUD SQL |
