# Project ₹50L — Month 01 Revision

### Backend Engineering Foundation (Day 001 – Day 030)

> **Purpose of this file:** A single, consolidated brain-dump of everything learned in the first 30 days of Project ₹50L, built from `00_Master` (Goal/Roadmap/Rules/Daily Log) and `01_Engineering_Handbook` (30 daily technical logs). Use this to revise fast before interviews, before starting Month 2, or whenever the details get fuzzy.
>
> **How to use it:** Section 1 gives you the big picture (why this month happened, what it built toward). Sections 2–8 are the technical core, grouped by theme rather than strictly by day, because interviews test _themes_ (auth, DB design, Docker) not "what did you do on day 14." Section 9 is the master interview question bank. Section 10 is the master cheat sheet. Section 11 is the FastAPI ↔ ASP.NET Core mapping (your fastest bridge from known-C#/.NET to the new stack). Section 12 is the "always remember" list — the things that are cheap to forget and expensive to fumble in an interview.

---

## 1. Big Picture — Where Month 1 Fits in Project ₹50L

**The master goal:** ₹13 LPA → ₹25–30 LPA (Jump 1, hard deadline **2 Jan 2027**) → ₹45–50+ LPA (Jump 2, hard deadline **2 Jan 2028**). Positioning: not a pure RPA developer, not a pure GenAI hobbyist — an **"Automation + AI-augmented Full-Stack Engineering Lead."** Month 1 is the unglamorous but load-bearing part of that pitch: it is what makes "I can build and ship production-grade backend systems" true and demonstrable, before any LLM/RAG/agent work gets layered on top in Month 2+.

**What the 12-week roadmap says Month 1 should deliver:** Python mastery, FastAPI, PostgreSQL, Docker, Authentication, Testing, CI/CD basics, and a working, containerized backend (the **Student Management System**) that evolves week over week — this is the flagship artifact of the month, and its evolution across 30 days _is_ the story you tell in interviews.

**The architecture evolution, in one line per stage** (this single narrative is one of your strongest interview assets — it shows deliberate architectural growth, not just "I followed a tutorial"):

```
Day 01–04   Plain Python scripts / CLI, OOP refactor
Day 05      Git workflow + raw SQL fundamentals introduced
Day 06      Proper relational schema (PK/FK, normalization) designed
Day 07      Python ↔ PostgreSQL wired up via psycopg
Day 08      CRUD + parameterized queries + first DatabaseHelper (anti SQL-injection)
Day 09      Repository Pattern + Service Layer + Clean/Layered Architecture introduced
Day 10      CLI replaced by FastAPI — REST API layer added on top, layers below unchanged
Day 11      Request/Response models, Path/Query params formalized
Day 12      Dependency Injection (Depends()) + APIRouter — modular routers
Day 13      Proper HTTP status codes + HTTPException discipline
Day 14      Pydantic Field() validation, Request vs Response model separation hardened
Day 15      JWT auth + bcrypt password hashing — the app becomes multi-user-safe
Day 16      Middleware, request lifecycle, CORS
Day 17      Structured logging replaces print()
Day 18      Global exception handling + custom domain exceptions
Day 19      Centralized config via Pydantic Settings + .env (12-factor)
Day 20      Transactions + ACID — data integrity guaranteed
Day 21      Connection pooling + FastAPI lifespan — expensive resources managed properly
Day 22      Indexing + EXPLAIN/EXPLAIN ANALYZE — query performance becomes measurable
Day 23      Docker fundamentals (images, containers, engine, CLI)
Day 24      FastAPI itself containerized
Day 25      Docker Compose — multi-container app (API + DB) with networking
Day 26      Health checks — "running" vs "ready" as separate concepts
Day 27      Environment management (env vs env_file), restart policies, dev vs prod config
Day 28      Docker internal networking deep-dive (bridge networks, service DNS, `db:5432`)
Day 29      Full reproducible local deployment — multi-stage builds, non-root containers
Day 30      Advanced SQL — JOINs, GROUP BY, HAVING, query design at the Repository layer
```

**The one sentence that ties it together:** _"I didn't just learn FastAPI and Docker as isolated topics — I evolved one real system, the Student Management backend, from a single Python script into a JWT-authenticated, logged, exception-handled, connection-pooled, health-checked, multi-container, reproducibly-deployable REST API with proper relational schema design and advanced SQL — using Clean Architecture throughout."_ That sentence, backed by the ability to explain any layer of it, is Month 1's real deliverable — more valuable than any single fact below.

---

## 2. Python Foundations (Days 1–4)

### 2.1 Core language concepts

- **Dynamic typing**: no explicit type declarations; a name is just a reference to an object.
- **Strings**: immutable sequences of Unicode. Immutability → better performance, safe hashing, thread safety. Slicing: `s[start:stop:step]`, `s[::-1]` reverses.
- **Lists**: ordered, mutable, allow duplicates. `append/extend/insert/remove/pop/sort/reverse/clear/copy`. List comprehensions: `[x*x for x in range(10)]`.
- **Tuples**: ordered, **immutable**, allow duplicates — use when data must never change (e.g. coordinates, fixed records).
- **Sets**: unordered, mutable, unique values only. `add/remove/union/intersection/difference`.
- **Dictionaries**: key–value pairs. Prefer `.get("key")` over `["key"]` when a key may not exist (avoids `KeyError`).
- **Mutable vs Immutable** — Mutable: List, Dict, Set. Immutable: String, Tuple, int, float.
- **Time complexity cheat sheet**: list append `O(1)`, list search `O(n)`, dict lookup `O(1)` avg, set lookup `O(1)` avg — because dict/set are hash tables (hash function → array index → constant-time access via pointer arithmetic; no scanning).
- **Control flow**: `if`, `for`, `while` — standard, nothing exotic introduced yet at this stage.

### 2.2 Functions & Modules (Day 2)

- **Function** = named, reusable block of logic. **Parameter** = variable in the definition; **Argument** = actual value passed at call time.
- Prefer `return` over `print()` inside functions — `print()` just displays; `return` lets the caller actually use the result.
- **Default parameters** (`def greet(name="Guest")`) and **keyword arguments** (`greet(name="Mayank")`) improve readability and flexibility.
- **Local vs Global variables**: local exists only inside the function; overusing globals creates hidden coupling and hard-to-trace bugs.
- **Modules** = a `.py` file of reusable code. Import explicitly (`from module import function`) for clarity over `import *`.
- **`if __name__ == "__main__":`** — ensures code runs only when the file is executed directly, not when imported elsewhere. This is the standard Python program entry-point idiom (loosely analogous to `Main()` in C#/.NET, but import-triggered rather than compiler-triggered).

### 2.3 Exception Handling & File Handling (Day 3)

- **Exception** = a runtime error that interrupts normal execution.
- `try` (risky code) → `except` (handle specific errors — never a bare `except:`, since that swallows _everything_ including bugs you actually want to see) → `else` (runs only if no exception occurred) → `finally` (always runs — ideal for cleanup, e.g. closing files/connections).
- **File modes**: `"r"` read, `"w"` overwrite (destroys existing content!), `"a"` append.
- **`with open(...) as f:`** is the professional pattern — guarantees the file is closed automatically (context manager), even if an exception occurs mid-block. Never rely on manually calling `.close()`.

### 2.4 OOP — Classes & Objects (Day 4)

- **Class** = blueprint. **Object** = an instance created from that blueprint.
- **Constructor `__init__`**: special method auto-called on object creation, used to initialize instance state.
- **`self`**: refers to the current object instance; required so methods can read/write that specific object's data (each object has its own copy of instance variables).
- **Instance variables** vs **local variables**: instance variables (`self.x`) persist on the object and are accessible from any method; local variables die when the method returns.
- **Methods** = functions defined inside a class that operate on/modify object state.
- Multiple objects of the same class each hold independent state.
- OOP improves scalability, maintainability, and organization vs. one giant procedural script — this is exactly the shift from Day 1–3's script style to Day 4's `Student` class-based refactor.

### Common mistakes to never repeat (Days 1–4)

- `my_list = list()` instead of the idiomatic `my_list = []`.
- Using `employee["salary"]` instead of `.get("salary")` when the key might not exist.
- Forgetting `self`, or accessing instance data as `name` instead of `self.name`.
- Writing one 100+ line function or one giant "does everything" class instead of decomposing responsibility.
- Bare `except:` blocks; forgetting to close files (solved by always using `with open()`).

---

## 3. Git & SQL / Database Design Fundamentals (Days 5–9)

### 3.1 Git (Day 5)

- **Git** = distributed version control tool (local). **GitHub** = cloud platform that _hosts_ Git repositories. They are not the same thing — a very common interview trip-up.
- **Workflow**: Working Directory → Staging Area (`git add`) → Local Repository (`git commit`) → Remote Repository (`git push`).
- Ten commands to know cold: `git status`, `git add .` / `git add <file>`, `git commit -m "..."`, `git log`, `git diff`, `git checkout -- <file>` (restore), `git branch`, `git push`, `git pull`.

### 3.2 SQL & Relational Database Fundamentals (Days 5–6)

- **SQL** = language to create/manage/retrieve/update/delete data in relational DBs. **Database** = collection of related tables. **Table** = rows (records) × columns (fields).
- **Primary Key (PK)**: uniquely identifies a row; no duplicates, no `NULL`.
- **Foreign Key (FK)**: a column referencing another table's PK — this is _how relationships are implemented_ in SQL.
- **Relationship types**:
  - **1:1** — one record relates to exactly one record elsewhere.
  - **1:N** — one record relates to many (e.g. one customer → many orders).
  - **N:N** — needs a **junction table** (relational DBs cannot store many-to-many directly); e.g. `students` ↔ `courses` via an `enrollments` junction table holding both FKs.
- **Normalization**: reduces redundancy/duplication and improves consistency. **1NF**: each column holds atomic (non-repeating, non-multi-valued) values.
- **CRUD in SQL**: `INSERT` (Create), `SELECT` (Read), `UPDATE`, `DELETE`. Plus `WHERE` (filter), `ORDER BY` (sort), aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`).
- **`DELETE` vs `DROP`**: `DELETE` removes rows, keeps the table structure; `DROP` removes the entire table (structure + data).
- Why databases over flat text files: concurrency, integrity constraints, query performance, scalability, transactional safety.

### 3.3 PostgreSQL & Python Integration (Day 7)

- **PostgreSQL** = the actual DBMS software that executes SQL and manages storage; **SQL** = just the language. `pgAdmin` = GUI client for administering Postgres.
- **`psycopg`** = the Python driver/bridge to PostgreSQL.
- Flow: `connection = psycopg.connect(...)` → `cursor = connection.cursor()` → `cursor.execute(query, params)` → `cursor.fetchone()`/`fetchall()` → **`connection.commit()`** (changes are NOT saved until you commit!) → `cursor.close()` → `connection.close()`.
- Always close connections — leaked connections exhaust server resources.

### 3.4 CRUD, SQL Injection & the first Database Helper (Day 8)

- **SQL Injection**: malicious SQL smuggled in through unsanitized user input, most commonly via naive string concatenation (`f"SELECT * FROM users WHERE name = '{name}'"`) — this is dangerous and must never be done.
- **Parameterized queries** are the fix: `cur.execute(query, params)` — the driver sends parameters separately from the SQL text, so user input can never be interpreted as executable SQL.
- **`fetchone()`** → single row (single-record lookups). **`fetchall()`** → list of all matching rows (lists/reports).
- **Database Helper class**: centralizes connection + query execution logic so it isn't duplicated across the codebase — first step toward layered architecture.

### 3.5 Repository Pattern & Clean Architecture (Day 9) — pivotal day

- **Separation of Concerns (SoC)**: divide the app into parts, each with a single responsibility → better maintainability, readability, testability.
- **Layered architecture** introduced:
  ```
  Presentation → Service → Repository → Database Helper → PostgreSQL
  ```
- **Repository Pattern**: abstracts data access — provides methods to fetch/persist domain objects _without exposing raw SQL_ to the rest of the app. Repository knows about business entities and returns domain objects; the Database Helper below it just knows how to talk to the DB and execute generic SQL.
  | Repository | Database Helper |
  |---|---|
  | Knows business entities | Knows only DB communication |
  | Contains data-access methods | Manages connections/execution/transactions |
  | Returns domain objects | Executes generic SQL |
- **Service Layer**: sits between presentation and repository; holds **business rules** and coordinates behavior — this is where decisions like "is this a valid enrollment" belong, not in the repository or the router.
- **Clean Architecture** (Uncle Bob-style dependency rule): inner layers (Domain) never depend on outer layers (Infrastructure); dependencies point _inward_. Presentation → Application → Domain ← Infrastructure.
- **Data Access Layer (DAL)**: the umbrella term for Repository + Database Helper together.

### Common mistakes (Days 5–9)

- Building SQL via string concatenation instead of parameters (SQL injection risk).
- Forgetting `commit()` after INSERT/UPDATE/DELETE.
- Skipping normalization → repeating data across rows, no defined PK, one giant "do everything" table.
- Duplicating database-access code across multiple files instead of centralizing it in a helper/repository.

---

## 4. FastAPI & REST APIs (Days 10–14)

### 4.1 What FastAPI is, and why it replaced the CLI (Day 10)

- **FastAPI**: modern, high-performance Python web framework for building REST APIs, built on **Starlette** (ASGI) + **Pydantic** (validation), with async support and automatic interactive docs.
- **Why faster than Flask**: async-native, Pydantic-based validation baked in, efficient ASGI request handling (vs Flask's traditional WSGI/sync model).
- **API** = a contract that lets applications communicate over HTTP. **REST** = architectural style built around _resources_ (nouns, e.g. `/students`) manipulated via standard HTTP methods (verbs).
- **HTTP methods**: `GET` (read), `POST` (create), `PUT` (replace/full update), `PATCH` (partial update), `DELETE` (remove).
- **Uvicorn**: the ASGI server that actually runs the FastAPI app and handles incoming HTTP connections (FastAPI is the framework; Uvicorn is the server that hosts it — same relationship as ASP.NET Core app ↔ Kestrel).
- **Swagger UI** (`/docs`) and **ReDoc** (`/redoc`): auto-generated interactive API documentation, derived directly from your route + Pydantic model definitions — zero extra effort.
- Crucially: introducing FastAPI **only replaced the presentation/CLI layer** — Service and Repository layers built on Days 8–9 didn't need to change. This is Clean Architecture paying off in practice.

### 4.2 Request/Response Models, Path & Query Parameters (Day 11)

- **Pydantic**: validates, parses, and serializes data using Python type hints. A `BaseModel` subclass defines the expected shape of data.
- **Request Model**: defines the _incoming_ payload shape. **Response Model**: defines the _outgoing_ payload shape — kept separate so you can accept one shape but expose a different (safer, smaller) one.
- **Path Parameters** (`/students/{id}`) identify a _specific resource_. **Query Parameters** (`/students?city=Ahmedabad`) _filter/customize_ a result set.
- **Automatic validation**: if incoming JSON doesn't match the Request Model → FastAPI auto-returns **`422 Unprocessable Entity`** with detailed field-level errors, _before_ your endpoint logic even runs.

### 4.3 Dependency Injection & APIRouter (Day 12)

- **Dependency Injection (DI)**: a design pattern where objects receive their dependencies from an external provider rather than constructing them internally → reduces coupling, improves testability.
- **`Depends()`**: FastAPI's built-in DI mechanism — automatically provides required objects (e.g. a DB session, the current authenticated user) to route handlers.
- **APIRouter**: splits endpoints into separate modular files (e.g. `routers/students.py`) instead of piling everything into `main.py`, then wired together via `app.include_router(...)`.
- **Routers should stay thin** — only translate HTTP ↔ Service calls. Business logic belongs in the Service layer, never in the router.
- Project structure that emerges: `main.py → routers/ → services/ → repositories/ → database/ → models/`.
- **Enterprise parallel**: this is architecturally identical to ASP.NET Core's built-in DI container and Controller/Service separation — a very strong talking point given your C#/.NET background.

### 4.4 CRUD APIs, HTTP Status Codes & Exception Handling (Day 13)

- Correct status code discipline (this is one of the most commonly probed _practical_ interview topics):
  | Code | Meaning | When |
  |---|---|---|
  | 200 OK | success | GET, PUT |
  | 201 Created | success + new resource | POST |
  | 204 No Content | success, nothing to return | DELETE |
  | 400 Bad Request | malformed/invalid request | client error |
  | 401 Unauthorized | not authenticated | missing/invalid credentials |
  | 403 Forbidden | authenticated but not permitted | authorization failure |
  | 404 Not Found | resource doesn't exist | |
  | 500 Internal Server Error | unhandled server-side failure | |
- **`HTTPException`**: FastAPI's built-in way to short-circuit a request and return a structured error response with a status code + detail message: `raise HTTPException(status_code=404, detail="Student not found")`.
- **401 vs 403** (classic interview question): 401 = "I don't know who you are"; 403 = "I know who you are, but you can't do this."

### 4.5 Pydantic Validation & Response Models, deepened (Day 14)

- **`Field()`**: adds validation constraints + metadata/docs to a Pydantic field, e.g. `name: str = Field(min_length=2, max_length=50)`, `age: int = Field(gt=0, lt=100)`.
- **`Optional` fields** and **default values** for fields that aren't mandatory.
- **`EmailStr`** (via `pydantic[email]`): validates email format automatically without hand-rolled regex.
- Why separate Request vs Response models matters for **security**: it stops you accidentally leaking internal fields (password hashes, internal flags) back to the client, and stops clients from injecting fields they shouldn't control (e.g. `is_admin`).
- `response_model=StudentResponse` on a route: FastAPI automatically filters/serializes the return value to match that shape.

### Common mistakes (Days 10–14)

- Putting SQL directly in route handlers instead of delegating to Service/Repository.
- Writing all endpoints in one giant `main.py`.
- Returning `200 OK` for everything regardless of outcome.
- Using one Pydantic model for both request and response ("one model for everything").
- Returning raw DB objects directly instead of going through a Response Model.
- Mixing validation logic with business logic.

---

## 5. Security, Middleware, Observability & Configuration (Days 15–19)

### 5.1 Authentication, Authorization & JWT (Day 15) — high interview-density day

- **Authentication** = "who are you?" (verifying identity). **Authorization** = "what are you allowed to do?" (permissions). These are _frequently confused in interviews_ — always state both definitions explicitly.
- **JWT (JSON Web Token)** structure: `Header.Payload.Signature` (three base64url-encoded parts separated by dots).
  - **Header**: algorithm + token type.
  - **Payload**: claims (user id, roles, expiry, etc.) — NOT encrypted, just encoded, so **never put secrets/passwords in the payload**.
  - **Signature**: proves the token wasn't tampered with; computed from header+payload using a secret (HS256) or private key (RS256).
- **bcrypt**: used to hash passwords before storing them. Generates a **random salt per hash**, which is _why the same password produces a different hash every time_ — but bcrypt stores algorithm+cost+salt+hash together, so at verification time it re-extracts the salt and recomputes to compare.
- **JWT ≠ password hashing** — they solve different problems. bcrypt verifies passwords at login; JWT proves identity on every subsequent request without re-sending credentials.
- **HS256 vs RS256**: HS256 = single shared secret key (symmetric) used by both signer and verifier. RS256 = public/private key pair (asymmetric) — verifier only needs the public key, useful when multiple services must verify tokens without holding the signing secret.
- **Login flow**: credentials → bcrypt verify against stored hash → issue JWT → client stores/sends JWT on subsequent requests → server verifies signature (no DB hit needed just to confirm identity) → grants access to protected endpoints.
- Never: store plaintext passwords, put passwords inside JWTs, use non-expiring tokens, or hardcode `SECRET_KEY` in source code (it belongs in environment config, per Day 19).

### 5.2 Middleware, Request Lifecycle & CORS (Day 16)

- **Middleware**: code that runs _before and after every_ HTTP request — the mechanism for cross-cutting concerns (logging, timing, auth checks, security headers) without duplicating logic in every route.
- **`await call_next(request)`**: forwards the request to the next stage of the pipeline — forgetting this call means the request never reaches the router at all.
- Middleware should stay generic — **never put business logic inside middleware**.
- **CORS (Cross-Origin Resource Sharing)**: a _browser_ security mechanism restricting which origins (domain+scheme+port) can call your API from client-side JS. Postman/curl don't enforce CORS because CORS is a browser behavior, not a server one.
- `allow_origins=["*"]` is fine for local dev, but is a real anti-pattern for production (interviewers will probe this).
- **Middleware vs DI**: middleware runs for _every_ request unconditionally; DI (`Depends()`) only runs where explicitly declared on a route.

### 5.3 Structured Logging & Debugging (Day 17)

- **Why not `print()`**: no severity levels, no timestamps, no persistence, no filtering, not production-viable.
- Python's `logging` module, standard levels (ascending severity): **DEBUG → INFO → WARNING → ERROR → CRITICAL**.
- `logger.exception(...)` inside an `except` block automatically captures the full stack trace along with the message — extremely useful and underused.
- **Never log**: passwords, secrets, API keys, JWT secrets, or other sensitive user data.
- In production, logs are frequently the _only_ window into what actually happened — this is why logging discipline matters more than it seems on day one.

### 5.4 Global Exception Handling & Custom Exceptions (Day 18)

- Centralizing exception handling avoids duplicated try/except blocks scattered across routes and guarantees **consistent error response shape** across the whole API.
- **Custom/domain exceptions** (e.g. `StudentNotFoundException`) represent business concepts explicitly, decoupling business logic from framework-specific exception types.
- **Where to raise what**: business-rule violations should be raised in the **Service layer** (where business rules live), not in the Repository (which should just return data or `None`) and not in the Router (which shouldn't contain business logic at all).
- A `@app.exception_handler(...)` catches custom exceptions globally and converts them into a standardized JSON error shape, e.g. `{"success": false, "error": {"code": "...", "message": "..."}}`.
- Never expose raw internal errors (stack traces, DB error text) directly to API clients — translate them into safe, generic messages while logging the real detail internally.

### 5.5 Configuration & Environment Variables (Day 19)

- Never hardcode secrets/config values in source code — hard to change, insecure, easy to leak via source control.
- **`.env` file**: stores environment-specific config locally. **Must never be committed to Git** (use a `.env.example` template instead, per Day 25's mistake list).
- **Pydantic `Settings`**: loads config from environment variables with type safety and validation built in — the standard, professional way to manage FastAPI config.
- **Centralized configuration** avoids duplicating values (DB URL, secret key, log level) across multiple modules.
- **Twelve-Factor App principle**: config must be strictly separated from code; the same build/artifact should run unchanged across dev/staging/prod, with only environment variables differing.
- Dev vs Prod differ in _configuration values_ (DB URL, debug flag, log level, secrets) — the _application code itself_ should not need to change.

### Common mistakes (Days 15–19)

- Storing plaintext passwords; embedding passwords/secrets inside JWT payloads; never expiring tokens.
- Forgetting `await call_next(request)` in middleware (request pipeline breaks silently).
- Allowing `allow_origins=["*"]` into production.
- Using `print()` in place of structured logging; logging sensitive data.
- Raising `HTTPException` from inside a Repository (wrong layer).
- Committing `.env` to GitHub; hardcoding `SECRET_KEY`.

---

## 6. Transactions, Connection Pooling & Indexing (Days 20–22)

### 6.1 Database Transactions & ACID (Day 20)

- **Transaction**: a group of DB operations treated as one logical unit — either _all_ succeed (commit) or _all_ fail (rollback). Classic example: bank transfer = debit account A + credit account B must both happen or neither should.
- **`COMMIT`**: permanently saves all changes in the current transaction. **`ROLLBACK`**: discards all pending changes in the current transaction.
- **ACID**:
  - **Atomicity** — all operations in a transaction succeed together, or none are applied.
  - **Consistency** — a transaction moves the DB from one valid state to another valid state (constraints/rules always hold).
  - **Isolation** — concurrent transactions don't interfere with each other's intermediate state.
  - **Durability** — once committed, changes survive even a crash immediately after.
- Pattern in Python: wrap multi-step DB work in `try: ... connection.commit() / except: connection.rollback()`.
- **Where transaction handling belongs in Clean Architecture**: close to the data layer (Repository / a "Unit of Work" concept), _not_ scattered through the Service layer's business logic.
- Keep transactions **short** — long-running transactions hold locks longer and hurt concurrency/performance.

### 6.2 Connection Pooling & FastAPI Lifespan (Day 21)

- Opening a raw DB connection is _expensive_ — PostgreSQL must authenticate, allocate resources, spin up a backend process before it can even run a query. Doing this on every single request does not scale.
- **Connection pool**: a set of pre-established, reusable connections shared across requests — dramatically cuts per-request overhead.
- **FastAPI `lifespan`**: the mechanism to initialize expensive shared resources (DB pool, loggers, ML models) once at app **startup**, and clean them up once at **shutdown** — instead of per-request setup/teardown.
- Pattern: `pool = ConnectionPool(...)` created at startup → `with pool.connection() as conn: ...` borrowed per-request → pool closed at shutdown.
- **Repositories should borrow from the pool, never create their own raw connections.**
- Symptom of a pool leak / exhaustion: `"too many clients already"` from PostgreSQL — a real production error worth knowing by name.
- Pool size is a tuning decision — too small causes contention, too large wastes DB-side resources.

### 6.3 Database Indexing & Query Performance (Day 22)

- **Index**: a separate, sorted data structure (commonly a **B-Tree**) mapping column values → row locations, so PostgreSQL doesn't have to scan every row.
- **Sequential Scan**: examines every row in the table (slow at scale). **Index Scan**: jumps directly to matching rows via the index (fast).
- **`EXPLAIN`**: shows the planned execution strategy _without running_ the query. **`EXPLAIN ANALYZE`**: actually _executes_ the query and reports real timing/statistics (planning time, execution time, scan type used) — the primary tool for diagnosing "why is this query slow."
- **Trade-off**: indexes speed up reads but slow down writes (every INSERT/UPDATE/DELETE must also update the index) and consume extra storage — so **don't index every column**; index columns that are frequently filtered, joined, or sorted on.
- **Composite index**: a single index across multiple columns, useful when queries commonly filter on that combination together.
- **Primary Key** and **Unique** constraints automatically create indexes.
- Good candidates for indexing: FK columns, columns in frequent `WHERE`/`JOIN`/`ORDER BY` clauses. Poor candidates: low-cardinality columns (e.g. a boolean flag), rarely-queried columns.

### Common mistakes (Days 20–22)

- Forgetting `commit()`, or calling it too early (before all steps of a logical unit complete).
- Ignoring exceptions instead of rolling back on failure.
- Keeping transactions open unnecessarily long.
- Creating a brand-new DB connection per request instead of using the pool.
- Forgetting to close the pool on shutdown; sharing one connection across concurrent requests.
- Indexing every column "just in case"; assuming Postgres will always use an available index; optimizing without measuring (`EXPLAIN ANALYZE` first, always).

---

## 7. Docker & Containerized Deployment (Days 23–29)

### 7.1 Docker Fundamentals (Day 23)

- **Why Docker exists**: eliminate "works on my machine" — package an app with everything it needs so it runs identically across dev/test/prod.
- **Dockerfile** → (build) → **Image** → (run) → **Container**. This chain is the single most important mental model of the whole Docker unit.
  - **Image** = an immutable _template/package_ (app + dependencies + runtime).
  - **Container** = a _running instance_ of an image (like Class → Object, if you want the OOP parallel).
- **Docker Engine**: the underlying technology that actually builds/runs containers. **Docker CLI**: the command interface you use to talk to the Engine. **Docker Hub**: public registry for storing/distributing images.
- **Containers vs VMs**: a VM virtualizes an entire machine including a guest OS (heavy). A container shares the host OS kernel and isolates just the application process (lighter, faster to start).
- Core CLI: `docker --version`, `docker images`, `docker ps` / `docker ps -a`, `docker pull <image>`, `docker run <image>`, `docker stop <container>`, `docker rm <container>`, `docker rmi <image>`.
- Dockerfile instructions: `FROM` (base image), `WORKDIR` (working dir inside image), `COPY` (bring files in), `RUN` (executes **during build**), `CMD` (default command when container **starts**).
- Docker is a **deployment/runtime concern** — it wraps around Clean Architecture; it does not replace or change the Router/Service/Repository layering underneath.

### 7.2 Dockerizing FastAPI (Day 24)

- `RUN` vs `CMD`: `RUN` executes at _image build time_ (e.g. installing dependencies); `CMD` defines the _default startup command_ when a container is launched from that image.
- **`0.0.0.0`**: Uvicorn inside the container must bind to `0.0.0.0` (all interfaces), not `127.0.0.1`, or Docker can't forward external traffic into it.
- **`EXPOSE 8000`** only _documents_ the intended port — it does **not** publish/open it to the host. Actual host access requires `-p 8000:8000` at `docker run` time, mapping `host_port:container_port`.
- **`.dockerignore`**: excludes files (like `.env`, `.git`, `__pycache__`) from the build context — critical to avoid leaking secrets into an image.
- Changing source code does **not** auto-update a running container — you must **rebuild the image** and replace the container.
- Troubleshooting workflow for a container that exits immediately: `docker ps -a` (find it) → `docker logs <container>` (read the error) → fix → rebuild → run again.

### 7.3 Docker Compose & Multi-Container Architecture (Day 25)

- **Docker Compose**: declaratively define and run a _multi-container_ application (e.g. API + PostgreSQL together) from one `compose.yaml` file.
- **Service** = one component/container definition inside Compose (e.g. `api`, `db`).
- **Docker networking / service discovery**: Compose auto-creates a shared network; containers reach each other **by service name as hostname**, not by IP and not by `localhost`.
  - `DB_HOST=localhost` → **wrong** inside a container — `localhost` means "this same container," not "the other container."
  - `DB_HOST=db` → **correct** — `db` is resolved via Docker's embedded DNS to the actual PostgreSQL container.
- **`build` vs `image`** in Compose: `build` tells Compose to build from a Dockerfile; `image` tells it to pull/use an existing image.
- **Persistent volumes**: containers are disposable/ephemeral — a database's actual data must live in a **volume**, decoupled from the container's own lifecycle, or data is lost on container removal.
- Essential commands: `docker compose up` / `up -d` (background) / `up --build` (rebuild), `docker compose ps`, `docker compose logs`, `docker compose down`.
- Not every internal service needs a published host port — e.g. PostgreSQL usually doesn't need `5432:5432` published if only the API container (on the same Compose network) needs to reach it.

### 7.4 Health Checks & Service Readiness (Day 26)

- **Running ≠ Ready.** A container's main process being alive does not mean the service inside it can actually serve requests yet (e.g. Postgres process started but DB not yet accepting connections).
- **`depends_on` alone** only controls _startup order_, not readiness — a classic gotcha.
- **`healthcheck`**: a Docker-level test (e.g. `pg_isready` for Postgres) with `test`, `interval` (how often), `timeout` (max duration per check), `retries` (failures before marked unhealthy), `start_period` (grace period before failures count).
- **`depends_on` conditions**: `service_started` (just started) vs **`service_healthy`** (dependency passed its health check) vs `service_completed_successfully` (dependency ran to completion, e.g. a migration job).
- **Liveness vs Readiness** (this distinction is the direct conceptual bridge to Kubernetes probes later): Liveness = "is the process alive?" Readiness = "can it actually handle work right now?" A container can be `running` yet `unhealthy` — these are separate states.
- Golden pattern: `depends_on: { db: { condition: service_healthy } }` combined with a _meaningful_ health check (testing real capability, not just "process exists").

### 7.5 Environment Management & Local Deployment discipline (Day 27)

- **`environment`** (inline in Compose) vs **`env_file`** (load from a file) — two different mechanisms for injecting container env vars.
- `.env` is commonly used for **Compose variable interpolation** (`${VAR}`, with `${VAR:-default}` for defaults) — but this is a _separate_ mechanism from actually injecting variables into a container's runtime environment; don't conflate the two.
- **`docker compose config`**: shows the fully-resolved configuration after interpolation — the best first tool for debugging "why is my env var not what I expect."
- **Restart policies** (e.g. `restart: on-failure`) answer "what happens after the container's process exits?" — a _different_ concern from health checks, which answer "is the service healthy right now?"
- **Dev vs Prod containers differ deliberately**: dev commonly uses **bind mounts** (host source code mapped live into the container, for fast iteration); production should run a built, **immutable image** instead — not depend on host filesystem state.
- Change one configuration layer at a time when debugging (`.env`, `compose.yaml`, Dockerfile, Pydantic Settings) — changing all four simultaneously makes root-causing nearly impossible.

### 7.6 Docker Internal Networking Deep-Dive (Day 28)

- **Bridge network**: Docker's default local network driver connecting containers while isolating them from unrelated networks. Docker Compose auto-creates a **user-defined bridge network** for your app, which additionally provides name-based DNS resolution between its containers (the default bridge network does not).
- `localhost` inside a container **always** means "this container's own network namespace" — never another container, regardless of context.
- Container-to-container communication over the same Compose network does **not** require published (`-p`) ports at all — published ports are for **host ↔ container** access, not container ↔ container.
- **Container IPs are dynamically allocated** — never hardcode them; always use the logical service name (Docker's embedded DNS resolves it).
- Troubleshooting tools: `docker network ls`, `docker network inspect <network>`, `docker compose exec api sh` (shell into a running container to test connectivity directly).
- Full systematic connectivity-debugging order: **process status → health status → shared network → correct `DB_HOST` → correct internal port → correct credentials → logs.**

### 7.7 Reproducible Local Deployment (Day 29)

- **Reproducible deployment**: the whole stack can be recreated deterministically from source + Dockerfile + Compose config + declared persistent storage — not from manually-tweaked machine state.
- Containers should be treated as **ephemeral/replaceable** — never hand-patch files inside a running production container; the correct loop is always: change source → rebuild image → replace container.
- **Image hygiene**: exclude irrelevant files via `.dockerignore`, avoid unnecessary installed packages, pick an appropriately small/trusted base image.
- **Multi-stage builds**: separate a "build" stage (compilers, build-only deps) from the final "runtime" stage, so build-only tooling never ships in the final production image — smaller, more secure image.
- **Non-root containers**: run the application as a dedicated non-root user inside the container — least-privilege principle, reduces blast radius if the container is ever compromised.
- A deployment is only "done" once verified end-to-end (real request → real DB round trip) — not just because `/docs` loads in a browser.

### Common mistakes (Days 23–29)

- Treating a container like a lightweight VM you SSH into and hand-edit.
- Confusing `EXPOSE` with actually publishing a port (`-p`) — one documents intent, the other opens the door.
- Copying `.env`/secrets into the image instead of injecting them at runtime.
- Hardcoding container IPs; using `localhost` for inter-container communication.
- Publishing every internal service's port to the host unnecessarily.
- Forgetting a persistent volume for the database → data lost on container removal.
- Relying on `depends_on` alone as a readiness guarantee.
- Running production off bind-mounted source instead of a built, immutable image.
- Running the app as root by default without a compatibility reason not to.

---

## 8. Advanced SQL — JOINs & Relational Query Design (Day 30)

- **Why JOINs exist**: a normalized schema splits data across multiple tables — JOINs are how you recombine them to answer real questions (e.g. "which courses is each student enrolled in").
- **`INNER JOIN`**: returns only rows where the join condition matches on _both_ sides.
- **`LEFT JOIN`**: returns _every_ row from the left table, plus matching right-table data where it exists, `NULL` where it doesn't — use when you need "all X, including those without a related Y" (e.g. "every student, including those with zero enrollments").
- **`RIGHT JOIN`**: mirror of LEFT JOIN (all rows from the right table). **`FULL OUTER JOIN`**: all rows from both sides, matched where possible.
- **`ON` vs `WHERE` with an outer join** (a genuinely tricky, high-value interview topic): `ON` decides _which rows match_ during the join itself; `WHERE` filters the _already-joined result_ afterward. Moving a condition on the right-hand table from `ON` into `WHERE` on a LEFT JOIN can silently convert it back into an INNER JOIN — accidentally dropping the unmatched left-side rows you meant to keep.
- **Table aliases** (`students s`, `courses c`) keep multi-table queries readable.
- **Three-table JOIN**: chain JOINs — `students → enrollments → courses` — each JOIN condition connects one FK/PK pair at a time.
- **`GROUP BY`** groups rows so aggregate functions (`COUNT`, `SUM`, `AVG`) apply per group. **`HAVING`** filters _after_ aggregation (whereas `WHERE` filters _before_ aggregation — another common point of confusion).
- **JOIN cardinality**: a JOIN can legitimately multiply rows — one student row can appear multiple times if they have multiple matching enrollments; this is _correct behavior_, not a bug, when the relationship is genuinely one-to-many.
- **Where JOIN SQL belongs in Clean Architecture**: the **Repository/data-access layer** — never in the Router, never in the Service layer's business-rule code.
- **JOIN performance**: JOINs are not inherently slow — performance comes down to correct predicates, relevant indexes on join/filter columns, and measuring with `EXPLAIN ANALYZE`, not avoiding JOINs on principle.
- Common mistakes: missing/omitted JOIN condition (accidental Cartesian product), joining on the wrong columns (query runs, but returns logically wrong data — a silent bug, more dangerous than a syntax error), using INNER JOIN when LEFT JOIN was actually required, filtering an outer join incorrectly via `WHERE` (see above), and `SELECT *` in production queries instead of explicit columns (couples you to schema changes and obscures the actual result contract).

Example pattern worth having memorized cold:

```sql
SELECT
    s.name AS student_name,
    c.name AS course_name
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id;
```

---

## 9. Master Interview Question Bank (grouped by theme, deduplicated)

### Python Core

1. **Difference between List and Tuple?** List: ordered, mutable, allows duplicates. Tuple: ordered, immutable, allows duplicates — use when data must never change.
2. **Difference between Set and Dictionary?** Set: unique unordered values. Dictionary: unique keys mapped to values.
3. **Mutable vs Immutable?** Mutable: list, dict, set. Immutable: string, tuple, int, float.
4. **Why is dictionary/set lookup O(1) on average?** Both are hash tables: a hash function converts the key into an integer, which maps to a direct index in an underlying array — direct array indexing is O(1), so no scanning is needed.
5. **`==` vs `is`?** `==` compares values; `is` compares object identity (same memory reference).
6. **Difference between parameter and argument?** Parameter = variable in the function definition. Argument = actual value passed at call time.
7. **`print()` vs `return`?** `print()` just displays output; `return` sends a value back to the caller for further use.
8. **What is `if __name__ == "__main__":` and why use it?** Ensures a block only runs when the file is executed directly, not when imported as a module — the standard Python entry-point idiom.
9. **What is an exception, and the role of `try/except/else/finally`?** An exception is a runtime error interrupting normal flow. `try` = risky code, `except` = handle specific errors, `else` = runs only if no exception occurred, `finally` = always runs (cleanup).
10. **Why avoid a bare `except:`?** It silently catches everything, including bugs you actually want surfaced, making debugging much harder.
11. **Why use `with open(...)` instead of `open()`?** Automatically closes the file and manages resources safely even if an exception occurs.
12. **What is OOP, and Class vs Object?** OOP organizes code around objects (data + behavior). Class = blueprint; Object = instance created from it.
13. **What does `__init__` do, and why is `self` required?** `__init__` is the constructor, auto-called on object creation to set initial state. `self` refers to the current instance, letting methods read/write that specific object's data.
14. **Function vs Method?** A function is independent, outside a class; a method is defined inside a class and operates on an object's data.

### Git & SQL Basics

15. **Git vs GitHub?** Git = local version control tool; GitHub = cloud platform hosting Git repositories.
16. **Git workflow?** Working Directory → Staging (`add`) → Local Repository (`commit`) → Remote Repository (`push`).
17. **Database vs Table?** Database = collection of related tables; Table = rows × columns.
18. **What is a Primary Key?** A column (or set of columns) that uniquely identifies each row — no duplicates, no NULLs.
19. **`DELETE` vs `DROP`?** `DELETE` removes rows, keeps table structure. `DROP` removes the whole table (structure + data).
20. **`WHERE` vs `ORDER BY`?** `WHERE` filters rows; `ORDER BY` sorts them.

### Database Design & Relationships

21. **What is a relational database?** One that stores data across multiple related tables connected via keys.
22. **Primary Key vs Foreign Key?** PK uniquely identifies a row in its own table; FK references another table's PK to create a relationship.
23. **Why normalize a database?** To reduce redundancy, improve consistency, and simplify maintenance.
24. **What is a One-to-Many relationship?** One record in table A relates to many records in table B (e.g. one customer → many orders).
25. **Why do Many-to-Many relationships need a junction table?** Relational databases can't store M:N directly — a third table maps both FKs to represent the relationship.

### PostgreSQL & Python Integration / CRUD / SQL Injection

26. **SQL vs PostgreSQL?** SQL is the language; PostgreSQL is the DBMS software that executes it.
27. **Why do we need `psycopg`?** It's the driver/bridge letting Python talk to PostgreSQL.
28. **What is a cursor?** An object that executes SQL commands and retrieves results from the DB.
29. **Why is `commit()` required?** Changes from INSERT/UPDATE/DELETE stay pending in the transaction until committed — `commit()` permanently saves them.
30. **What is CRUD?** Create, Read, Update, Delete — the four fundamental operations on persisted data.
31. **What is SQL Injection, and how do parameterized queries prevent it?** SQL Injection = malicious SQL smuggled through unsanitized input (typically via string concatenation). Parameterized queries separate SQL text from input values, so the driver never treats input as executable SQL.
32. **`fetchone()` vs `fetchall()`?** `fetchone()` returns a single row (single-record lookups); `fetchall()` returns all matching rows (lists/reports).
33. **Purpose of a Database Helper class?** Centralizes connection/query logic, reduces duplication, improves maintainability.

### Clean Architecture / Repository / Service Layer

34. **What is Separation of Concerns?** A design principle dividing an app into distinct parts, each with a single responsibility, improving maintainability, readability, testability.
35. **What is the Repository Pattern?** Abstracts data access — exposes methods to retrieve/persist domain objects without leaking SQL into the rest of the app.
36. **Repository vs Database Helper?** Repository knows business entities and returns domain objects; Database Helper only knows how to talk to the DB and execute generic SQL.
37. **What is the Service Layer responsible for?** Business rules and coordinating application behavior, sitting between presentation and repository.
38. **What is Clean Architecture?** An architecture organizing code into layers with clear responsibilities and dependencies pointing _inward_ toward the domain, improving testability and maintainability.

### FastAPI / REST

39. **What is FastAPI, and why is it fast?** A modern, high-performance Python framework for building REST APIs with automatic validation and docs; built on Starlette + Pydantic, async-native.
40. **What is an API endpoint?** A specific URL exposing an operation on a resource (e.g. `GET /students`).
41. **What is Uvicorn?** The ASGI server that runs the FastAPI application and handles incoming HTTP requests.
42. **What is Pydantic, and why does FastAPI use it?** A library that validates/serializes data using Python type hints — used for automatic request validation, type conversion, and OpenAPI schema generation.
43. **What is Swagger UI / ReDoc?** Auto-generated interactive API documentation derived from your routes and Pydantic models.
44. **Path vs Query Parameters?** Path parameters identify a specific resource (`/students/10`); query parameters filter/customize results (`/students?city=Ahmedabad`).
45. **What is a Request Model vs a Response Model, and why separate them?** Request = expected incoming shape; Response = outgoing shape. Separating them controls exactly what clients can send and what the API exposes back — improves security and maintainability.
46. **What happens on invalid input?** Pydantic validation fails → FastAPI automatically returns `422 Unprocessable Entity` with field-level errors, without running endpoint logic.
47. **What is Dependency Injection, and what is `Depends()`?** DI = objects receive dependencies from an external provider instead of creating them, reducing coupling and improving testability. `Depends()` is FastAPI's built-in DI mechanism.
48. **Why use APIRouter?** Organizes endpoints into modular files for maintainability/scalability instead of one giant `main.py`.
49. **Why should routers stay thin?** They should only translate HTTP ↔ service calls; business logic belongs in the Service layer.
50. **Difference between GET and POST?** GET retrieves data without modifying server state; POST creates resources and changes state.
51. **Why 201 instead of 200 after POST?** `201 Created` explicitly signals a new resource was successfully created.
52. **Why 204 after DELETE?** The deletion succeeded and there's no response body to return.
53. **401 vs 403?** 401 = not authenticated ("I don't know who you are"). 403 = authenticated but not permitted ("I know you, but you can't do this").
54. **What is `HTTPException`?** FastAPI's built-in mechanism to return structured HTTP error responses with a status code and detail message.
55. **What does `Field()` do in Pydantic?** Defines validation constraints, metadata, and documentation for a model field.
56. **Why use `EmailStr`?** Validates email format automatically without custom regex.

### Authentication / JWT / Security

57. **Authentication vs Authorization?** Authentication verifies identity; authorization determines permissions.
58. **What is JWT, and its structure?** A digitally signed token identifying an authenticated user without resending credentials each time; structured as Header.Payload.Signature.
59. **Why use bcrypt?** To securely hash passwords before storing them.
60. **Does JWT use bcrypt?** No — bcrypt verifies _passwords_; JWT uses HMAC (HS256) or public/private-key crypto (RS256) to create/verify _signatures_. Different problems.
61. **Why do bcrypt hashes differ each time for the same password?** bcrypt generates a new random salt per hash; the salt is stored alongside the hash so verification can recompute and compare correctly.
62. **How does an API server verify a JWT?** It recomputes the signature using its own SECRET_KEY (HS256) or the public key (RS256) and compares it to the token's signature.
63. **HS256 vs RS256?** HS256 = single shared secret (symmetric). RS256 = public/private key pair (asymmetric) — lets multiple services verify without holding the signing secret.

### Middleware / CORS / Logging / Exceptions / Config

64. **What is Middleware, and why use it?** Code executing before/after every HTTP request; implements cross-cutting concerns (logging, timing, security headers, CORS) without duplicating logic per route.
65. **What does `call_next(request)` do?** Forwards the request to the next stage of the pipeline.
66. **What is CORS, and why doesn't Postman need it?** A browser security mechanism controlling which origins can call your API from client-side JS; enforced by browsers, not by tools like Postman.
67. **Middleware vs Dependency Injection?** Middleware runs on every request; DI runs only where explicitly declared.
68. **Why is logging better than `print()`?** Provides timestamps, severity levels, persistence, filtering, and monitoring capability.
69. **Standard log levels?** DEBUG, INFO, WARNING, ERROR, CRITICAL (ascending severity).
70. **When to use `logger.exception()`?** Inside an `except` block, to log both the message and the full stack trace automatically.
71. **What should never be logged?** Passwords, secrets, API keys, JWT secrets, sensitive user data.
72. **Why use global exception handling?** Centralizes error handling, avoids duplicate code, guarantees consistent API error responses.
73. **Where should business exceptions be raised in Clean Architecture?** In the Service layer, where business rules are enforced — not in Repository (data access only) and not in Router (no business logic).
74. **Why shouldn't secrets be hardcoded?** Hard to change, insecure, risk of accidental exposure via source control.
75. **Why use Pydantic Settings?** Loads configuration from environment variables automatically, with validation and type safety.
76. **What changes between Dev and Prod?** Config values (DB URL, debug flag, log level, secrets) — the application _code_ should stay the same (Twelve-Factor App principle).

### Transactions / Pooling / Indexing

77. **What is a database transaction?** A group of operations treated as one logical unit — all succeed (commit) or all fail (rollback).
78. **`COMMIT` vs `ROLLBACK`?** COMMIT permanently saves changes; ROLLBACK discards pending changes in the current transaction.
79. **What does Atomicity mean (ACID)?** All operations in a transaction succeed together, or none are applied.
80. **Why is opening a DB connection expensive?** PostgreSQL must authenticate, allocate resources, and create a backend process before it can execute queries.
81. **What is a connection pool, and why use one?** A set of reusable connections shared across requests, avoiding the overhead of creating a new connection per request.
82. **Why use FastAPI Lifespan?** To initialize expensive shared resources (DB pool, loggers, ML models) once at startup and clean them up at shutdown.
83. **Should repositories create their own DB connections?** No — they should borrow from the shared pool and return them when finished.
84. **What is a database index, and why is it faster?** A separate structure (typically B-Tree) mapping column values to row locations, so Postgres searches a much smaller sorted structure instead of scanning every row.
85. **Sequential Scan vs Index Scan?** Sequential Scan reads every row; Index Scan navigates directly to matching rows via the index.
86. **`EXPLAIN` vs `EXPLAIN ANALYZE`?** `EXPLAIN` shows the planned execution strategy without running the query; `EXPLAIN ANALYZE` actually executes it and reports real performance stats.
87. **Should every column be indexed?** No — indexes speed reads but slow writes and cost storage; index only columns frequently searched/filtered/joined/sorted on.

### Docker & Docker Compose

88. **What is Docker, and what is a container?** Docker is a platform for packaging/running apps in containers for consistent environments across dev/test/prod. A container is an isolated running instance created from an image.
89. **What is a Docker image, and Image vs Container?** An image is an immutable template/package of the app + dependencies. Image = template; Container = running instance (same relationship as Class → Object).
90. **What is a Dockerfile?** A text file of instructions used to build a Docker image.
91. **Docker vs VM?** A VM virtualizes a full machine including a guest OS; containers share the host kernel and isolate just the process, so they're generally lighter and start faster.
92. **`RUN` vs `CMD`?** `RUN` executes during image build; `CMD` defines the default command when a container starts.
93. **What does `EXPOSE 8000` do — does it publish the port?** It only documents the intended port; it does **not** publish it. Host access requires `-p host:container` at run time.
94. **Why does Uvicorn bind to `0.0.0.0` inside a container?** So Docker can forward external traffic from the host into the container's network interface.
95. **Why use `.dockerignore`?** To prevent unnecessary or sensitive files (e.g. `.env`, `.git`) from entering the build context/image.
96. **What is Docker Compose, and why use it?** A tool to declaratively define and run multi-container applications, simplifying management of services, networks, volumes, and environment variables.
97. **How do Compose services discover each other?** Via Docker's embedded DNS and the auto-created network — containers reach each other **by service name** (e.g. `db`), not `localhost` and not hardcoded IPs.
98. **Why doesn't `localhost` work for container-to-container communication?** `localhost` always refers to the current container's own network namespace, never another container.
99. **Do containers need published ports to talk to each other?** No — published (`-p`) ports are only for host↔container access; containers on the same Compose network communicate directly without publishing.
100.  **Why do databases need volumes?** Containers are disposable; volumes decouple persistent data from the container's own lifecycle so data survives container removal/recreation.
101.  **`build` vs `image` in Compose?** `build` builds an image from a Dockerfile/context; `image` uses an existing pre-built image.
102.  **Running vs Ready — why isn't `depends_on` alone enough?** A container's process being "running" doesn't guarantee the service inside is actually ready to serve requests; `depends_on` alone only orders startup, it doesn't wait for readiness.
103.  **What is a Docker health check?** A test Docker runs to determine whether the service inside a container is functioning as expected (e.g. `pg_isready` for Postgres).
104.  **`service_started` vs `service_healthy`?** `service_started` = dependency container has started; `service_healthy` = dependency has passed its health check.
105.  **Can a container be running but unhealthy?** Yes — "running" and "healthy" are separate, independent states.
106.  **`environment` vs `env_file` in Compose?** `environment` sets variables directly inline; `env_file` loads them from a file.
107.  **Why is `docker compose config` useful?** It shows the fully resolved configuration after variable interpolation — the best tool for diagnosing config problems.
108.  **What is a Docker bridge network, and user-defined bridge vs default bridge?** A bridge network connects containers with isolation from unrelated networks. A user-defined bridge (which Compose creates automatically) additionally provides name-based DNS resolution between containers, unlike the default bridge.
109.  **Why avoid hardcoding container IPs?** Docker allocates container IPs dynamically, especially on recreation — logical service names are stable, IPs are not.
110.  **What does reproducible deployment mean?** The environment can be recreated deterministically from source + Dockerfile + Compose config + declared persistent storage, not from manually-tweaked machine state.
111.  **What is a multi-stage Docker build, and why use one?** A Dockerfile pattern separating a "build" stage from a "runtime" stage, so build-only tools/dependencies don't ship in the final image — smaller, more secure.
112.  **Why run containers as a non-root user?** Least-privilege principle — reduces the process's privileges and blast radius if compromised.

### Advanced SQL (JOINs)

113. **INNER JOIN vs LEFT JOIN?** INNER JOIN returns only matching rows from both sides. LEFT JOIN returns all rows from the left table plus matching right-table data (NULL where no match).
114. **Why can a JOIN "duplicate" rows, and is that a bug?** One left-side row can match multiple right-side rows in a one-to-many relationship — this is correct behavior, not a bug.
115. **`ON` vs `WHERE` with a LEFT JOIN?** `ON` controls which rows match during the join; `WHERE` filters the already-joined result afterward. Moving a right-table condition from `ON` to `WHERE` can silently drop unmatched left-side rows, effectively turning it back into an INNER JOIN.
116. **`GROUP BY` vs `HAVING`?** `GROUP BY` groups rows for aggregate functions; `HAVING` filters groups _after_ aggregation (vs `WHERE`, which filters rows _before_ aggregation).
117. **Where should JOIN SQL live in Clean Architecture?** In the Repository/data-access layer — not the Router, not the Service layer's business logic.
118. **How is JOIN performance improved?** Correct schema design, correct join predicates, relevant indexes on join/filter columns, and measuring with `EXPLAIN ANALYZE` — not by avoiding JOINs.

---

## 10. Master Cheat Sheet

### Python quick reference

```python
len(); type(); print(); range(); enumerate(); zip(); sorted(); sum(); min(); max(); any(); all()

# functions
def add(a, b): return a + b
def greet(name="Guest"): print(name)
import module
from module import function
if __name__ == "__main__":
    main()

# exceptions + files
try:
    ...
except ValueError:
    ...
except FileNotFoundError:
    ...
else:
    ...
finally:
    ...

with open("file.txt", "r") as f: data = f.read()
with open("file.txt", "w") as f: f.write("Hello")   # overwrites
with open("file.txt", "a") as f: f.write("World")   # appends

# OOP
class Student:
    def __init__(self, name):
        self.name = name
    def display(self):
        print(self.name)

student = Student("Mayank")
student.display()
```

### Git

```bash
git status
git add .
git add <file>
git commit -m "message"
git log
git diff
git checkout -- <file>
git branch
git push
git pull
```

### SQL essentials

```sql
CREATE DATABASE db_name;
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);
INSERT INTO students (name, email) VALUES ('Mayank', 'm@x.com');
SELECT * FROM students WHERE name = 'Mayank' ORDER BY student_id;
UPDATE students SET name = 'New Name' WHERE student_id = 1;
DELETE FROM students WHERE student_id = 1;
SELECT city, COUNT(*) FROM students GROUP BY city HAVING COUNT(*) > 5;
```

### psycopg (Python ↔ PostgreSQL)

```python
connection = psycopg.connect(...)
cursor = connection.cursor()
cursor.execute(query, params)          # ALWAYS parameterized — never string-concat SQL
results = cursor.fetchall()            # or .fetchone() for a single row
connection.commit()                    # required after INSERT/UPDATE/DELETE
cursor.close()
connection.close()

# transactions
try:
    cursor.execute(...)
    cursor.execute(...)
    connection.commit()
except Exception:
    connection.rollback()

# connection pool + lifespan pattern
pool = ConnectionPool(...)             # created once at app startup
with pool.connection() as conn:        # borrowed per-request
    ...
```

### Clean Architecture layering (memorize this diagram)

```
Presentation (Router)
      ↓
Service (business rules)
      ↓
Repository (returns domain objects, hides SQL)
      ↓
Database Helper (generic SQL execution, connections)
      ↓
PostgreSQL
```

Dependency Rule: dependencies always point **inward**. Presentation → Application → Domain ← Infrastructure. Nothing in Domain should ever import from Infrastructure.

### FastAPI

```python
from fastapi import FastAPI, Depends, APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()
router = APIRouter()

class StudentRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(gt=0, lt=100)
    email: EmailStr

class StudentResponse(BaseModel):
    id: int
    name: str

@router.get("/students/{student_id}")
def get_student(student_id: int, service = Depends(get_student_service)):
    student = service.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/students", response_model=StudentResponse, status_code=201)
def create_student(payload: StudentRequest, service = Depends(get_student_service)):
    return service.create(payload)

app.include_router(router)
```

- HTTP methods → CRUD: `GET`=Read, `POST`=Create, `PUT`=Replace, `PATCH`=Partial Update, `DELETE`=Delete.
- Status codes: `200` OK · `201` Created · `204` No Content · `400` Bad Request · `401` Unauthorized · `403` Forbidden · `404` Not Found · `422` Validation Error (automatic from Pydantic) · `500` Internal Server Error.
- Docs: `/docs` → Swagger UI, `/redoc` → ReDoc.
- Run: `uvicorn main:app --reload` (dev) / `uvicorn main:app --host 0.0.0.0 --port 8000` (container).

### Auth (JWT + bcrypt)

```
Authentication → "Who are you?"
Authorization  → "What are you allowed to do?"

Password → bcrypt.hash() → stored in DB
Login: password → bcrypt.verify() → JWT issued
JWT = Header . Payload . Signature   (base64url, dot-separated)
Protected route: JWT → verify signature (HS256 shared secret / RS256 public key) → allow/deny
```

### Middleware / CORS

```python
@app.middleware("http")
async def timing_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)     # NEVER forget this line
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["https://mydomain.com"], allow_methods=["*"])
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug(...); logger.info(...); logger.warning(...); logger.error(...); logger.critical(...)

