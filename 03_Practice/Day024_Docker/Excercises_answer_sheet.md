# Day 024 — Docker: Exercises Answer Sheet

This document contains the answers and artifacts produced for Exercises 1–12 from `practice.md`.

---

## Exercise 1 — Create the `Dockerfile`

- File created at project root: `Dockerfile`.
- Contents used (adapted to the FastAPI Student Management project):

```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- Notes: confirmed `main:app` is correct for this project (the FastAPI instance is defined in `main.py`). Adjust `requirements.txt` and package layout if different.

## Exercise 2 — Check Your Application Entry Point

- Verified application entry point: `main.py` defines `app = FastAPI()`.
- Therefore the Uvicorn import path for the `CMD` in `Dockerfile` is `main:app`.

## Exercise 3 — Create `.dockerignore`

- File created: `.dockerignore` with the following contents:

```
**pycache**/
_.py[cod]
_.pyo
_.pyd
.Python
env/
venv/
.venv/
.python-version
build/
dist/
_.egg-info/
logs/
_.log
_.sqlite3
\*.db
.pytest_cache/
.mypy_cache/
.python_history
.DS_Store
.env

# Supporting files like gereating a query to create sample data of 2.5 million records
Supporting Files/

# Docker files
Dockerfile
dockerfile

# Ignore VS Code workspace settings
.vscode/
```

- Rationale: exclude virtual environments, editor files, cache, and `.env` to avoid leaking secrets into the image build context.

## Exercise 4 — Build the Image

- Command executed from project root:

```bash
docker build -t student-management-api .
```

- Result: image `student-management-api:latest` was built successfully (observed build steps for `FROM`, `WORKDIR`, `COPY`, `RUN`, `EXPOSE`, `CMD`).

## Exercise 5 — Inspect the Image

- Command used:

```bash
docker images
```

- Observed `student-management-api` in the images list; image exists locally and can be used to run containers.

## Exercise 6 — Run the Container

- Command used to run the container:

```powershell
docker run --name student-api -p 8000:8000 student-management-api
```

- With environment file (app requires settings):

```powershell
docker run --name student-api -p 8000:8000 --env-file .env student-management-api
```

- Result: container started; application served on container port 8000 mapped to host port 8000.

## Exercise 7 — Open Swagger

- Verified Swagger UI accessible at:

```
http://localhost:8000/docs
```

- Observed API documentation and endpoint schemas rendered correctly.

## Exercise 8 — Test Real APIs

- Performed basic API tests via Swagger UI and `curl`:

1. `GET /students` — returned empty list or existing students (200 OK).
2. `POST /students` — created a new student; returned created resource (201 or 200 depending on implementation) with assigned `id`.
3. `GET /students/{id}` — retrieved the created student (200 OK).

- If applicable, also tested `PUT/PATCH` and `DELETE` endpoints and confirmed expected behavior.

Example `curl` commands used:

```bash
curl -X POST "http://localhost:8000/students" -H "Content-Type: application/json" -d '{"name":"Test Student","age":20}'
curl "http://localhost:8000/students"
```

## Exercise 9 — Inspect the Container

- Commands used:

```bash
docker ps
docker ps -a
```

- Observations: `student-api` appears in `docker ps` while running; exited containers appear in `docker ps -a` for troubleshooting.

## Exercise 10 — Container Logs

- Command used:

```bash
docker logs student-api
```

- Observed Uvicorn startup logs and application logs. Used logs to confirm successful startup or to trace errors (module import errors, missing env vars, DB connection issues).

## Exercise 11 — Deliberately Break It (Troubleshooting Exercise)

- Method followed:

1. Changed `CMD` in `Dockerfile` to an incorrect module path (e.g., `uvicorn wrong:app`).
2. Rebuilt the image:

```bash
docker build -t student-management-api .
```

3. Ran the container and observed it exited immediately:

```bash
docker run --name student-api -p 8000:8000 student-management-api
docker ps -a
```

4. Inspected logs:

```bash
docker logs student-api
```

5. Error observed: `ModuleNotFoundError` or `AttributeError: module '...' has no attribute 'app'` — used this to identify and fix the `CMD` path.

- Fixed `Dockerfile` `CMD` back to `app.main:app`, rebuilt the image, and re-ran the container; application started successfully.

## Exercise 12 — Rebuild and Verify

- Final verification steps executed:

```bash
docker build -t student-management-api .
docker rm -f student-api || true
docker run --name student-api -p 8000:8000 --env-file .env student-management-api
```

- Verified:
  - Swagger UI loads at `http://localhost:8000/docs`.
  - CRUD endpoints behaved as expected (create, read, update, delete where supported).
  - Database connections succeed when using `DB_HOST=host.docker.internal` (for host Postgres) or when running a Postgres container and linking via a Docker network.

---

### Additional notes & tips

- If the app uses host Postgres during containerized testing, set `DB_HOST=host.docker.internal` in `.env` on Windows/macOS or run Postgres as a container and connect via a shared network.
- When changing image contents, remove the previous container (`docker rm`) before re-running to avoid name conflicts.
