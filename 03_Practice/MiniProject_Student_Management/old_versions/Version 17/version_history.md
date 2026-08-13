# Version History — Student Management System

Full changelog for every version of this project: **what** changed, **why** it was changed, **how** it was implemented, **where** in the codebase, and **when** (which day of the course).

---

## v17 — Day 024: Dockerization

**When:** Day 024  
**Theme:** Containerization — provide a reproducible, portable way to build and run the FastAPI app using Docker images and containers; document `Dockerfile`, `.dockerignore`, run/build commands, and host-to-container networking notes (host gateway / `host.docker.internal`).

### What Changed

| Area                       |                                        Before (v16) | After (v17)                                                                                                          |
| -------------------------- | --------------------------------------------------: | -------------------------------------------------------------------------------------------------------------------- |
| **Container packaging**    |                         No Docker artifacts in repo | Added `Dockerfile` and `.dockerignore`; documented `docker build` / `docker run` workflow                            |
| **Run instructions**       |                                `python app.py` only | Added containerized run instructions and guidance to pass `.env` via `--env-file`                                    |
| **Host DB connectivity**   | Documentation assumed host DB usage via `localhost` | Documented `DB_HOST=host.docker.internal` for host-to-container connectivity on Windows/macOS and Docker for Desktop |
| **Optional orchestration** |                                      Not documented | Recommended `docker-compose.yml` for app + postgres orchestration (example noted in README)                          |
| **App Version**            |                                             `9.0.0` | `10.0.0`                                                                                                             |

### Why

Packaging the application into a Docker image makes local testing and tutor verification reproducible regardless of the host Python environment. Key benefits:

- Reproducible builds: same image runs anywhere with Docker.
- Isolation: container provides consistent runtime environment (Python version, dependencies).
- Easier onboarding: tutors and CI systems can build/run the same image without installing Python packages locally.

Docker also exposes a common pitfall: when a containerized app needs to reach services running on the host (Postgres), `localhost` inside the container refers to the container itself. Documenting `host.docker.internal` prevents connection errors and speeds troubleshooting.

### How

Key artifacts and commands added to the repo:

- `Dockerfile` (example):

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- `.dockerignore` (example): `.git`, `.venv`, `__pycache__`, `.env`, `.vscode`, etc.

- Build image:

```bash
docker build -t student-management-api .
```

- Run container (pass `.env`):

```bash
docker run --name student-api -p 8000:8000 --env-file .env student-management-api
```

- If your database runs on the host machine, set in `.env`:

```env
DB_HOST=host.docker.internal
```

- Optional: use `docker-compose.yml` to run app + postgres together (recommended for end-to-end local testing).

### Where

```
Dockerfile                ← added at project root
.dockerignore             ← added at project root
README.md                 ← updated: new Docker instructions + `--env-file` guidance
version_history.md        ← updated: this v17 entry
```

---

## v16 — Day 022: Database Indexing

**When:** Day 022  
**Theme:** Query performance — add B-Tree indexes on the most frequently searched columns so that common lookups become O(log N) point traversals instead of O(N) full-table scans

### What Changed

| Area                                    | Before (v15)                                               | After (v16)                                                                                                                         |
| --------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **`email` column constraint**           | `VARCHAR(100)` — no uniqueness enforcement at the DB level | `VARCHAR(100) UNIQUE` — the DB rejects duplicate emails at INSERT time                                                              |
| **`idx_students_email` index**          | Not present                                                | `CREATE UNIQUE INDEX IF NOT EXISTS idx_students_email ON students (email)` — UNIQUE B-Tree; serves `WHERE email = %s` in O(log N)   |
| **`idx_students_name` index**           | Not present                                                | `CREATE INDEX IF NOT EXISTS idx_students_name ON students (name)` — non-unique B-Tree; accelerates prefix `ILIKE 'Alice%'` patterns |
| **`_create_table_if_not_exists()`**     | Created only the table                                     | Creates the table + both indexes in one idempotent method; safe to call on every startup                                            |
| **`get_student_by_email()` (ABC)**      | Not present                                                | Abstract method declared in `StudentRepository`; enforces the contract on every implementation                                      |
| **`get_student_by_email()` (Postgres)** | Not present                                                | Concrete implementation issues `WHERE email = %s`; resolved by `idx_students_email`                                                 |
| **Module docstrings**                   | Day 021 Update was the last entry                          | Day 022 Update added to `database_helper.py` and `student_repository.py`                                                            |
| **App Version**                         | `8.0.0`                                                    | `9.0.0`                                                                                                                             |

### Why

Without indexes, every `SELECT … WHERE email = %s` or `SELECT … WHERE name ILIKE …` query forces PostgreSQL to read **every row in the table** (a sequential scan). This is acceptable for a handful of students, but degrades quickly at scale:

| Table size     | Sequential scan (no index) | B-Tree index scan |
| -------------- | -------------------------- | ----------------- |
| 1,000 rows     | 1,000 row reads            | ~10 node visits   |
| 10,000 rows    | 10,000 row reads           | ~14 node visits   |
| 1,000,000 rows | 1,000,000 row reads        | ~20 node visits   |