try:
    ...
except Exception:
    logger.exception("Failed to insert student into PostgreSQL")   # auto-captures stack trace
```

### Config (Pydantic Settings + .env)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    class Config:
        env_file = ".env"

settings = Settings()
# .env — NEVER commit this file; commit a .env.example template instead
```

### Indexing

```sql
CREATE INDEX idx_students_email ON students(email);
EXPLAIN SELECT * FROM students WHERE email = 'x@y.com';
EXPLAIN ANALYZE SELECT * FROM students WHERE email = 'x@y.com';
```

### Docker

```bash
docker --version
docker images
docker ps            # running containers
docker ps -a          # all containers (including stopped)
docker pull <image>
docker build -t student-management-api .
docker run --name student-api -p 8000:8000 student-management-api
docker logs student-api
docker stop student-api
docker rm student-api
docker rmi <image>
```

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```
Dockerfile → (docker build) → Image → (docker run) → Container
EXPOSE 8000       → documents intent only, does NOT publish
-p 8000:8000      → host_port:container_port, actually publishes
0.0.0.0           → bind inside container so Docker can forward traffic in
```

### Docker Compose

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DB_HOST: db
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

```bash
docker compose up            # start (foreground)
docker compose up -d         # start (background)
docker compose up --build    # rebuild + start
docker compose ps
docker compose logs api
docker compose config        # show fully resolved config — debug tool
docker compose exec api sh   # shell into a running container
docker network ls
docker network inspect <network>
docker compose down          # stop + remove
```

