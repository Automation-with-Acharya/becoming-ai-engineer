# Docker Compose Configuration — Exercise Answer Sheet

**Project:** Student Management REST API  
**Day:** 027  
**Date:** 2026-08-21  
**Version at completion:** v20 (13.0.0)

---

## Exercise 1 — Inspect the Resolved Compose Configuration ✅

**Task:** Run `docker compose config` and understand what Compose resolves.

### Command

```bash
docker compose config
```

### What this command does

`docker compose config` reads `compose.yaml` and the `.env` file, substitutes all `${VAR}` placeholders with their resolved values, and prints the fully-expanded YAML. No containers are started.

**Resolution flow:**

```
compose.yaml
    + .env
    + ${VAR} interpolation
        |
        v
docker compose config
        |
        v
Resolved configuration (printed to stdout)
```

### Actual resolved output (excerpt)

```yaml
name: miniproject_student_management
services:
  api:
    environment:
      APP_NAME: Student Management REST API
      APP_VERSION: 13.0.0
      DB_HOST: db
      DB_NAME: student_db
      DB_PASSWORD: password@postgres
      DB_POOL_MAX_SIZE: "5"
      DB_POOL_MIN_SIZE: "1"
      DB_PORT: "5432"
      DB_USER: postgres
      DEBUG: "false"
      JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "30"
      JWT_ALGORITHM: HS256
      JWT_SECRET_KEY: day019-env-secret-key-change-this-in-production
      LOG_LEVEL: INFO
    restart: on-failure
    ...
  db:
    healthcheck:
      test:
        - CMD-SHELL
        - pg_isready -U postgres -d student_db
      timeout: 5s
      interval: 5s
      retries: 5
      start_period: 10s
    image: postgres:latest
    ...
networks:
  default:
    name: miniproject_student_management_default
volumes:
  postgres_data:
    name: miniproject_student_management_postgres_data
```

### Key observations

- All `${VAR}` placeholders are fully substituted with actual values.
- The project name (`miniproject_student_management`) is auto-derived from the directory name.
- Ports are shown in their expanded form (`mode: ingress`, `target`, `published`).
- The `healthcheck.test` array shows the resolved shell command with actual credential values.
- This output is the ground truth for what Docker will actually run — use it to audit before deployment.

---

## Exercise 2 — Move Configuration to Explicit Environment Variables ✅

**Task:** Refactor the Compose file so variables are supplied explicitly rather than only via `env_file`.

### Variable classification

| Variable                         | Category       | Reason                                                        |
| -------------------------------- | -------------- | ------------------------------------------------------------- |
| `DB_HOST`, `DB_PORT`, `DB_NAME`  | Infrastructure | Describes where the database lives; changes per environment   |
| `DB_USER`, `DB_PASSWORD`         | Secret         | Credentials — should never be hard-coded or logged            |
| `JWT_SECRET_KEY`                 | Secret         | Signing key — must be secret and long in production           |
| `APP_NAME`, `APP_VERSION`        | App config     | Metadata; changes with each release                           |
| `DEBUG`, `LOG_LEVEL`             | App config     | Behaviour toggles; differ between dev and prod                |
| `DB_POOL_MIN_SIZE/MAX_SIZE`      | App config     | Tuning parameters; may need per-environment adjustment        |
| `JWT_ALGORITHM`, `JWT_*_MINUTES` | App config     | Security configuration; usually stable but should be explicit |

### Implemented solution

Added an explicit `environment:` block to the `api` service alongside the existing `env_file`:

```yaml
api:
  env_file:
    - .env # bulk-load all vars as container defaults
  environment:
    APP_NAME: ${APP_NAME} # ${VAR} filled by Compose from .env at project level
    APP_VERSION: ${APP_VERSION}
    DEBUG: ${DEBUG}
    JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    JWT_ALGORITHM: ${JWT_ALGORITHM}
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: ${JWT_ACCESS_TOKEN_EXPIRE_MINUTES}
    DB_HOST: ${DB_HOST}
    DB_PORT: ${DB_PORT}
    DB_NAME: ${DB_NAME}
    DB_USER: ${DB_USER}
    DB_PASSWORD: ${DB_PASSWORD}
    DB_POOL_MIN_SIZE: ${DB_POOL_MIN_SIZE}
    DB_POOL_MAX_SIZE: ${DB_POOL_MAX_SIZE}
    LOG_LEVEL: ${LOG_LEVEL}
```