Two specific columns benefit most:

1. **`email`** — the natural unique identifier for a student account. Used in authentication flows, duplicate-prevention checks on INSERT, and direct profile lookups. Because the query pattern is always an exact-match (`WHERE email = %s`), a UNIQUE B-Tree index is the ideal data structure. The UNIQUE property also enforces the data-integrity constraint that no two students can share an email address — at the **database level**, not just the application level.

2. **`name`** — the target of `search_students()`, which uses `ILIKE` pattern matching. A B-Tree index accelerates prefix patterns (`ILIKE 'Alice%'`) via an index range scan. Full-wildcard patterns (`ILIKE '%alice%'`) cannot use a B-Tree and still trigger a sequential scan; a future `pg_trgm` + GIN index would eliminate that remaining case.

### How

| Change                            | Where                                                   | Detail                                                                                                 |
| --------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `UNIQUE` constraint on `email`    | `_create_table_if_not_exists()` in `database_helper.py` | Added `UNIQUE` keyword to the `email` column definition in `CREATE TABLE IF NOT EXISTS`                |
| `idx_students_email`              | `_create_table_if_not_exists()` in `database_helper.py` | `CREATE UNIQUE INDEX IF NOT EXISTS idx_students_email ON students (email)` — runs after table creation |
| `idx_students_name`               | `_create_table_if_not_exists()` in `database_helper.py` | `CREATE INDEX IF NOT EXISTS idx_students_name ON students (name)` — runs after table creation          |
| `get_student_by_email()` abstract | `StudentRepository` ABC in `student_repository.py`      | New `@abstractmethod` — all future implementations must provide this method                            |
| `get_student_by_email()` concrete | `PostgresStudentRepository` in `student_repository.py`  | `fetch_one("SELECT * FROM students WHERE email = %s", (email,))` — exercises the UNIQUE index          |

### Key Concept: Why UNIQUE Index Over UNIQUE Constraint?

PostgreSQL implements a `UNIQUE` column constraint **by creating an implicit B-Tree index** internally. Declaring the index explicitly with `CREATE UNIQUE INDEX` makes the index name known and queryable:

```sql
-- Verify the index exists and is in use:
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'students';

-- Confirm the query planner uses it (expect "Index Scan using idx_students_email"):
EXPLAIN ANALYZE SELECT * FROM students WHERE email = 'alice@example.com';
```

Using `IF NOT EXISTS` on both `CREATE TABLE` and `CREATE INDEX` makes `_create_table_if_not_exists()` fully **idempotent** — it can be called on every application startup with no errors and no duplicate index creation.

### Where

```
database/
  database_helper.py     ← _create_table_if_not_exists(): table now has UNIQUE on email;
                            CREATE UNIQUE INDEX IF NOT EXISTS idx_students_email added
                            CREATE INDEX IF NOT EXISTS idx_students_name added
                            Day 022 Update note added to module docstring

repositories/
  student_repository.py  ← StudentRepository (ABC): get_student_by_email() abstract method added
                            PostgresStudentRepository: get_student_by_email() implementation added
                            Day 022 Update note added to module docstring
```

---

## v15 — Day 021: Connection Pooling and Lifespan Control

**When:** Day 021  
**Theme:** Concurrency readiness — replace the single persistent connection with a managed connection pool; every query borrows a connection for exactly one operation and returns it immediately

### What Changed

| Area                    | Before (v14)                                                                                                    | After (v15)                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Connection model**    | `self.connection` — one `psycopg.Connection` per `DatabaseHelper` instance, held for the whole process lifetime | `self._pool` — `psycopg_pool.ConnectionPool`; shared pool of up to `DB_POOL_MAX_SIZE` connections     |
| **Startup**             | `db_helper.connect()` — opens one connection, runs schema check                                                 | `db_helper.open_pool()` — creates `min_size` connections; runs schema check via a borrowed connection |
| **Shutdown**            | `db_helper.close()` — closes the one connection                                                                 | `db_helper.close_pool()` — drains & closes all pool connections                                       |
| **Per-query lifecycle** | Connection held from startup to shutdown; queries share it sequentially                                         | Connection borrowed at start of each `execute_*` / `fetch_*` call; returned immediately after         |
| **Concurrency**         | Only 1 query at a time (single connection = no parallelism)                                                     | Up to `DB_POOL_MAX_SIZE` queries simultaneously                                                       |
| **Config**              | Not configurable                                                                                                | `DB_POOL_MIN_SIZE` / `DB_POOL_MAX_SIZE` in `.env` → `settings.db_pool_min_size / max_size`            |
| **Legacy aliases**      | `connect()` / `close()` were the only lifecycle methods                                                         | `open_pool()` / `close_pool()` are new canonical names; `connect()` / `close()` now delegate to them  |
| **App Version**         | `7.0.0`                                                                                                         | `8.0.0`                                                                                               |

### Why

A single persistent connection is a development convenience, not a production-ready pattern:

1. **No parallelism**: If 10 requests arrive simultaneously, 9 of them queue behind the one connection. Response time degrades linearly with concurrency.
2. **Single point of failure**: If that one connection drops (network blip, PostgreSQL restart), the whole application loses database access until the process is restarted.
3. **Hidden resource leak on errors**: psycopg3 leaves a connection in an aborted-transaction state after any query failure. With a pool, the bad connection is automatically recycled and replaced.

`psycopg_pool.ConnectionPool` addresses all three:

- Keeps `min_size` connections pre-warmed (no cold-start latency for the first N concurrent requests).
- Allows up to `max_size` concurrent DB queries; requests beyond that wait in an internal queue (bounded wait, not indefinite blocking).
- Automatically replaces stale or dead connections; surviving connections keep serving.
- Each query borrows a connection for its lifetime only — the pool reclaims it the moment the query finishes.

### How (Three Exercises)

| Exercise         | What                                | Implementation                                                                                                                                                                        |
| ---------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Day 021 Ex 3** | Replace single connection with pool | `DatabaseHelper`: `self._pool = ConnectionPool(conninfo=..., min_size=..., max_size=..., open=True)`; all `execute_*` / `fetch_*` methods use `with self._pool.connection() as conn:` |
| **Day 021 Ex 4** | FastAPI Lifespan with pool          | `main.py` lifespan: STARTUP calls `db_helper.open_pool()`; SHUTDOWN calls `db_helper.close_pool()`; startup log reports `min` / `max` pool size                                       |
| **Day 021 Ex 5** | Request-flow trace                  | `day_21_practice.md` — full `Client → Router → Service → Repository → Pool → Database` trace with exact connection acquire/release points                                             |

### Key Concept: Borrow-per-Operation Pattern

```python
# Every execute_* method inside DatabaseHelper now looks like this:
def execute_write(self, query, params=None):
    with self._pool.connection() as conn:   # ← CONNECTION ACQUIRED here
        with conn.transaction():            # ← BEGIN
            with conn.cursor() as cur:
                cur.execute(query, params)
                                            # ← COMMIT on clean exit
                                            # ← ROLLBACK on exception
    # ← CONNECTION RETURNED TO POOL here (automatically)
```

The connection is held for **zero time** outside of actual SQL execution. This is what makes the pool effective under concurrent load — connections are never "idle-held" by a request that is doing computation, validation, or JSON serialization.

### Where

```
config.py                ← Added: db_pool_min_size (int=1), db_pool_max_size (int=5)
.env                     ← Added: DB_POOL_MIN_SIZE=1, DB_POOL_MAX_SIZE=5; APP_VERSION→8.0.0
.env.example             ← (should be updated to match .env template)

database/
  database_helper.py     ← REWRITTEN: self.connection → self._pool (ConnectionPool)
                            open_pool() / close_pool() — new lifecycle methods
                            execute_query(), execute_write(), execute_write_transaction(),
                            fetch_all(), fetch_one() — all now use with self._pool.connection()
                            connect() / close() — kept as legacy aliases

main.py                  ← Updated lifespan: open_pool() on startup, close_pool() on shutdown
                            Startup log now includes pool min/max sizes

day_21_practice.md       ← NEW: Exercise 5 answer — full request flow trace with acquire/release points
```

---

## v14 — Day 020: Database Transactions and ACID

**When:** Day 020  
**Theme:** Data integrity — wrap all write operations in explicit ACID transactions so the database is never left in a partial or dirty state

### What Changed

| Area                                    | Before (v13)                                                                                                                              | After (v14)                                                                                                                           |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **`execute_query()` failure path**      | Logs and re-raises; connection left in aborted state                                                                                      | Now calls `connection.rollback()` before re-raising; connection is always clean for next query                                        |
| **`execute_write()` (new)**             | Not present                                                                                                                               | Wraps a single INSERT/UPDATE/DELETE in `connection.transaction()` — automatic COMMIT on success, ROLLBACK on failure                  |
| **`execute_write_transaction()` (new)** | Not present                                                                                                                               | Accepts a callable `steps(cursor)` and runs it inside one `connection.transaction()` — entire multi-step operation is one atomic unit |
| **`add_student` in repository**         | Two separate calls: `fetch_one()` (SELECT max id) then `execute_query()` (INSERT) with `commit=True` — race condition window between them | Single `execute_write_transaction()` call; SELECT and INSERT share one cursor inside one transaction                                  |
| **`delete_student` in repository**      | `execute_query(..., commit=True)` — commit but no rollback on failure                                                                     | `execute_write()` — explicit transaction with automatic rollback on any error                                                         |
| **App Version**                         | `6.0.0`                                                                                                                                   | `7.0.0`                                                                                                                               |

### Why

The previous write pattern had two concrete problems:

1. **Dirty connection state after failure**: psycopg3 operates in autocommit=False mode by default. When a query fails, the connection enters an aborted transaction state. Any subsequent query on the same connection raises `InFailedSqlTransaction` — effectively rendering the connection unusable — until `rollback()` is called explicitly. This was never called.

