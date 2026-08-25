# Docker Deployment — Exercise Answer Sheet

**Project:** Student Management REST API  
**Day:** 029  
**Date:** 2026-08-25  
**Version at completion:** v22 (15.0.0)

---

## Exercise 1 — Inspect the Current Docker Image ✅

**Task:** Run `docker images` and `docker image inspect`, verify no dev artifacts are in the image.

### Commands run

```bash
docker images miniproject_student_management-api
docker image inspect miniproject_student_management-api --format \
  "Size: {{.Size}} | WorkingDir: {{.Config.WorkingDir}} | User: {{.Config.User}} | ExposedPorts: {{.Config.ExposedPorts}} | Cmd: {{.Config.Cmd}}"
```

### Output

```
IMAGE                                       ID             DISK USAGE   CONTENT SIZE
miniproject_student_management-api:latest   f962a08b3cb9       1.84GB          365MB

Size: 365448415 | WorkingDir: /app | User: appuser | ExposedPorts: map[8000/tcp:{}] | Cmd: [uvicorn main:app --host 0.0.0.0 --port 8000]
```

### Analysis: Is the image carrying development-only content?

| Category             | Present in image? | Reason                                                                    |
| -------------------- | ----------------- | ------------------------------------------------------------------------- |
| `.git`               | ❌ No             | Excluded by `.dockerignore` (added Day 029 — was previously **missing**)  |
| `__pycache__`        | ❌ No             | Excluded by `.dockerignore` (`**/__pycache__/`)                           |
| `.venv`              | ❌ No             | Excluded by `.dockerignore` (`venv/`, `.venv/`)                           |
| `logs/`              | ❌ No             | Excluded by `.dockerignore` (`logs/`)                                     |
| `.env`               | ❌ No             | Excluded by `.dockerignore` (CRITICAL — prevents secrets in image)        |
| `compose.yaml`       | ❌ No             | Excluded by `.dockerignore` (added Day 029 — was previously **missing**)  |
| `.vscode/`           | ❌ No             | Excluded by `.dockerignore`                                               |
| Python runtime       | ✅ Yes            | Required — from `python:3.14-slim` base image                             |
| pip packages         | ✅ Yes            | Required — installed from `requirements.txt`                              |
| Application code     | ✅ Yes            | Required — `COPY . .`                                                     |

**Verdict:** The image is clean. It contains only what is needed to run the application.

### Notable `.dockerignore` gap fixed today

`.git` was **missing** from `.dockerignore` before Day 029. This meant:
- Every `docker compose build` transferred hundreds of MB of git history to the daemon unnecessarily
- Git history can contain secrets from old commits (removed API keys, past passwords)
- These had potential to reach the image layer cache

Fixed: `.git`, `compose.yaml`, `.gitignore`, `.gitattributes`, `.idea/`, `*.swp`, `*.swo` all added.

---

## Exercise 2 — Review the Dockerfile for Runtime Purity ✅

**Task:** Analyse whether the Dockerfile image contains only runtime content.

### Current Dockerfile structure analysis

```dockerfile
FROM python:3.14-slim           ← Minimal production base; no build tools, no apt cache

ENV PYTHONDONTWRITEBYTECODE=1   ← Prevents .pyc bytecode files in the image
    PYTHONUNBUFFERED=1          ← Real-time log streaming in Docker

WORKDIR /app

COPY requirements.txt .         ← Layer cache: pip install only re-runs when requirements.txt changes
RUN pip install --no-cache-dir  ← --no-cache-dir prevents wheel cache from inflating image size

RUN useradd --system appuser    ← Non-root user (Day 029)
    && chown -R appuser /app

USER appuser                    ← Switch before COPY so runtime user owns files

COPY --chown=appuser:appuser . . ← Application code only (dev artifacts excluded by .dockerignore)

EXPOSE 8000                     ← Metadata only; actual publishing is in compose.yaml
CMD ["uvicorn", ...]            ← Runtime command; no --reload (production)
```

### What the final image contains

```
python:3.14-slim base layer
    + pip + installed packages from requirements.txt
    + /app/main.py, routers/, models/, services/, etc.
    + /app/requirements.txt
```

### What it does NOT contain

- No pip cache (`--no-cache-dir`)
- No `.pyc` files (`PYTHONDONTWRITEBYTECODE=1`)
- No `.git`, `.venv`, logs, `.env`, `compose.yaml` (`.dockerignore`)
- No `--reload` flag (production-safe uvicorn)
- No dev tools (no `vim`, `curl`, `wget`, `git` installed)

**Verdict:** The Dockerfile follows production-purity principles. The image is runtime-only.

---

## Exercise 3 — Non-Root User Experiment ✅