### Why keep both `env_file` AND `environment`?

- `env_file` bulk-loads every variable from `.env` — so nothing is accidentally missed.
- `environment` makes specific variables **visible** in `compose.yaml` and individually **overridable** without editing `.env`.

For example, to enable debug logging for a single dev run without changing `.env`:

```bash
LOG_LEVEL=DEBUG docker compose up
```

Or temporarily override in `compose.yaml` itself:

```yaml
environment:
  LOG_LEVEL: DEBUG # overrides env_file value
```

---

## Exercise 3 — Use `.env` and `env_file` Deliberately ✅

**Task:** Understand that Compose interpolation and container environment injection are related but different.

### The distinction

| Mechanism          | Who reads it          | What it does                                                              |
| ------------------ | --------------------- | ------------------------------------------------------------------------- |
| `.env` (project)   | **Compose itself**    | Fills `${VAR}` placeholders in `compose.yaml` at parse time               |
| `env_file: .env`   | **Container runtime** | Injects all key=value pairs as environment variables inside the container |
| `environment:` key | **Container runtime** | Injects a specific variable (can use `${VAR}` which Compose fills first)  |

### The same `.env` file serves two purposes

In this project, `.env` is used for BOTH:

1. **Compose interpolation** — When Compose reads `compose.yaml`, it loads `.env` automatically from the project directory and substitutes `${POSTGRES_USER}` in the healthcheck command, `${DB_HOST}` in the environment block, etc.

2. **Container env injection** — `env_file: .env` injects every variable in `.env` into the container's environment at runtime.

This is intentional and practical for a single-environment project. For multi-environment setups, you might separate:

```
.env          ← Compose-level interpolation only (project variables, image tags, port numbers)
.env.dev      ← container env for development (LOG_LEVEL=DEBUG, DEBUG=true)
.env.prod     ← container env for production (LOG_LEVEL=WARNING, DEBUG=false)
```

**This project does not split files** because it is a learning project with one environment. The important insight is that the two uses are conceptually different even when physically the same file.

---

## Exercise 4 — Environment Precedence Experiment ✅

**Task:** Define the same variable in `.env` AND in the `environment:` block; observe which wins.

### Experiment setup

`.env` has:

```dotenv
DEBUG=false
```

Temporarily changed `compose.yaml` `environment:` block to:

```yaml
environment:
  DEBUG: "true" # overrides env_file
```

### Result from `docker compose config`

```yaml
environment:
  DEBUG: "true" # ← environment: block value wins
```

### Result from `docker compose run --rm api env | grep DEBUG`

```
DEBUG=true
```

The container receives `DEBUG=true` — the `environment:` block value, NOT `false` from `.env`.

### Precedence table (highest to lowest inside a container)

```
1. environment: key in compose.yaml          ← WINS
       |
2. env_file: listed in compose.yaml
       |
3. ENV instruction in Dockerfile
       |
4. Image built-in default
```

### After the experiment

Restored `compose.yaml` to:

```yaml
environment:
  DEBUG: ${DEBUG} # reads from .env → false
```

### Key insight

Compose does not simply "merge" environment sources randomly. It resolves them in a deterministic order. The `environment:` block is the **highest-precedence per-service override** — useful for tuning a specific service in a specific deployment without touching the shared `.env` file.

---

## Exercise 5 — Add a Restart Policy ✅

**Task:** Add `restart: on-failure` to the `api`, observe the automatic restart lifecycle.

### What was added to `compose.yaml`

```yaml
api:
  restart: on-failure # restart container if it exits with a non-zero code
```

### Restart policy options

| Policy           | Behaviour                                                              |
| ---------------- | ---------------------------------------------------------------------- |
| `no`             | Never restart (default)                                                |
| `always`         | Always restart regardless of exit code                                 |
| `on-failure`     | Restart only on non-zero exit; does NOT restart on clean stop (exit 0) |
| `unless-stopped` | Always restart unless explicitly stopped with `docker compose stop`    |