2. **Race condition in `add_student`**: The ID-generation `SELECT COALESCE(MAX(id),0)+1` and the `INSERT` were two separate round-trips to the database. Under concurrent load (e.g. two simultaneous POST `/students/` requests), both could read the same max ID, then both attempt to INSERT with that same primary key — the second would fail with a unique-constraint violation.

### How

| Change                         | Where                            | Detail                                                                                                     |
| ------------------------------ | -------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Rollback on query failure      | `DatabaseHelper.execute_query()` | Added `try: self.connection.rollback()` in the `except` block before re-raising                            |
| `execute_write()`              | `DatabaseHelper`                 | Uses `with self.connection.transaction():` context manager; single cursor executes the write               |
| `execute_write_transaction()`  | `DatabaseHelper`                 | Uses `with self.connection.transaction():` + `with cursor:` then calls `steps(cur)` and returns its result |
| `add_student` atomic           | `PostgresStudentRepository`      | Defined `_create(cur)` inner function with SELECT + INSERT; passed to `execute_write_transaction()`        |
| `delete_student` transactional | `PostgresStudentRepository`      | Replaced `execute_query(..., commit=True)` with `execute_write(DELETE_SQL, params)`                        |

### Key Concept: psycopg Transaction Context Manager

```python
with self.connection.transaction():   # issues BEGIN
    with self.connection.cursor() as cur:
        cur.execute(...)              # all statements here are in the same transaction
# issues COMMIT if no exception, ROLLBACK if exception raised
```

This is the psycopg3 idiomatic way to manage transactions. The `connection.transaction()` context manager:

- Issues `BEGIN` on `__enter__`
- Issues `COMMIT` on clean `__exit__`
- Issues `ROLLBACK` on `__exit__` with an exception — no explicit cleanup needed

### Where

```
database/
  database_helper.py     ← execute_query: added rollback in except block
                            execute_write: NEW — single write in one transaction
                            execute_write_transaction: NEW — multi-step callable transaction

repositories/
  student_repository.py  ← add_student: SELECT+INSERT now one atomic transaction via execute_write_transaction()
                            delete_student: DELETE now uses execute_write() instead of execute_query(commit=True)
```

---

## v13 — Day 019: Configuration & Environment Variables

**When:** Day 019  
**Theme:** Deployment readiness — eliminate all hardcoded secrets and settings; load everything from `.env` via a typed Pydantic Settings module

### What Changed

| Area                     | Before (v12)                                                         | After (v13)                                                                        |
| ------------------------ | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Config Module**        | Not present                                                          | `config.py` — `Settings(BaseSettings)` class; reads `.env` via `pydantic-settings` |
| **Environment File**     | Not present (empty stub)                                             | `.env` — all settings: app metadata, JWT secret, DB credentials, log level         |
| **Environment Template** | Not present                                                          | `.env.example` — safe, committable template with placeholder values                |
| **JWT Secret**           | Hardcoded `"day015-super-secret-key-..."` in `jwt_utils.py`          | `settings.jwt_secret_key` read from `JWT_SECRET_KEY` in `.env`                     |
| **JWT Algorithm**        | Hardcoded `"HS256"` in `jwt_utils.py`                                | `settings.jwt_algorithm` from `JWT_ALGORITHM` in `.env`                            |
| **JWT Expiry**           | Hardcoded `30` in `jwt_utils.py`                                     | `settings.jwt_access_token_expire_minutes` from `.env`                             |
| **DB Connection**        | `os.getenv("DB_HOST", ...)` etc. scattered in `database_helper.py`   | `settings.db_host / db_name / db_user / db_password / db_port`                     |
| **Log Level (console)**  | Hardcoded `logging.INFO` in `logger_config.py`                       | `settings.log_level_int` from `LOG_LEVEL` in `.env`                                |
| **App Name / Version**   | Hardcoded strings `"Student Management..."` / `"5.0.0"` in `main.py` | `settings.app_name` / `settings.app_version` from `.env`                           |
| **Startup Log**          | Simple `"routers and middleware registered"` message                 | Config profile logged: name, version, debug flag, log level                        |
| **App Version**          | `5.0.0`                                                              | `6.0.0`                                                                            |

### Why

Hardcoded secrets and settings are the single biggest security risk in application development:

- A hardcoded `SECRET_KEY` in source code is exposed to anyone who can read the repository.
- Changing a DB password or JWT secret requires modifying source code and redeploying.
- There is no way to have different settings for dev, staging, and production without code changes.

A `.env` + config module pattern solves all three:

- **Secrets stay out of code**: `.env` is added to `.gitignore`; `.env.example` is the safe template.
- **Config changes without code changes**: swap a DB URL or secret key by editing `.env` only.
- **Type safety**: Pydantic validates every setting at startup; bad values cause a clear error immediately.

### How (Six Exercises)