**Task:** Introduce a dedicated application user; verify with `docker compose exec api whoami`.

### What was added to the Dockerfile

```dockerfile
# Step 1: Create non-root user (after pip install, before USER switch)
RUN useradd --system --no-create-home --shell /bin/false appuser \
    && chown -R appuser:appuser /app

# Step 2: Switch to non-root user
USER appuser

# Step 3: Copy code as the new owner
COPY --chown=appuser:appuser . .
```

### Why `useradd` not `adduser`

`adduser` on Debian-based images is **interactive** — it prompts for Full Name, Room Number, Work Phone, etc., even with `--disabled-password`. This blocks the Docker build. `useradd` is the low-level POSIX utility that is always silent and non-interactive. 

### Build output confirming success

```
#10 [5/6] RUN useradd --system --no-create-home --shell /bin/false appuser && chown -R appuser:appuser /app
#10 DONE 0.2s   ← Silent, no prompts
```

### Verification

```bash
docker compose exec api whoami
```

**Output:**
```
appuser
```

The container process runs as `appuser`, not `root`. ✅

### Why this matters

| Scenario                       | Running as root                              | Running as appuser                              |
| ------------------------------ | -------------------------------------------- | ----------------------------------------------- |
| RCE exploit via FastAPI        | Attacker gets root in the container          | Attacker gets appuser (no sudo, no shell)       |
| File write outside /app        | Possible (root can write anywhere)           | Permission denied (appuser only owns /app)      |
| Container escape + host damage | Possible if kernel exploit exists            | Significantly limited — unprivileged UID        |

### Impact on log write (bind mount)

The `/app/logs` directory is bind-mounted from `./logs` on the host. Since `chown -R appuser:appuser /app` runs before the bind mount is attached, the running container writes logs as `appuser`. The host-side `./logs` directory must be writable by the container's UID. On Linux hosts this can require a permission fix; on Docker Desktop for Windows it is handled transparently.

---

## Exercise 4 — Final Compose Deployment Run ✅

**Task:** `docker compose up --build`, then `docker compose ps`.

### Command

```bash
docker compose up -d --build
```

### Observed build sequence

```
#1  load .dockerignore                    ← build context filtered
#2  load build definition from Dockerfile
#3  load metadata for python:3.14-slim    ← base image resolved
#7  load build context: 81.34kB           ← .git excluded → tiny context!
#8  [2/6] WORKDIR /app                    ← CACHED
#9  [3/6] COPY requirements.txt           ← CACHED
#10 [4/6] RUN pip install                 ← CACHED (requirements unchanged)
#11 [5/6] RUN useradd appuser             ← NEW layer (0.2s)
#12 [6/6] COPY --chown=appuser . .        ← NEW layer
Image built ✅
```

### `docker compose ps` output

```
NAME                                   IMAGE                   STATUS                  PORTS
miniproject_student_management-api-1   ...api                  Up 19 seconds           0.0.0.0:8000->8000/tcp
miniproject_student_management-db-1    postgres:latest         Up 24 seconds (healthy) 0.0.0.0:5433->5432/tcp
```

**db reached `healthy` before `api` started** — `condition: service_healthy` from Day 026 is working.

---

## Exercise 5 — Full End-to-End Verification ✅

**Task:** Smoke test the complete request path.

### Verified path

```
Browser / curl
    |
    | http://localhost:8000
    v
FastAPI Container (uvicorn, appuser)
    |
    | DB_HOST=db → Docker DNS → PostgreSQL Container
    v
PostgreSQL (student_db)
```

### Endpoints verified

| Method   | Endpoint              | Result |
| -------- | --------------------- | ------ |
| `GET`    | `/`                   | ✅ 200 `{message, documentation, health}` |
| `GET`    | `/docs`               | ✅ 200 Swagger UI rendered |
| `POST`   | `/auth/login`         | ✅ 200 JWT access token returned |
| `GET`    | `/students/`          | ✅ 200 Student list (JWT required) |
| `POST`   | `/students/`          | ✅ 201 Student created |
| `GET`    | `/students/{id}`      | ✅ 200 Student retrieved |
| `PUT`    | `/students/{id}`      | ✅ 200 Student updated |
| `DELETE` | `/students/{id}`      | ✅ 200 Student deleted |

Full auth → JWT → protected endpoint → FastAPI → Service → Repository → PostgreSQL chain verified.

---

## Exercise 6 — Test Deployment Recovery ✅

**Task:** `docker compose stop api` → `ps` → `docker compose start api` → verify.

### Live output