### `on-failure` chosen for this project because

- A FastAPI application that exits cleanly (e.g., `Ctrl+C`) should **not** loop forever.
- A crash (OOM kill, unhandled exception, bad DB connection at startup) **should** be recovered automatically.
- `always` would cause the container to keep restarting even after an intentional `docker compose stop`, which is confusing.

### Expected lifecycle

```
Application crashes (non-zero exit)
        |
        v
Docker sees non-zero exit code
        |
        v
restart: on-failure triggers
        |
        v
Container restarted (with exponential backoff after repeated failures)
        |
        v
FastAPI starts again
```

### Verification

```bash
docker compose ps
```

During restart loop: `STATUS` shows `restarting`  
After successful restart: `STATUS` shows `running`

```bash
docker compose logs api
```

Shows multiple startup log sequences, confirming restarts occurred.

---

## Exercise 6 — Development vs. Production ✅

**Task:** Understand why a source-code bind mount is useful in development but undesirable in production.

### Development workflow

```
Host source code (edited in IDE)
        |
        v
Bind mount (./:/app)
        |
        v
Container sees changes immediately
        |
        v
Uvicorn hot-reload picks up the change
        |
        v
No rebuild needed
```

**Why useful in dev:** The round-trip of `docker compose up --build` takes seconds. A bind mount lets code changes reflect instantly, preserving the rapid feedback loop expected during development.

### Production workflow

```
Source code
  |
  v
docker compose build (or CI pipeline)
  |
  v
Immutable image (code baked in)
  |
  v
Container
```

**Why undesirable in prod:**

| Risk                | Explanation                                                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------- |
| **Mutability**      | If host code changes (accidentally or via an attacker), the container behaviour changes instantly    |
| **Reproducibility** | Two containers from the same image can behave differently if they bind-mount different host dirs     |
| **Portability**     | Bind mounts depend on the exact host path; the same `compose.yaml` fails on a host without that path |
| **Security**        | A bind mount exposes the host filesystem path to the container (privilege escalation risk)           |

### What this project does

This project uses **no source-code bind mount** — only a logs bind mount (`./logs:/app/logs`).

The logs mount is acceptable in both dev and prod because:

- It only exposes the `logs/` directory, not the full source tree.
- Log persistence is a valid operational need (logs survive container restarts).
- The directory is written by the app, not read for execution.

---

## Exercise 7 — Compose Architecture Review ✅

**Task:** Mentally organize the complete Compose architecture as it stands after Day 027.

### Architecture diagram

```
                    compose.yaml
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Services       Networks       Volumes
          |               |              |
     +----+----+     [default]    [postgres_data]
     v         v
    api        db
     |          |
     |          +---- image: postgres:latest
     |          +---- env_file: .env (POSTGRES_*)
     |          +---- volume: postgres_data:/var/lib/postgresql
     |          +---- healthcheck: pg_isready every 5s
     |
     +---- build: . (local Dockerfile)
     +---- env_file: .env (all vars as defaults)
     +---- environment: ${VAR} explicit listing (overridable)
     +---- ports: 8000:8000
     +---- volumes: ./logs:/app/logs
     +---- restart: on-failure
     +---- depends_on: db (condition: service_healthy)
```

### Configuration concerns covered

| Concern                | Implementation                                                                   |
| ---------------------- | -------------------------------------------------------------------------------- |
| **Configuration**      | `env_file: .env` + `environment: ${VAR}` block; `docker compose config` to audit |
| **Health checks**      | `pg_isready` probe on db; `condition: service_healthy` on api                    |
| **Restart behavior**   | `restart: on-failure` on api                                                     |
| **Persistent storage** | Named volume `postgres_data` for PostgreSQL data                                 |
| **Networking**         | Compose default bridge network; service-name DNS resolves `db`                   |
| **Log persistence**    | Bind mount `./logs:/app/logs`                                                    |

This is a real, production-oriented deployment configuration — not just a Docker tutorial exercise.

---

_Answer sheet written: 2026-08-21_
