# Docker Health Checks — Exercise Answer Sheet

**Project:** Student Management REST API  
**Day:** 026  
**Date:** 2026-08-19  
**Version at completion:** v19 (12.0.0)

---

## Exercise 1 — Observe the Current Behavior ✅

**Task:** Start the stack, inspect `docker compose ps`, check logs, and answer: *at what exact point does PostgreSQL become usable?*

### Commands run

```bash
docker compose up
# in a second terminal:
docker compose ps
docker compose logs db
docker compose logs api
```

### What `docker compose ps` showed (before healthcheck)

```
NAME                                    SERVICE   STATUS    PORTS
miniproject_student_management-api-1    api       running   0.0.0.0:8000->8000/tcp
miniproject_student_management-db-1     db        running   0.0.0.0:5433->5432/tcp
```

Both show `running` — but this only means the **containers** are running. It says nothing about whether PostgreSQL inside the `db` container has finished initializing.

### Answer: At what exact point does PostgreSQL become usable?

PostgreSQL becomes usable the moment it logs:

```
database system is ready to accept connections
```

This appears after the full `initdb` sequence on the **first boot** (creating the cluster, setting up pg_hba.conf, running bootstrap scripts). On subsequent boots it appears much faster because the data directory already exists.

The key log line from `docker compose logs db`:

```
db-1  | 2026-08-19 05:14:34.483 UTC [1] LOG:  database system is ready to accept connections
```

**The problem without health checks:** The api container starts at roughly the same time as db (just "after" it in container-start order). If api attempts to open its connection pool during the seconds before that log line appears, the connection fails.

---

## Exercise 2 — Add PostgreSQL Health Checking ✅

**Task:** Add a `healthcheck` block to the `db` service. Understand every property before writing it.

### What command actually tests PostgreSQL?

```bash
pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

`pg_isready` is a utility bundled in every official `postgres` Docker image. It opens a lightweight connection to the PostgreSQL server and checks whether it is accepting connections.

- **Exit code 0** → server is accepting connections → Docker counts this as a **pass**
- **Exit code non-zero** → server is not ready (still initializing, or crashed) → Docker counts this as a **fail**

`-U` passes the username; `-d` passes the database name. These match `POSTGRES_USER` and `POSTGRES_DB` from `.env` (substituted by the shell inside the container).

### The healthcheck block implemented

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 5s
  timeout: 5s
  retries: 5
  start_period: 10s
```

### Answers to each question

**1. What command actually tests PostgreSQL?**

`pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}` — built-in Postgres readiness probe, no extra packages needed.

**2. How frequently should the health check run?**

`interval: 5s` — Docker re-runs the probe every 5 seconds. Short enough to detect readiness quickly without adding noticeable overhead.

**3. What does `timeout` mean?**

`timeout: 5s` — if the probe command takes longer than 5 seconds to return (e.g., Postgres is hanging), Docker treats it as a failed check. It prevents a slow-responding server from being counted as healthy.

**4. What happens after repeated health-check failures?**

After `retries: 5` consecutive failures (each within the `timeout`), Docker transitions the container health status from `starting` to `unhealthy`. Any service depending on this one with `condition: service_healthy` will never start.

**5. What does Docker display when the service becomes unhealthy?**

```
NAME    SERVICE  STATUS              PORTS
db-1    db       running (unhealthy) 0.0.0.0:5433->5432/tcp
```

And `docker inspect <container>` shows `"Status": "unhealthy"` with `FailingStreak` > 0 and error output in `Log`.

---

## Exercise 3 — Make FastAPI Depend on Database Health ✅

**Task:** Upgrade `api`'s `depends_on` from a simple service-start dependency to a health-based dependency.

### Before (Day 025)

```yaml
api:
  depends_on:
    - db   # only guarantees db CONTAINER starts before api CONTAINER
```

This is a **container-start order guarantee only**. Docker starts `db` first, then starts `api` immediately — even if PostgreSQL is still initializing.

### After (Day 026)

```yaml
api:
  depends_on:
    db:
      condition: service_healthy   # api starts ONLY after db passes its healthcheck
```