| Exercise         | What                                      | Implementation                                                                                                                                                                        |
| ---------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Day 019 Ex 1** | Create `.env` file                        | `.env` — stores `APP_NAME`, `APP_VERSION`, `DEBUG`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `DB_*`, `LOG_LEVEL`                                         |
| **Day 019 Ex 2** | Create `config.py` with Pydantic Settings | `Settings(BaseSettings)` class with typed fields; `model_config` sets `env_file=".env"`; `log_level_int` property converts string to `logging` int; `settings = Settings()` singleton |
| **Day 019 Ex 3** | Read config in `main.py`                  | `FastAPI(title=settings.app_name, version=settings.app_version)`; startup log prints active config profile                                                                            |
| **Day 019 Ex 4** | Move JWT secret to config                 | `jwt_utils.py`: removed hardcoded `SECRET_KEY`; now reads `settings.jwt_secret_key`, `settings.jwt_algorithm`, `settings.jwt_access_token_expire_minutes`                             |
| **Day 019 Ex 5** | Move DB URL to config                     | `database_helper.py`: removed all `os.getenv()` calls; now reads `settings.db_host / db_name / db_user / db_password / db_port`                                                       |
| **Day 019 Ex 6** | Configure logging level                   | `logger_config.py`: `StreamHandler.setLevel(settings.log_level_int)` — set `LOG_LEVEL=DEBUG` in `.env` to expose debug traces on console                                              |

### Key Concept: Settings Priority

Pydantic Settings reads values in this priority order (highest → lowest):

```text
1. Process environment variables (os.environ)   ← set by CI/CD, Docker, systemd
2. .env file in the working directory            ← local development
3. Default values declared in Settings class     ← last-resort fallback
```

This means you can override `.env` values in production by setting real environment variables without changing the file.

### Where

```
config.py            ← NEW: Settings(BaseSettings) class + settings singleton
.env                 ← NEW: real configuration values (add to .gitignore)
.env.example         ← NEW: safe template (commit this to version control)

auth/jwt_utils.py    ← Updated: hardcoded SECRET_KEY replaced by settings.jwt_secret_key
database/
  database_helper.py ← Updated: os.getenv() calls replaced by settings.db_* attributes
logger_config.py     ← Updated: stream_handler.setLevel(settings.log_level_int)
main.py              ← Updated: FastAPI title/version from settings; config startup log
```

---

## v12 — Day 018: Global Exception Handling

**When:** Day 018  
**Theme:** Reliability — replace ad-hoc HTTPException raises and None-checks with a clean custom-exception + global-handler pattern

### What Changed

| Area | Before (v11) | After (v12) |
|---|---|---|\n| **Custom Exception** | Not present | `exceptions/student_exceptions.py` — `StudentNotFoundException(student_id)` |
| **Exceptions Package** | Not present | `exceptions/__init__.py` — re-exports `StudentNotFoundException` for clean imports |
| **Service: get_student_by_id** | Returns `None` when student not found | Raises `StudentNotFoundException` — no more nullable return type |
| **Service: delete_student** | Returns `bool` (False when not found) | Raises `StudentNotFoundException` — no more boolean flag |
| **Router: get / delete** | Manual `if student is None` / `if not deleted` → raises `HTTPException` | Removed — exception propagates automatically to global handler |
| **Global Handler: 404** | Not present | `@app.exception_handler(StudentNotFoundException)` → `{error, message, student_id}` JSON |
| **Global Handler: 500** | Not present | `@app.exception_handler(Exception)` catch-all → `{error, message, exception_type}` JSON |
| **Exception Logging** | Not applicable | All handlers log via centralized logger (`WARNING` for 404, `EXCEPTION` for 500) |
| **App Version** | `4.0.0` | `5.0.0` |

### Why

Without a consistent exception strategy:

- Routers accumulate boilerplate `if result is None: raise HTTPException(...)` in every handler.
- The client receives either a vague `500 Internal Server Error` HTML page or inconsistent JSON shapes across endpoints.
- Service layer was returning nullable types (`None` / `bool`) that pushed error-handling responsibility to the wrong layer.

A custom exception + global handler separates concerns properly:

- The **service layer** detects the error and raises the right domain exception.
- The **global handler** in `main.py` decides the HTTP status code and JSON response shape — once, for the whole app.
- The **router** stays completely clean — it just calls the service and returns the result.

### How (Five Exercises)

| Exercise         | What                                          | Implementation                                                                                                                                                                 |
| ---------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Day 018 Ex 1** | Raise `HTTPException` for a missing student   | Moved to service layer: `get_student_by_id` and `delete_student` raise `StudentNotFoundException` instead of returning `None`/`False`; router no longer raises `HTTPException` |
| **Day 018 Ex 2** | Create `StudentNotFoundException`             | `exceptions/student_exceptions.py` — subclasses `Exception`, stores `student_id` as an attribute, sets a human-readable message via `super().__init__()`                       |
| **Day 018 Ex 3** | Global handler for `StudentNotFoundException` | `@app.exception_handler(StudentNotFoundException)` in `main.py` — returns `HTTP 404` with `{error, message, student_id}`                                                       |
| **Day 018 Ex 4** | Log the exception                             | All handlers call `logger.warning()` (client errors) or `logger.exception()` (server errors) via the existing `logger_config` infrastructure; no `print()` used                |
| **Day 018 Ex 5** | Trigger scenarios via Swagger                 | GET/DELETE with a non-existent ID → 404 JSON; POST with empty name → 400 JSON; terminal shows WARNING; `logs/application.log` shows full structured entry                      |

