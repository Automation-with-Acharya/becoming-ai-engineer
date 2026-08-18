# Docker Compose — Exercise Answer Sheet

**Project:** Student Management REST API  
**Day:** 025  
**Date:** 2026-08-18  
**Version at completion:** v18 (11.0.0)

---

## Exercise 1 — Create the Compose File ✅

**Task:** Turn the empty `compose.yaml` placeholder into a real Compose configuration starting with only `api` (build) and `db` (postgres image).

**Answer:**

The minimal starting structure that was implemented first:

```
services
│
├── api
│   └── build: .          ← tells Compose to build from the local Dockerfile
│
└── db
    └── image: postgres   ← tells Compose to pull the official postgres image
```

**Understanding the structure:**

- `services:` is the top-level key. Every container is declared as a named entry under `services:`.
- `api:` — the service name. This also becomes the hostname that other services can use to reach this container inside the Compose network.
- `build: .` — Compose builds the Docker image from the `Dockerfile` in the current directory (`.`). No pre-built image is needed.
- `db:` — second service. Unlike `api`, this uses a pre-built image from Docker Hub.
- `image: postgres:latest` — Docker pulls this image automatically if not cached locally.

> **Key insight:** The service name is not just a label. Docker Compose's internal DNS resolver maps it to the container's IP. So `api` can connect to `db` using the hostname `"db"` — this is what enables `DB_HOST=db`.

---

## Exercise 2 — Create the PostgreSQL Container Properly ✅

**Task:** Configure the `db` service with database name, username, password, and a persistent volume.

**Answer:**

The final `db` service configuration (with `env_file` to avoid hard-coding secrets):

```yaml
db:
  image: postgres:latest
  env_file:
    - .env                  # POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD loaded from here
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

The `.env` file holds the corresponding values:

```env
POSTGRES_DB=student_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password@postgres
```

**Why these three variables?**

The official `postgres` Docker image reads exactly these three `POSTGRES_*` environment variables **on its very first startup** to:
1. Create a database named `POSTGRES_DB`.
2. Create a superuser named `POSTGRES_USER`.
3. Set the superuser password to `POSTGRES_PASSWORD`.

**Why a named volume — and why `/var/lib/postgresql`, not `/var/lib/postgresql/data`?**

```yaml
volumes:
  - postgres_data:/var/lib/postgresql
```

PostgreSQL stores all data files inside the container. Without a volume, those files are ephemeral — `docker compose down` erases everything. A named volume (`postgres_data`) is managed by Docker and survives container removal.

> ⚠️ **PostgreSQL 18+ volume path change:** `postgres:latest` now pulls PostgreSQL 18, which changed the data directory layout. In v18+, data lives at `/var/lib/postgresql/18/docker` (a major-version subdirectory). Mounting at the old path `/var/lib/postgresql/data` causes the container to crash with:
>
> ```
> Error: in 18+, these Docker images are configured to store database data in a
> format which is compatible with "pg_ctlcluster"
> ```
>
> The fix is to mount at `/var/lib/postgresql` (the parent), letting Postgres manage its own versioned subdirectory. This is also required for `pg_upgrade` compatibility.
>
> **Rule:** For `postgres:latest` (v18+) → mount at `/var/lib/postgresql`  
> **Rule:** For `postgres:17` or older → `/var/lib/postgresql/data` also works

> ⚠️ **Security note:** Real passwords should never be committed to version control. `.env` is in `.gitignore`. Only `.env.example` (with placeholder values) is committed.

---

## Exercise 3 — Fix the Database Configuration ✅

**Task:** Change `DB_HOST` from `host.docker.internal` to `db` and understand why.

**Answer:**

```env
# Before (Day 024 — FastAPI in container, Postgres on host machine):
DB_HOST=host.docker.internal

# After (Day 025 — both in Compose network):
DB_HOST=db
```

**Why `host.docker.internal` fails inside Compose:**

`host.docker.internal` is a special DNS name Docker for Desktop provides so containers can reach services on the **host machine**. It only works for host-to-container scenarios.

When PostgreSQL is running *inside* the same Compose stack, the FastAPI container needs to reach **another container**, not the host. In that case, Docker's built-in DNS resolver resolves service names within the Compose network.

**The complete flow:**

```
FastAPI Container  (service: api)
│
│  DB_HOST=db   ←── set in .env, loaded by Compose via env_file
▼
Docker Compose Internal DNS
│
│  Resolves "db" → 172.18.0.x  (Postgres container IP, assigned dynamically)
▼
PostgreSQL Container  (service: db)
│
▼
/var/lib/postgresql/data  (mounted from postgres_data volume)
```

> **Rule of thumb:** Use `localhost` when both processes share the same OS. Use the service name when they're in separate containers in the same Compose network. Use `host.docker.internal` only when targeting the host machine from a container.

---

## Exercise 4 — Start the Application with ONE Command ✅

**Task:** Run `docker compose up` and verify both services appear in `docker compose ps`.

**Command:**

```bash
docker compose up
```

Or to run in the background:

```bash
docker compose up -d
```

**Verify with:**

```bash
docker compose ps
```

**Expected output:**

```
NAME                              SERVICE   STATUS    PORTS
student_management-api-1          api       running   0.0.0.0:8000->8000/tcp
student_management-db-1           db        running   5432/tcp
```

**What happens internally when you run `docker compose up`:**

1. Compose reads `compose.yaml` and discovers two services: `api` and `db`.
2. Because `api` has `depends_on: db`, Compose starts `db` first.
3. Compose pulls `postgres:latest` if not cached, then starts the db container.
4. Postgres initializes using `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` from `.env`.
5. Compose builds the `api` image from the local `Dockerfile` (runs `pip install`, copies source).
6. Compose starts the `api` container, injecting all `.env` vars.
7. FastAPI's lifespan starts: `open_pool()` opens connections to `db:5432`, creates the `students` table if needed.
8. Both containers are now on a shared virtual bridge network (`student_management_default`).

---

## Exercise 5 — Verify the API ✅

**Task:** Open `http://localhost:8000/docs` and verify all endpoints work.