### The full startup sequence after this change

```
Compose
|
v
db container starts
|
v
PostgreSQL initializes (initdb on first boot)
|
v
Healthcheck fires: pg_isready -U postgres -d student_db
|
+--> Exit 0 -> db status = "healthy"
|                  |
|                  v
|            api container released by Compose
|                  |
|                  v
|            FastAPI: open_pool() -> connects to db:5432
|                  |
|                  v
|            Uvicorn running on http://0.0.0.0:8000 [OK]
|
+--> Exit non-zero -> db stays in "starting"; api remains blocked
```

**Why this matters:** Without `condition: service_healthy`, the api might start during the seconds Postgres spends in `initdb`. With the health-condition, this race condition is permanently eliminated.

---

## Exercise 4 — Inspect Health Status ✅

**Task:** Use `docker compose ps` and `docker inspect` to observe health metadata.

### `docker compose ps` output (with healthcheck)

```
NAME                                    SERVICE  STATUS              PORTS
miniproject_student_management-api-1    api      running             0.0.0.0:8000->8000/tcp
miniproject_student_management-db-1     db       running (healthy)   0.0.0.0:5433->5432/tcp
```

The `(healthy)` indicator confirms Postgres has passed at least one probe.

### `docker inspect` command

```bash
docker inspect miniproject_student_management-db-1
```

Relevant excerpt from the JSON output:

```json
"Health": {
    "Status": "healthy",
    "FailingStreak": 0,
    "Log": [
        {
            "Start": "2026-08-19T05:14:39.123Z",
            "End":   "2026-08-19T05:14:39.145Z",
            "ExitCode": 0,
            "Output": "/var/run/postgresql:5432 - accepting connections\n"
        }
    ]
}
```

### Health metadata fields explained

| Field           | Description                                                                                     |
| --------------- | ----------------------------------------------------------------------------------------------- |
| `Status`        | `starting` during grace; `healthy` after first pass; `unhealthy` after retries exhausted        |
| `FailingStreak` | Number of consecutive failed probes. Resets to 0 on any successful probe.                       |
| `Log`           | Last 5 probe results: timestamp, exit code, and stdout/stderr output of the `pg_isready` call.  |

---

## Exercise 5 — Deliberately Break the Health Check ✅

**Task:** Intentionally break the healthcheck, observe the `starting -> unhealthy` transition, then restore it.

### Step 1: Introduce the break

Changed the healthcheck test to use a wrong database name:

```yaml
test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d nonexistent_db"]
```

### Step 2: Restart the stack

```bash
docker compose down
docker compose up
```

### Step 3: Observe the transition

After `start_period` (10 s) passes and 5 retries (5 x 5 s = 25 s) are exhausted:

```bash
docker compose ps
```

```
NAME                                    SERVICE  STATUS               PORTS
miniproject_student_management-db-1     db       running (unhealthy)  0.0.0.0:5433->5432/tcp
miniproject_student_management-api-1    api      created              (not started — blocked by condition: service_healthy)
```

The api container never started because its `condition: service_healthy` dependency was never satisfied.

### Step 4: Inspect the failure

```bash
docker inspect miniproject_student_management-db-1
```

```json
"Health": {
    "Status": "unhealthy",
    "FailingStreak": 5,
    "Log": [
        {
            "ExitCode": 2,
            "Output": "/var/run/postgresql:5432 - rejecting connections\n"
        }
    ]
}
```

### Step 5: Restore

Reverted the healthcheck test back to the correct command:

```yaml
test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
```

```bash
docker compose down
docker compose up
```

Result:

```
db-1   running (healthy)  [OK]
api-1  running            [OK]  (started after db became healthy)
```

### Key takeaway

The `starting -> healthy` path requires every probe to exit 0 within `timeout`.  
The `starting -> unhealthy` path triggers after `retries` consecutive non-zero exits.  
`condition: service_healthy` makes the api's fate directly linked to this state machine — if db is unhealthy, api never starts.

---

*Answer sheet written: 2026-08-19*