### Key Concept: Exception Handler Precedence

FastAPI evaluates exception handlers from **most-specific to least-specific**:

```text
@app.exception_handler(StudentNotFoundException)  ← checked first for StudentNotFoundException
@app.exception_handler(ValueError)               ← checked first for ValueError
@app.exception_handler(Exception)                ← catch-all fallback (last resort)
```

This means the catch-all `Exception` handler never silently swallows errors that already have a dedicated handler — each exception type gets the right response shape.

### Where

```
exceptions/
├── __init__.py              ← NEW: re-exports StudentNotFoundException
└── student_exceptions.py   ← NEW: StudentNotFoundException(student_id) class

main.py                      ← Added: student_not_found_exception_handler, unhandled_exception_handler
                                Updated: app version 4.0.0 → 5.0.0; comment labels updated to Day 017 Exn
services/student_service.py  ← Updated: get_student_by_id raises StudentNotFoundException (not return None)
                                         delete_student raises StudentNotFoundException (not return False)
routers/students.py          ← Updated: removed manual None/bool checks; HTTPException import removed
```

---

## v11 — Day 017: Python Logging Practice

**When:** Day 017  
**Theme:** Observability — structured logging with FileHandler, StreamHandler, and Formatter across all application layers

### What Changed

| Area                  | Before (v10)                                                   | After (v11)                                                                                                                    |
| --------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Logging**           | `print()` statements scattered across `main.py`, `middleware/` | Centralized `logging` module with `Logger`, `FileHandler`, `StreamHandler`, `Formatter`                                        |
| **Log Config**        | Not present                                                    | `logger_config.py` — single module wires the entire logging pipeline                                                           |
| **Log File**          | Not present                                                    | `logs/application.log` — all `DEBUG`+ records written here persistently                                                        |
| **Console Output**    | Raw `print()` text                                             | Structured `INFO`+ records with timestamp, level, module, and message                                                          |
| **Exception Logging** | No stack traces captured                                       | `logger.exception()` inside every `try/except` captures full Python stack traces                                               |
| **Log Levels**        | None (print = always visible)                                  | `DEBUG` (file-only trace), `INFO` (operations), `WARNING` (missing resources, auth fails), `ERROR`/`EXCEPTION` (server errors) |
| **Middleware**        | `print()` in every middleware class                            | `logger.info()` for requests; `logger.debug()` for timing & LIFO demo; `logger.warning/error()` for 4xx/5xx                    |
| **Repository**        | No observability                                               | `logger.info()` on CRUD success; `logger.warning()` for not-found; `logger.exception()` on DB failure                          |
| **Service**           | No observability                                               | `logger.info()` for method entry/exit; `logger.warning()` for validation failures and not-found                                |
| **Router**            | No observability                                               | `logger.info()` for route entry/result; `logger.warning()` before 404 raises                                                   |
| **Auth Router**       | No observability                                               | `logger.info()` for login success; `logger.warning()` for wrong credentials; `logger.debug()` for token ops                    |
| **JWT Bearer**        | No observability                                               | `logger.warning()` on validation failure; `logger.debug()` on success                                                          |
| **DB Helper**         | No observability                                               | `logger.info()` for connect/close; `logger.debug()` for query traces; `logger.exception()` on failure                          |
| **App Version**       | `3.0.0`                                                        | `4.0.0`                                                                                                                        |

### Why

Application logs are the primary tool for diagnosing production issues. Without structured logging:

- There is no persistent record of what happened when an error occurs.
- `print()` has no severity level — you can't distinguish a debug trace from a critical failure.
- Stack traces disappear after the terminal session ends.

Python's `logging` module solves all three problems: it supports severity levels, persistent file output, consistent formatting, and automatic stack trace capture via `logger.exception()`.

### How (Five Exercises)

| Exercise | What                                 | Implementation                                                                                                                           |
| -------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Ex 1** | Configure logging                    | `logging.Logger` + manual `FileHandler` + `StreamHandler` + `Formatter` in `logger_config.py` (replaces `basicConfig` for finer control) |
| **Ex 2** | Write logs to `logs/application.log` | `FileHandler(LOG_FILE, mode="a")` at `DEBUG` level — captures everything including trace details invisible on console                    |
| **Ex 3** | Replace `print()` with logger calls  | Every module: `logger.info()` for normal ops, `logger.warning()` for user/auth errors, `logger.error()` for server errors                |
| **Ex 4** | Log exceptions                       | `logger.exception("...")` inside every `try/except` — automatically appends the full traceback to the log file                           |
| **Ex 5** | Review output                        | Console shows `INFO`+ only; `logs/application.log` shows everything including `DEBUG` traces and stack traces                            |