```
Inside a container:
  localhost      → THIS container
  service name   → ANOTHER Compose service (via Docker's embedded DNS)

running   ≠ healthy ≠ reachable   (three separate things to verify when debugging)
```

### Advanced SQL — JOINs

```sql
-- INNER JOIN: matching rows only
SELECT s.name, c.name AS course
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id;

-- LEFT JOIN: all students, even with zero enrollments
SELECT s.name, c.name AS course
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id
LEFT JOIN courses c ON e.course_id = c.course_id;

-- GROUP BY + HAVING
SELECT s.student_id, COUNT(e.course_id) AS course_count
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id
GROUP BY s.student_id
HAVING COUNT(e.course_id) > 2;
```

---

## 11. FastAPI ↔ ASP.NET Core Mapping (your fastest bridge from known → new)

Since 6+ years of C#/.NET experience is your baseline, this table is one of your strongest interview weapons — it lets you reframe "new" FastAPI knowledge as "same architectural principles, different syntax."

| Concept                    | FastAPI (Python)                         | ASP.NET Core (C#)                                    |
| -------------------------- | ---------------------------------------- | ---------------------------------------------------- |
| Web server                 | Uvicorn (ASGI)                           | Kestrel                                              |
| Routing                    | `@router.get("/x")`, `APIRouter`         | `[HttpGet("x")]`, Controllers                        |
| Request/response contracts | Pydantic `BaseModel`                     | DTOs / POCOs with Data Annotations                   |
| Validation                 | Automatic via Pydantic + `Field()`       | Data Annotations / FluentValidation                  |
| Dependency Injection       | `Depends()`                              | Built-in DI container (constructor injection)        |
| Layering                   | Router → Service → Repository            | Controller → Service → Repository                    |
| Middleware                 | `@app.middleware("http")`, `call_next()` | `IMiddleware`, `_next()` delegate pipeline           |
| Global exception handling  | `@app.exception_handler(...)`            | Exception filters / `UseExceptionHandler` middleware |
| Config                     | Pydantic `Settings` + `.env`             | `appsettings.json` + `IConfiguration`                |
| Logging                    | Python `logging` module                  | `ILogger<T>`                                         |
| ORM/data access            | psycopg (raw) / Repository pattern       | Entity Framework Core / Dapper                       |
| API docs                   | Swagger UI (`/docs`), ReDoc              | Swashbuckle / Swagger UI                             |
| Auth                       | JWT + bcrypt (manual/PyJWT)              | ASP.NET Core Identity + JWT Bearer                   |
| Async model                | `async def` / ASGI                       | `async Task<T>` / Kestrel async pipeline             |

**The takeaway to say out loud in an interview:** _"The concepts transfer directly — Dependency Injection, layered/Clean Architecture, middleware pipelines, centralized config, and structured logging are identical in spirit across ASP.NET Core and FastAPI. What changed is syntax and ecosystem, not the underlying engineering discipline — which is exactly why 6 years in one stack accelerates ramp-up in another."_

---

## 12. Things to Always Remember (the fast-forgettable, expensive-to-fumble list)

1. **`commit()` is not automatic.** Every INSERT/UPDATE/DELETE from Python via psycopg needs an explicit `connection.commit()` or the change silently never persists.
2. **Never build SQL via string concatenation/f-strings with user input** — always parameterized queries (`cursor.execute(query, params)`). This is the #1 SQL Injection defense and a guaranteed interview topic.
3. **`EXPOSE` in a Dockerfile does not open a port.** Only `-p host:container` (or Compose `ports:`) actually publishes it.
4. **Inside a container, `localhost` always means "this container."** Use the Compose service name (e.g. `db`) to reach another container — never hardcode a container IP.
5. **`depends_on` alone is startup _order_, not readiness.** Pair it with `condition: service_healthy` + a real `healthcheck` if the dependent service actually needs the other one _ready_, not just _started_.
6. **A container can be `running` and `unhealthy` at the same time** — these are two separate states; don't conflate them.
7. **Authentication ≠ Authorization.** Say both definitions explicitly whenever this comes up — it's a very common "sounds obvious, gets fumbled anyway" question.
8. **JWT payload is encoded, not encrypted** — never put secrets/passwords in it. bcrypt (passwords) and JWT (identity tokens) solve two _different_ problems; don't merge them in an explanation.
9. **Business exceptions belong in the Service layer** — Repository returns data/`None`, Router has no business logic, Service is where "is this actually valid" gets decided.
10. **Request Model ≠ Response Model.** Keeping them separate is a security control (prevents leaking internal fields, prevents clients injecting fields they shouldn't control), not just a style preference.
11. **Routers stay thin.** If you're writing SQL or business rules inside a route handler, that logic is in the wrong layer.
12. **`.env` is never committed.** Commit a `.env.example` template instead; secrets live in environment config, never in source.
13. **`ON` vs `WHERE` in an outer JOIN changes the result.** Moving a right-table filter from `ON` to `WHERE` on a LEFT JOIN can silently drop the unmatched left rows you meant to keep — this single fact is a favorite senior-level SQL trap question.
14. **Index columns you actually filter/join/sort on — not everything.** Indexes trade write speed and storage for read speed; measure with `EXPLAIN ANALYZE` before optimizing, don't guess.
15. **Connections are expensive — pool them, and borrow/return, never create ad hoc per request.** The failure mode to know by name: `"too many clients already"`.
16. **Docker images are immutable; containers are disposable.** Never hand-patch a running container's files — change source, rebuild the image, replace the container.
17. **Docker is a deployment concern, not an architecture concern.** It wraps around Clean Architecture; it never replaces the Router/Service/Repository layering.
18. **Config changes between environments (dev/prod); application code does not** — this is the Twelve-Factor App principle, and it's the correct answer whenever asked "what's different between your dev and prod setup."
19. **`GROUP BY`/`HAVING` filters groups after aggregation; `WHERE` filters rows before aggregation.** Don't reach for `WHERE` when you actually need `HAVING`.
20. **When debugging Docker connectivity, go in order**: container status → health status → shared network → correct `DB_HOST`/hostname → correct internal port → correct credentials → logs. Reciting this order in an interview signals real operational experience, not memorized trivia.

---

## 13. Month 1 Status Check (against `04_Progress.md` / `README.md` roadmap)

Skills flagged in the roadmap and their Month-1 status based on what was actually covered in the Engineering Handbook:

| Skill                                          | Status after Day 30                                                                                                                                                                |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python Advanced                                | ✅ Core language, OOP, exceptions, file handling covered (Days 1–4)                                                                                                                |
| Git                                            | ✅ Workflow + 10 core commands (Day 5)                                                                                                                                             |
| SQL                                            | ✅ Fundamentals → design/normalization → advanced JOINs (Days 5, 6, 30)                                                                                                            |
| FastAPI                                        | ✅ REST APIs, request/response models, DI, routers, status codes, validation (Days 10–14)                                                                                          |
| Docker                                         | ✅ Fundamentals → Dockerizing FastAPI → Compose → health checks → networking → reproducible deployment (Days 23–29)                                                                |
| Testing                                        | ⚠️ Not explicitly covered as a dedicated day in the 30-day log — **flag for Month 2 planning** against the original 12-week roadmap's "Testing" deliverable                        |
| System Design                                  | ⚠️ Not yet formally introduced — scheduled per `02_Roadmap.md` for Phase 2/4 (Months 4+ / 10–12)                                                                                   |
| LLM Fundamentals / RAG / Vector DB / AI Agents | ⏳ Scheduled to begin Month 2 (Weeks 5–8+) per both `02_Roadmap.md` Phase 1 weeks 5–12 and `README.md` Phase 2                                                                     |
| Cloud Deployment (AWS/Azure cert)              | ⏳ Coursework was scheduled to run in parallel from Week 1 per `02_Roadmap.md` — worth confirming actual progress against the ~25%-by-Week-4 / ~60–70%-by-Week-8 checkpoints       |
| Linux                                          | ⚠️ Not explicitly covered as a dedicated topic in the Engineering Handbook — implicitly touched via Docker CLI/container shell usage, but worth a deliberate pass if gaps are felt |
| DSA                                            | ⚠️ Not covered in the Engineering Handbook proper (Mentor Rules calls for ~2 LeetCode problems/week as a separate parallel track, not part of the daily handbook)                  |

**Portfolio status**: The **Student Management System** is the flagship Month-1 project — evolved from a Python CLI script (Day 1–4) through raw SQL/PostgreSQL (Day 7–9), into a JWT-authenticated, middleware-instrumented, logged, exception-handled, config-driven, transaction-safe, connection-pooled, indexed, and fully Dockerized/Compose-deployed REST API (Day 10–29), with advanced relational querying (Day 30). This is genuinely a strong, coherent, demo-able Project 1 for the resume/portfolio work called for in `MASTER_CONTEXT.md` Section 6B(6) and `02_Roadmap.md` Phase 1 — worth packaging with a clean README, architecture diagram, and a short demo GIF/video sooner rather than later, in parallel with Month 2's RAG/agentic work.

---

_End of Month 01 Revision. Generated from `00_Master_Month01_completed.zip` and `01_Engineering_Handbook_Month01_Completed.zip`._
