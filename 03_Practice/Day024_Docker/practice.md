# Day 024 — Docker

## Exercise 1 — Create the Dockerfile

1. Change to the root of your FastAPI Student Management project.
2. Create a file named `Dockerfile` (no extension).

Example starter Dockerfile (adjust to your project structure):

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Note: Don't blindly copy the example — adapt the module path and dependency steps to your project.

Dockerfile instruction flow (conceptually):

- `FROM` → base image
- `WORKDIR` → set working directory inside the image
- `COPY` → copy files into the image
- `RUN` → run build-time commands (install deps)
- `COPY` → copy application source
- `EXPOSE` → document the container port
- `CMD` → default runtime command

## Exercise 2 — Check Your Application Entry Point

Find where your FastAPI app instance is created, for example:

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI()
```

Determine the correct Uvicorn import path for `CMD` in the Dockerfile. Examples:

- `app.main:app` (if `app/main.py` defines `app`)
- `main:app` (if `main.py` sits at the project root)
- `src.main:app` (if your package root is `src/`)

This is a practical exercise in understanding Python module paths.

## Exercise 3 — Create `.dockerignore`

Create a `.dockerignore` file to avoid including unnecessary or sensitive files in the build context.

Suggested contents:

```
.git
.gitignore
.venv
venv
**/__pycache__/
*.pyc
.pytest_cache
.vscode
.idea
.env
```

Important: deliberately exclude `.env` so secrets/configuration aren't copied into the image (see Day 019 — Configuration & Environment Variables).

## Exercise 4 — Build the Image

From the project root run:

```bash
docker build -t student-management-api .
```

Watch the build output to see Docker execute the Dockerfile instructions.

Conceptual flow: `Dockerfile` → `FROM` → `WORKDIR` → `COPY` → `RUN` → `COPY` → `EXPOSE` → `CMD` → `IMAGE`

## Exercise 5 — Inspect the Image

List images:

```bash
docker images
```

Find `student-management-api`. This is an image (not a running container).

## Exercise 6 — Run the Container

Run the image:

```bash
docker run --name student-api -p 8000:8000 student-management-api
```

`-p 8000:8000` maps host port 8000 → container port 8000, allowing `http://localhost:8000` to reach the app running in the container.

## Exercise 7 — Open Swagger

Open your browser at:

```
http://localhost:8000/docs
```

This verifies the application is served from inside Docker (Windows → Docker → Container → FastAPI).

## Exercise 8 — Test Real APIs

From Swagger UI or with curl/httpie test at least:

- `GET /students` (retrieve students)
- `POST /students` (create a student)
- `GET /students/{id}` (retrieve created student)

If your project supports update/delete, test those as well — ensure end-to-end functionality (app + DB) inside the container.

## Exercise 9 — Inspect the Container

List running containers:

```bash
docker ps
```

List all containers (including exited):

```bash
docker ps -a
```

Understand the difference between running and stopped containers.

## Exercise 10 — Container Logs

View logs:

```bash
docker logs student-api
```

Flow: FastAPI → Python logger / Uvicorn → container stdout/stderr → Docker → `docker logs`.

This is useful for production-style troubleshooting.

## Exercise 11 — Deliberately Break It (Troubleshooting Exercise)

1. Temporarily change the `CMD` in `Dockerfile` to an incorrect module path.
2. Rebuild the image:

```bash
docker build -t student-management-api .
```

3. Run the container and observe:

```bash
docker run --name student-api -p 8000:8000 student-management-api
docker ps -a
```

4. If it exited, inspect logs:

```bash
docker logs student-api
```

Troubleshooting workflow:

- Container stopped → `docker ps -a`
- Find container → `docker logs <name>`
- Read error → identify root cause → fix code or Dockerfile → rebuild

Don't immediately ask AI — practice reading the logs and fixing the root cause yourself first.

## Exercise 12 — Rebuild and Verify

After fixing the issue, rebuild and run:

```bash
docker build -t student-management-api .
docker run --name student-api -p 8000:8000 student-management-api
```

Verify:

- Swagger UI loads
- APIs behave correctly
- Database connections (if used) operate inside the container