### Key Concept: Logger Hierarchy

All loggers use the naming convention `student_management.<module>`:

```text
student_management                   ← root app logger (configured in logger_config.py)
├── student_management.main
├── student_management.middleware.request_middleware
├── student_management.routers.students
├── student_management.routers.auth
├── student_management.services.student_service
├── student_management.repositories.student_repository
├── student_management.database.database_helper
└── student_management.auth.jwt_bearer
```

Child loggers inherit both handlers from the parent. Calling `get_logger(__name__)` in each module automatically produces the correct name.

### Log Level Strategy

| Level       | When Used                                                        | Visible        |
| ----------- | ---------------------------------------------------------------- | -------------- |
| `DEBUG`     | Query traces, LIFO demo steps, token validation success          | File only      |
| `INFO`      | Startup, shutdown, CRUD success, request/response summary        | Console + File |
| `WARNING`   | Record not found, auth failures, validation errors (user errors) | Console + File |
| `ERROR`     | 5xx response status codes                                        | Console + File |
| `EXCEPTION` | Any `except` block — wraps ERROR with full stack trace           | Console + File |

### Where

```
logger_config.py                ← NEW: root logger, FileHandler, StreamHandler, Formatter, get_logger()
logs/
└── application.log             ← AUTO-CREATED: persistent log output (DEBUG+)

main.py                         ← lifespan startup/shutdown now uses logger; exception on DB fail
middleware/request_middleware.py ← all print() replaced; level varies by HTTP status
database/database_helper.py     ← connect/close/execute all logged; try/except with logger.exception()
repositories/student_repository.py ← full CRUD observability; logger.exception() on every failure
services/student_service.py     ← method entry/exit logged; warning on validation errors
routers/students.py             ← route entry/result logged; warning before 404
routers/auth.py                 ← login attempts/failures logged; profile access logged
auth/jwt_bearer.py              ← JWT validation success/failure logged
```

---

## v10 — Day 016: Middleware Practice

**When:** Day 016  
**Theme:** HTTP Middleware layer — request pipeline observability and cross-cutting concerns

### What Changed

| Area                | Before (v9) | After (v10)                                                                            |
| ------------------- | ----------- | -------------------------------------------------------------------------------------- |
| **Middleware**      | None        | Five middleware registered via `add_middleware()` in `main.py`                         |
| **Request Logging** | Not present | `LogIncomingRequestMiddleware` — prints `METHOD /path` on every request                |
| **Execution Time**  | Not present | `ExecutionTimeMiddleware` — prints duration & adds `X-Process-Time-Ms` response header |
| **Console Logging** | Not present | `ConsoleRequestLogMiddleware` — prints `METHOD /path -> STATUS` after each request     |
| **CORS**            | Not enabled | `CORSMiddleware` — allows origin `http://localhost:5173`, all methods & headers        |
| **Order Demo**      | Not present | `MiddlewareOrderDemoA` & `MiddlewareOrderDemoB` — illustrates LIFO middleware pipeline |
| **New Module**      | Not present | `middleware/` package: `__init__.py` + `request_middleware.py`                         |
| **App Version**     | `2.0.0`     | `3.0.0`                                                                                |

### Why

Middleware is how real-world APIs handle **cross-cutting concerns** — things that apply to every request without polluting individual route handlers. Logging, timing, CORS, and auth checks all belong in the middleware pipeline, not inside route functions.

### How (Five Exercises)

| Exercise | Class                                           | Mechanism                                                                           |
| -------- | ----------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Ex 1** | `LogIncomingRequestMiddleware`                  | `BaseHTTPMiddleware` subclass; prints before `call_next()`                          |
| **Ex 2** | `ExecutionTimeMiddleware`                       | Records `time.time()` before/after `call_next()`; writes `X-Process-Time-Ms` header |
| **Ex 3** | `ConsoleRequestLogMiddleware`                   | Calls `call_next()`, then prints `response.status_code`                             |
| **Ex 4** | `CORSMiddleware`                                | FastAPI built-in; configured with `allow_origins=["http://localhost:5173"]`         |
| **Ex 5** | `MiddlewareOrderDemoA` + `MiddlewareOrderDemoB` | Both print on request entry and response exit to show LIFO order                    |

### Key Concept: LIFO Middleware Stack

FastAPI middleware is a **Last In, First Out** stack. The _last_ `add_middleware()` call runs _first_ on the incoming request, then response unwinding happens in reverse.

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

