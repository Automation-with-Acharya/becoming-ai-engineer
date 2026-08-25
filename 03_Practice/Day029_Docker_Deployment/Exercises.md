# Day 29 Docker Deployment Exercises

## Exercise 1: Inspect the Current Docker Image

Run:

```bash
docker images
```

Find your `student-management-api` image, then inspect it:

```bash
docker image inspect student-management-api
```

Look for:

- Image size
- Entrypoint or command
- Environment-related metadata
- Exposed ports
- Working directory

### Question

Is this image carrying anything that belongs only to development?

Examples include:

- `.git`
- `__pycache__`
- `.venv`
- Logs
- Editor configuration
- Temporary files

Your `.dockerignore` already handles many of these. Today, verify that the final build context is clean.

## Exercise 2: Review the Dockerfile for Runtime Purity

Open your existing Dockerfile and ask:

Does the runtime image contain only:

- Python runtime
- Dependencies
- Application code

Or does it also contain:

- Build-only tools
- Temporary files
- Development artifacts

Do not rewrite everything just to make it "advanced". The goal is to reason about the image contents.

## Exercise 3: Non-Root Experiment

Introduce a dedicated application user in a practice copy of the Dockerfile.

Conceptually:

```dockerfile
RUN useradd --create-home appuser

USER appuser
```

Then build:

```bash
docker compose build
```

Run:

```bash
docker compose up
```

Verify that the application still works. Then inspect the running container:

```bash
docker compose exec api whoami
```

The result should be `appuser` rather than `root`.

> **Important:** If your current filesystem permissions or project setup make this unnecessarily disruptive, do not force the change into the final application today.

The learning objective is to understand the principle and test it safely.

## Exercise 4: Final Compose Deployment Run

Bring up the entire stack with one command:

```bash
docker compose up --build
```

Then verify the services:

```bash
docker compose ps
```

You should see:

- `api`
- `db`

The database should reach `healthy` before the API becomes ready, based on the Day 26 architecture.

## Exercise 5: Full End-to-End Verification

Perform a complete smoke test by opening:

<http://localhost:8000/docs>

Then test the complete request path:

```text
Authentication
	-> JWT
	-> Protected endpoint
	-> FastAPI
	-> Service
	-> Repository
	-> PostgreSQL
```

At minimum, verify:

- `POST` login
- `GET` students
- `POST` student
- `GET` student
- `PUT` student
- `DELETE` student

Use the exact endpoints that exist in your current application.

## Exercise 6: Test Deployment Recovery

Stop the API container:

```bash
docker compose stop api
```

Inspect the services:

```bash
docker compose ps
```

Start the API again:

```bash
docker compose start api
```

Then verify that the following work again:

```text
Swagger
	-> API
	-> Database
```

This reinforces the principle that containers are replaceable runtime units, not manually maintained servers.

## Exercise 7: Simulate a Full Environment Restart

Run:

```bash
docker compose down
```

Then start the stack in detached mode:

```bash
docker compose up -d
```

Observe:

```text
Network recreated
	-> PostgreSQL container recreated
	-> Health check
	-> Healthy
	-> FastAPI starts
	-> Application available
```

Then verify that the database data still exists.

This is your final proof that:

```text
Container lifecycle != Database data lifecycle
```

The persistent volume preserves the database data.

## Exercise 8: Verify the Deployment From the Outside

From the host machine, run:

```bash
curl http://localhost:8000/docs
```

You can also open Swagger directly.

Then verify PostgreSQL through your host-side pgAdmin configuration if you still have its published port available.

You are proving both paths:

```text
HOST
|-- localhost:8000 -> API
`-- localhost:5433 -> PostgreSQL

API Container
`-- db:5432 -> PostgreSQL Container
```

## Exercise 9: Final Failure Drill

Before calling Day 29 complete, deliberately break one deployment layer.

Pick one:

- Incorrect `DB_HOST`
- Incorrect port
- Incorrect health check
- Incorrect environment variable
- Incorrect startup command

Then troubleshoot using the workflow built over Days 17, 24, 26, 27, and 28:

```text
Failure
	-> docker compose ps
	-> docker compose logs
	-> docker compose config
	-> Network inspection
	-> Root cause
	-> Fix
	-> docker compose up --build
	-> Verify
```

This is the point where all of the Docker days come together.