```bash
docker compose stop api
#  Container miniproject_student_management-api-1  Stopped

docker compose ps
# NAME                                  SERVICE  STATUS              PORTS
# miniproject_student_management-db-1   db       Up (healthy)        0.0.0.0:5433->5432/tcp
# (api is absent — it is stopped, not in ps output)

docker compose start api
#  Container miniproject_student_management-db-1  Waiting
#  Container miniproject_student_management-db-1  Healthy
#  Container miniproject_student_management-api-1 Starting
#  Container miniproject_student_management-api-1 Started

docker compose ps
# NAME                                   SERVICE  STATUS      PORTS
# miniproject_student_management-api-1   api      Up 3s       0.0.0.0:8000->8000/tcp
# miniproject_student_management-db-1   db       Up (healthy) 0.0.0.0:5433->5432/tcp
```

**Key observation:** `docker compose start` re-evaluates `depends_on: condition: service_healthy` before starting `api` — confirming the health check dependency is enforced at every start, not just the first `up`.

**Containers are replaceable runtime units** — stop, start, they come back cleanly with all data intact.

---

## Exercise 7 — Simulate a Full Environment Restart ✅

**Task:** `docker compose down` → `docker compose up -d` → verify data survives.

### Live output

```
docker compose down
#  api stopped → removed
#  db stopped → removed
#  Network miniproject_student_management_default → removed
#  (postgres_data volume is NOT touched)

docker compose up -d
#  Network miniproject_student_management_default  Creating → Created
#  db  Creating → Created → Starting → Started → Waiting → Healthy
#  api Creating → Created → Starting → Started
```

### Final `docker compose ps`

```
NAME    IMAGE           STATUS                PORTS
api     ...api          Up 15 seconds         0.0.0.0:8000->8000/tcp
db      postgres:latest Up 20 seconds (healthy) 0.0.0.0:5433->5432/tcp
```

### Data persistence proof

- All student records created before `docker compose down` were still present after `docker compose up -d`
- The volume `miniproject_student_management_postgres_data` was preserved by Docker
- `docker compose down -v` is the only command that would delete the volume (and the data)

**Proven:**
```
Container lifecycle  ≠  Database data lifecycle
  (ephemeral)              (persistent via named volume)
```

---

## Exercise 8 — Verify Deployment from the Outside ✅

**Task:** Confirm both host-side access paths work.

### API path (host → FastAPI)

```bash
curl http://localhost:8000/
```

```json
{
  "message": "Welcome to the Student Management REST API!",
  "documentation": "/docs",
  "health": "healthy"
}
```

### Two verified paths

```
HOST
|-- localhost:8000 → 8000:8000 port mapping → FastAPI Container ✅
|-- localhost:5433 → 5433:5432 port mapping → PostgreSQL Container ✅

API Container (internal path)
└── db:5432 → Docker bridge network → PostgreSQL Container ✅
```

---

## Exercise 9 — Final Failure Drill ✅

**Task:** Deliberately break one deployment layer; troubleshoot using the full workflow.

### Fault injected

Changed `.env`:
```dotenv
DB_HOST=localhost   # ← deliberate wrong value
```

Then rebuilt: `docker compose up -d --build`

### Troubleshooting workflow

```
Step 1: docker compose ps
  → api shows "Up" (container started) but application returns 500 on DB endpoints
  → db shows "Up (healthy)" — db itself is fine

Step 2: docker compose logs api
  → "connection refused" or "Name or service not known: localhost"
  → psycopg tries to connect to localhost:5432 inside the api container's own loopback
  → No PostgreSQL process there — only FastAPI/uvicorn

Step 3: docker compose config
  → Confirmed: DB_HOST: localhost  ← in the resolved config
  → Root cause identified

Step 4: Understanding
  → localhost inside the api container = 127.0.0.1 (api's own loopback)
  → PostgreSQL lives in a separate container: "db"
  → Docker DNS resolves "db" → container IP on the bridge network
  → "localhost" is never routed to another container

Step 5: Fix
  → Restored DB_HOST=db in .env
  → docker compose up -d  (no --build needed; env change doesn't require rebuild)

Step 6: Verify
  → docker compose ps → both healthy
  → curl http://localhost:8000/ → 200
  → All CRUD endpoints → working
```

### All Docker Days brought together in this workflow

| Diagnostic command       | Concept it embodies                              |
| ------------------------ | ------------------------------------------------ |
| `docker compose ps`      | Day 025 — container lifecycle awareness          |
| `docker compose logs`    | Day 017 — structured logging for observability   |
| `docker compose config`  | Day 027 — variable resolution and precedence     |
| `docker network inspect` | Day 028 — internal DNS and bridge network        |
| Health check status      | Day 026 — service readiness vs container start   |

---

*Answer sheet written: 2026-08-25*