| Area                   | Before (v8)               | After (v9)                                                                          |
| ---------------------- | ------------------------- | ----------------------------------------------------------------------------------- |
| **Authentication**     | None — all endpoints open | JWT Bearer authentication added                                                     |
| **Password Hashing**   | Not present               | `passlib` + `bcrypt` via `hash_password()` / `verify_password()`                    |
| **Token Generation**   | Not present               | `python-jose` HS256 signed JWTs with `sub`, `role`, `exp`, `iat` claims             |
| **Token Decoding**     | Not present               | `decode_token()` verifies signature + expiry; `inspect_token_parts()` for education |
| **Protected Endpoint** | Not present               | `GET /auth/profile` — requires valid `Authorization: Bearer <token>` header         |
| **Auth Dependency**    | Not present               | `get_current_user` FastAPI dependency; `OAuth2PasswordBearer` wires Swagger padlock |
| **Login Endpoint**     | Not present               | `POST /auth/login` — accepts `OAuth2PasswordRequestForm`; returns `TokenResponse`   |
| **Demo Endpoints**     | Not present               | `GET /auth/demo/hash`, `GET /auth/demo/token`, `POST /auth/inspect-token`           |
| **New Module**         | Not present               | `auth/` package: `password_utils.py`, `jwt_utils.py`, `jwt_bearer.py`               |
| **New Router**         | Not present               | `routers/auth.py` registered as `auth_router` in `main.py`                          |
| **App Version**        | `1.0.0`                   | `2.0.0`                                                                             |

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

| Exercise   | Endpoint                   | What it demonstrates                                      |
| ---------- | -------------------------- | --------------------------------------------------------- |
| **Ex 1**   | `GET /auth/demo/hash`      | bcrypt hashing + salt proof + `verify_password()`         |
| **Ex 1+2** | `POST /auth/login`         | Credential check + JWT issuance                           |
| **Ex 2+3** | `GET /auth/demo/token`     | JWT generation + structural inspection                    |
| **Ex 3**   | `POST /auth/inspect-token` | Decode any JWT Header/Payload/Signature (no verification) |
| **Ex 4+5** | `GET /auth/profile`        | Protected endpoint + Swagger Bearer auth testing          |

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

| Area                      | Before (v7)                                                  | After (v8)                                                                           |
| ------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| **Student Fields**        | `id`, `name`, `age`, `city`                                  | `id`, `name`, `age`, `city`, **`email`**                                             |
| **Pydantic Model**        | Single `Student` class (request + response combined)         | Split into `Student_model` (request) and `Student_response_model` (response)         |
| **Request `id` field**    | `id: int \| None = None` (optional, could be sent by client) | Removed from `Student_model` — client never sends an `id`                            |
| **Response `id` field**   | `id: int \| None` (could be `None`)                          | `id: int` (required; guaranteed by DB before response is sent)                       |
| **Field Validation**      | No constraints on `name`, `age`, `city`                      | `Field(min_length=1, max_length=100)` on `name`, `city`; `Field(ge=0)` on `age`      |
| **Email Validation**      | Not present                                                  | `email: EmailStr` with Pydantic `EmailStr` type (requires `pydantic[email]`)         |
| **Database Table**        | `id`, `name`, `age`, `city` columns                          | Added `email VARCHAR(100)` column                                                    |
| **SQL Queries**           | `INSERT ... VALUES (%s, %s, %s, %s)`                         | `INSERT ... VALUES (%s, %s, %s, %s, %s)` (includes `email`)                          |
| **Repository signatures** | Used `Student` for both input and output                     | `add_student` accepts `Student_model`; all return types use `Student_response_model` |
| **Service signatures**    | `add_student(name, age, city)`                               | `add_student(name, age, city, email)`                                                |
| **Router signatures**     | Used `Student` for request/response models                   | Uses `Student_model` for request body, `Student_response_model` for response         |

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
>
> ```sql
> ALTER TABLE students ADD COLUMN IF NOT EXISTS email VARCHAR(100);
> ```

---

## v7 — Day 013: FastAPI REST API Migration

**When:** Day 013  
**Theme:** CLI → REST API; introduced Repository Pattern, Dependency Injection, and Clean Architecture

### What Changed

| Area                  | Before (v6)                 | After (v7)                                          |
| --------------------- | --------------------------- | --------------------------------------------------- |
| **Interface**         | CLI (terminal menu)         | REST API (HTTP endpoints via FastAPI)               |
| **Entry Point**       | `main.py` (CLI loop)        | `main.py` (FastAPI app) + `app.py` (Uvicorn runner) |
| **Student Model**     | `id`, `name`                | `id`, `name`, `age`, `city`                         |
| **Database Table**    | `id`, `name` only           | `id`, `name`, `age`, `city`                         |
| **Dependency Wiring** | Manual instantiation        | FastAPI `Depends()` injection chain                 |
| **Error Handling**    | `print()` / bare exceptions | Global `ValueError` → HTTP 400 handler              |
| **App Lifecycle**     | No lifecycle management     | `@asynccontextmanager` lifespan (startup/shutdown)  |
| **Search**            | Basic string scan           | Case-insensitive PostgreSQL `ILIKE` query           |
| **API Docs**          | None                        | Auto-generated Swagger UI at `/docs`                |

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

| Version | Key Addition                                         |
| ------- | ---------------------------------------------------- |
| **v3**  | Basic list-based student storage; terminal menu loop |
| **v4**  | OOP refactor — `Student` class introduced            |
| **v5**  | File persistence (JSON / pickle)                     |
| **v6**  | PostgreSQL backend via `psycopg`; basic CRUD SQL     |