**Results:**

| Endpoint                      | Method   | Result |
| ----------------------------- | -------- | ------ |
| `/`                           | `GET`    | ✅ Root health check returns welcome message |
| `/students/`                  | `POST`   | ✅ Creates a new student record in the Compose Postgres container |
| `/students/`                  | `GET`    | ✅ Returns all students |
| `/students/{id}`              | `GET`    | ✅ Returns student by ID; 404 if not found |
| `/students/{id}`              | `PUT`    | ✅ Updates student by ID |
| `/students/{id}`              | `DELETE` | ✅ Deletes student by ID |
| `/students/search?query=name` | `GET`    | ✅ Case-insensitive search via ILIKE |
| `/auth/login`                 | `POST`   | ✅ Returns JWT token |
| `/auth/profile`               | `GET`    | ✅ Protected route works with Bearer token |

**Full architecture at this point:**

```
Browser
│
▼
localhost:8000
│
▼
FastAPI Container  (service: api)
│
▼
Middleware Layer  (request_middleware.py)
│
▼
Router Layer  (routers/students.py)
│
▼
Service Layer  (services/student_service.py)
│
▼
Repository Layer  (repositories/student_repository.py)
│
▼
Database Helper  (database/database_helper.py)
│
▼
Connection Pool  (psycopg_pool.ConnectionPool)
│
▼
PostgreSQL Container  (service: db)
│
▼
postgres_data volume  (persistent storage)
```

---

## Exercise 6 — Prove That Service-Name Networking Works ✅

**Task:** Break the configuration by changing `DB_HOST=db` to `DB_HOST=localhost`, observe the failure, then restore it.

### Step-by-step experiment

**Step 1: Change `.env`**
```env
DB_HOST=localhost   # intentionally wrong
```

**Step 2: Restart the stack**
```bash
docker compose down
docker compose up
```

**Step 3: Observe the failure**

The `api` container starts but immediately fails to connect to Postgres. FastAPI's lifespan `open_pool()` call raises a connection error.

**Step 4: Inspect logs**
```bash
docker compose logs api
```

**Error you'd see (typical output):**
```
psycopg_pool._pool.PoolTimeout: couldn't get a connection after 30.00 sec
  caused by: psycopg.OperationalError: connection to server at "localhost" (127.0.0.1),
  port 5432 failed: Connection refused
```

**Step 5: Why `DB_HOST=localhost` fails inside Docker**

`localhost` (or `127.0.0.1`) inside any container refers to the container's **own loopback interface** — not the host machine and not any other container. The FastAPI container has nothing listening on its own port 5432, so the connection is immediately refused.

```
FastAPI Container
│
│  Tries to connect to localhost:5432
▼
127.0.0.1:5432 (FastAPI container's own loopback)
│
▼
❌ Connection refused — nothing listening here
```

The Postgres container exists on a completely different network namespace. Without Docker DNS, the two containers cannot discover each other at all.

**Step 6: Restore**
```env
DB_HOST=db   # correct — resolves via Docker DNS
```

**Step 7: Restart and verify**
```bash
docker compose down
docker compose up
```

✅ API connects successfully. `docker compose logs api` shows pool opened and table created.

**Why this matters:**

This experiment makes the networking rule visceral:
- In the same process / same OS → use `localhost`
- In the same Compose network, different containers → use the **service name**
- Container reaching the host machine → use `host.docker.internal` (Docker Desktop) or `172.17.0.1` (Linux Docker)

---

## Exercise 7 — Essential Compose Commands ✅

**Task:** Be able to explain each command without looking them up.

### Basic Operations

| Command | What it does | When to use it |
|---------|-------------|----------------|
| `docker compose up` | Reads `compose.yaml`, builds any images that need building, creates and starts all containers in the foreground. Logs stream to your terminal. | During active development when you want to see all output. |
| `docker compose up -d` | Same as above but runs in **detached** (background) mode. Your terminal is freed immediately. | When you want the stack running while you work on something else. |
| `docker compose down` | Stops all running containers and removes them (and their default network). Named volumes are **preserved**. | When you want to stop the stack cleanly without losing data. |

### Monitoring

| Command | What it does |
|---------|-------------|
| `docker compose ps` | Lists all services defined in `compose.yaml`, their current status (running/stopped), and port mappings. |
| `docker compose logs` | Streams combined log output from all services to your terminal. |
| `docker compose logs api` | Streams logs from **only** the `api` service. Useful for isolating application errors from database noise. |

### Building

| Command | What it does | When to use it |
|---------|-------------|----------------|
| `docker compose build` | Builds (or rebuilds) all images that use `build:` in the Compose file, without starting any containers. | When you want to pre-build images in CI or verify your Dockerfile before running. |
| `docker compose up --build` | Rebuilds images **and then** starts all services. Equivalent to `docker compose build && docker compose up`. | After changing source code or `requirements.txt` — forces Docker to pick up the new code instead of using a cached layer. |

### Additional Useful Commands

| Command | What it does |
|---------|-------------|
| `docker compose down -v` | Stops and removes containers **and** deletes all named volumes. Use when you want a completely clean slate (⚠️ destroys all database data). |
| `docker compose exec api bash` | Opens an interactive shell inside the running `api` container. Useful for debugging or running management commands. |
| `docker compose restart api` | Restarts only the `api` service without stopping `db`. |

---

*Answer sheet written: 2026-08-18*
