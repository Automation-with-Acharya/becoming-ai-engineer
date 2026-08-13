# Docker — Learning Log & Troubleshooting Guide

## Issue 1 — Docker Desktop stuck on "Starting the Docker Engine..."

### Symptom

Docker Desktop remained stuck in an infinite loading loop showing "Starting the Docker Engine...". Reinstalling Docker Desktop did not resolve the issue. The system mouse cursor was flickering repeatedly every second, indicating a background crash/restart loop.

### Cause

Corrupted state files and a hung WSL 2 (Windows Subsystem for Linux) backend service running in an infinite failure/restart cycle on Windows.

### Solution (worked)

Reset stuck WSL instances and Docker state. Open PowerShell as Administrator and run:

```powershell
wsl --shutdown
wsl --unregister docker-desktop
wsl --unregister docker-desktop-data
```

Purge corrupted AppData configuration directories:

```powershell
Remove-Item -Recurse -Force "$env:APPDATA\Docker" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Docker" -ErrorAction SilentlyContinue
```

Re-initialize WSL components (if needed):

```powershell
wsl --update --web-download
```

Restart the PC and launch Docker Desktop.

---

## Issue 2 — Pydantic `ValidationError` (missing required settings)

### Symptom

Running the FastAPI container with:

```powershell
docker run --name student-api -p 8000:8000 student-management-api
```

caused the application to crash on startup with a pydantic validation error similar to:

```text
pydantic_core._pydantic_core.ValidationError: 8 validation errors for Settings
app_name -> Field required
db_host -> Field required
...
```

### Cause

The FastAPI app uses `pydantic-settings` to load configuration from environment variables. A plain `docker run` executes in an isolated environment and doesn't inherit your host environment variables or local `.env` file automatically.

### Solution (worked)

Pass the local `.env` file into the container at startup:

```powershell
docker run --name student-api -p 8000:8000 --env-file .env student-management-api
```

---

## Issue 3 — PostgreSQL connection refused (127.0.0.1:5432)

### Symptom

After supplying the `.env` file, the container timed out trying to connect to PostgreSQL:

```text
connection to server at "127.0.0.1", port 5432 failed: Connection refused
psycopg_pool.PoolTimeout: couldn't get a connection after 30.00 sec
```

### Cause

Inside a Docker container, `localhost` (127.0.0.1) refers to the container itself, not the host machine where PostgreSQL is running.

### Solution (worked)

Update your `.env` to use Docker's host gateway name instead of `localhost`:

```env
# From:
# DB_HOST=localhost

# To:
DB_HOST=host.docker.internal
```

Then recreate and run the container:

```powershell
docker rm student-api
docker run --name student-api -p 8000:8000 --env-file .env student-management-api
```

---

## Key takeaways

- **Networking:** Containers use isolated networks. Use `host.docker.internal` to reach services on the host (Windows/macOS).
- **Config management:** Supply `--env-file .env` or `-e KEY=VALUE` when running containers that rely on environment variables.
- **Container lifecycle:** Run `docker rm <container-name>` before re-running `docker run` with the same name.
