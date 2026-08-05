# Day 021 Practice — Exercise 5: Request Flow Trace

## The Question

> Trace the request flow from Client → Database. Understand exactly where
> the connection is acquired and released.

---

## Full Request Flow: `POST /students/` (Create Student)

```
Client
  ↓  HTTP POST /students/  {name, age, city, email}
  ↓
[Middleware stack — LIFO, outermost first on request]
  ↓  LogIncomingRequestMiddleware  → logs "Incoming Request: POST /students/"
  ↓  ExecutionTimeMiddleware       → records start timestamp
  ↓  ConsoleRequestLogMiddleware   → (runs on response, not yet)
  ↓
Router  (routers/students.py)
  ↓  @router.post("/students/")
  ↓  FastAPI calls:  get_student_service() via Depends()
  ↓
[Dependency chain — dependencies.py]
  ↓  get_db_helper()           → returns the module-level _db_helper singleton
  ↓  get_student_repository()  → returns PostgresStudentRepository(_db_helper)
  ↓  get_student_service()     → returns StudentService(repository)
  ↓
Service  (services/student_service.py)
  ↓  validate_student_name()   → raises ValueError if empty/invalid
  ↓  repository.add_student()
  ↓
Repository  (repositories/student_repository.py)
  ↓  db_helper.execute_write_transaction(_create)
  ↓
DatabaseHelper  (database/database_helper.py)
  ↓  with self._pool.connection() as conn:    ← CONNECTION ACQUIRED HERE
  ↓      with conn.transaction():             ← BEGIN
  ↓          with conn.cursor() as cur:
  ↓              cur.execute(SELECT COALESCE(MAX(id),...))  ← Step 1
  ↓              cur.execute(INSERT INTO students ...)      ← Step 2
  ↓          (cursor closed)
  ↓      (COMMIT issued by conn.transaction() context exit)
  ↓  (connection context exits)              ← CONNECTION RETURNED TO POOL HERE
  ↓
Pool  (psycopg_pool.ConnectionPool)
  ↓  Connection checked back in; available for next request
  ↓
PostgreSQL  (database server)
  ↓  Data written to disk / WAL; changes are durable (ACID Durability guarantee)

← ← ← ← ← ← ← ← ← ← ← ← ← response travels back up the stack ← ← ← ← ← ←

Repository  → returns Student_response_model(id=N, ...)
Service     → returns the model unchanged (no further business logic on create)
Router      → wraps in HTTP 201 Created JSON response
Middleware  → ExecutionTimeMiddleware records elapsed ms, adds X-Process-Time-Ms header
Middleware  → ConsoleRequestLogMiddleware logs "POST /students/ → 201"
Client      ← receives HTTP 201 + JSON body
```

---

## Where the Connection Is Acquired and Released

| Event | Location | Code |
|---|---|---|
| **Pool opened** | `DatabaseHelper.open_pool()` called by FastAPI lifespan STARTUP | `self._pool = ConnectionPool(..., open=True)` |
| **Connection acquired** | Inside each `execute_*` / `fetch_*` call in `DatabaseHelper` | `with self._pool.connection() as conn:` |
| **Transaction started** | Inside `execute_write` / `execute_write_transaction` | `with conn.transaction():  # BEGIN` |
| **COMMIT** | On clean exit of the `conn.transaction()` context | Automatic — no explicit `conn.commit()` needed |
| **ROLLBACK** | On exception exit of the `conn.transaction()` context | Automatic — psycopg_pool rolls back and recycles |
| **Connection released** | When the `with self._pool.connection()` block exits | Automatic — connection returned to pool |
| **Pool closed** | `DatabaseHelper.close_pool()` called by FastAPI lifespan SHUTDOWN | `self._pool.close()` |

> **Key insight:** The connection is held for the absolute minimum time — only while
> the SQL is executing. The moment `with self._pool.connection()` exits (whether by
> success or exception), psycopg_pool reclaims the connection and it becomes available
> for the next waiting request. This is what makes pools efficient under concurrent load.

---

## Single-Connection vs Pool — Comparison

| Aspect | Before (Day 020) | After (Day 021) |
|---|---|---|
| **Connection object** | `self.connection` — one per `DatabaseHelper` instance | `self._pool` — shared pool, `max_size` concurrent connections |
| **Concurrency** | Only one query at a time; second request waits for first to finish | Up to `max_size` queries run simultaneously |
| **Acquisition point** | `connect()` at app startup; held for the entire process lifetime | `with self._pool.connection()` at the start of each query |
| **Release point** | `close()` at app shutdown | End of each `with self._pool.connection()` block |
| **On connection failure** | Entire app loses DB access; restart required | Pool replaces bad connections automatically; other connections continue |
| **On query exception** | Manual `rollback()` required (added in Day 020) | Pool automatically rolls back and recycles the connection |

---

## Why the Pool Lives in `DatabaseHelper` and Not the Router

The pool is an **infrastructure concern** — it is about _how_ we talk to the database,
not _what_ we ask it. Keeping it inside `DatabaseHelper` means:

- The **Router** only knows about the `StudentService` interface.
- The **Service** only knows about the `StudentRepository` interface.
- The **Repository** only knows about `DatabaseHelper`'s query methods.
- Only `DatabaseHelper` knows about `psycopg_pool` — this is the correct layer.

If we ever switched to a different pool library (or a different database driver entirely),
only `DatabaseHelper` would change. Nothing above it in the stack would need to know.
