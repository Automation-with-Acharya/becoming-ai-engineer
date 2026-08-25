# Day 029 — Docker Local Deployment & Student Backend v2

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 24 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Explain what makes a containerized application deployment reproducible.
- Review a Docker image for unnecessary development/build artifacts.
- Understand Docker image hygiene and the role of `.dockerignore`.
- Understand why production images should be small, focused, and preferably immutable.
- Understand the principle of least privilege for container processes.
- Understand the development-versus-production runtime boundary.
- Recreate the complete Student Management stack with Docker Compose.
- Verify FastAPI, PostgreSQL, networking, health checks, configuration, persistence, and CRUD behavior end-to-end.
- Perform a deployment recovery drill and troubleshoot failures systematically.

---

# Big Picture

The last seven Docker days have built one continuous system.

```text
Day 23
Docker Fundamentals
        ↓
Day 24
FastAPI Container
        ↓
Day 25
FastAPI + PostgreSQL + Compose
        ↓
Day 26
Health Checks + Service Readiness
        ↓
Day 27
Environment + Restart Behaviour
        ↓
Day 28
Internal Networking + DNS + Inspection
        ↓
Day 29
Local Deployment + Production Hardening
```

Today we are not learning another disconnected Docker command.

We are answering the larger engineering question:

> **Can this backend be recreated reliably from the repository configuration instead of depending on manual machine setup?**

---

# 1. What Does "Reproducible Deployment" Mean?

A deployment is reproducible when the environment can be recreated from declared configuration and artifacts.

Instead of relying on:

```text
"This machine was manually configured three weeks ago."
```

we want:

```text
Source Code
   +
Dockerfile
   +
compose.yaml
   +
Configuration
   +
Persistent Storage
        ↓
Recreate Application Stack
```

Docker describes containers as ephemeral by design: they should be replaceable with minimal setup rather than manually repaired. citeturn199798view0

---

# 2. What Is an Immutable Application Image?

An application image is the artifact from which the container is created.

```text
Source Code
    ↓
docker build
    ↓
Application Image
    ↓
docker compose up
    ↓
Container
```

The container should not be treated like a manually maintained server.

When application code changes:

```text
Modify Source
     ↓
Build New Image
     ↓
Replace Container
```

This makes deployments predictable.

Docker explicitly describes images as immutable snapshots and recommends rebuilding regularly as part of keeping the image current. citeturn199798view0

---

# 3. Image Hygiene

A production-oriented image should contain what the application needs to run—and as little else as practical.

Avoid carrying unnecessary files such as:

```text
.git
.venv
__pycache__
*.pyc
IDE configuration
local development artifacts
secret files
```

A `.dockerignore` file helps exclude files that are not relevant to the image build context. citeturn199798view0

Mental model:

```text
Repository
   ↓
.dockerignore
   ↓
Useful Build Context
   ↓
Docker Image
```

---

# 4. Why Smaller Images Matter

A smaller image generally means:

- less data to transfer,
- faster startup/deployment operations,
- fewer packages and dependencies,
- lower complexity,
- a smaller potential vulnerability surface.

Docker recommends choosing trusted, minimal base images and avoiding unnecessary packages. citeturn199798view0

The goal is not:

> "Make the image tiny at any cost."

The goal is:

> **Include everything required by the runtime and avoid everything that is not.**

---

# 5. Development Image vs Production Image

Development often benefits from convenience:

```text
Source Code
    ↓
Bind Mount
    ↓
Development Container
    ↓
Fast Feedback
```

Production should generally prefer:

```text
Source Code
    ↓
Build
    ↓
Immutable Image
    ↓
Production Container
```

A production container should not depend on someone manually editing files on the host machine.

Docker's production guidance specifically discusses separating development-oriented configuration from production deployment and removing development source-code bindings where appropriate. citeturn199798view3

---

# 6. Multi-Stage Builds

A multi-stage Dockerfile separates build-time requirements from runtime requirements.

Example mental model:

```text
Stage 1 — Builder

Compiler / build tools
Dependencies
Tests
Build artifacts
        ↓
      COPY
        ↓
Stage 2 — Runtime

Runtime
Application
Only required dependencies
```

Docker recommends multi-stage builds as a way to reduce the size of the final image and keep build-only material out of the runtime image. citeturn199798view0turn199798view1

For our current FastAPI project, a multi-stage build may not be necessary simply for the sake of using one. The important engineering lesson is knowing **when** the separation is useful.

---

# 7. Base Image Selection

Our Dockerfile starts from a Python base image.

The engineering questions are:

```text
Is the image trusted?
Is it maintained?
Is it larger than necessary?
Does it include unnecessary tooling?
```

Docker recommends trusted official images and minimal bases where appropriate. citeturn199798view0

There is no universal rule that "smallest image wins." Compatibility, debugging needs, native dependencies, and operational requirements matter too.

---

# 8. Non-Root Containers

By default, some containers may execute their application process as `root`.

A least-privilege approach is to create a dedicated application user:

```dockerfile
RUN useradd --create-home appuser
USER appuser
```

Then:

```text
Container Process
      ↓
appuser
```

rather than unnecessarily running the application as root.

The `USER` Dockerfile instruction controls the user and group used for subsequent Dockerfile instructions and for the container's runtime process. citeturn199798view2

---

# 9. Why Least Privilege Matters

Suppose an application process is compromised.

The impact can be greater when the process has unnecessary privileges.

The principle is:

```text
Give the process
only the permissions
it actually needs.
```

This is part of a broader engineering principle:

> **Minimize privileges at every trust boundary.**

Do not treat `USER` as a magical security solution. It is one layer of defense within a larger container-security strategy.

---

# 10. Our Final Local Deployment Architecture

```text
                         HOST MACHINE
                              │
                              │ localhost:8000
                              ▼
                   ┌──────────────────────┐
                   │  FastAPI Container   │
                   │                      │
                   │ Middleware           │
                   │ Authentication       │
                   │ Router               │
                   │ Service              │
                   │ Repository           │
                   │ DB Helper            │
                   │ Connection Pool      │
                   └──────────┬───────────┘
                              │
                              │ db:5432
                              ▼
                   ┌──────────────────────┐
                   │ PostgreSQL Container │
                   │                      │
                   │ Health Check         │
                   └──────────┬───────────┘
                              │
                              ▼
                      postgres_data Volume
```

Around the two containers:

```text
Docker Compose
│
├── Environment Management
├── Internal Networking
├── Service Discovery
├── Health Checks
├── Restart Behaviour
└── Persistent Storage
```

---

# 11. One Command to Recreate the Stack

The central local-deployment command is:

```bash
docker compose up --build
```

Conceptually:

```text
compose.yaml
     ↓
Build / Pull Images
     ↓
Create Network
     ↓
Create / Recreate Containers
     ↓
Create / Reuse Volume
     ↓
PostgreSQL Starts
     ↓
Health Check
     ↓
Healthy
     ↓
FastAPI Starts
     ↓
Application Ready
```

This is the culmination of Days 25–29.

---

# 12. Verify the Stack

Start:

```bash
docker compose up --build
```

Inspect:

```bash
docker compose ps
```

You should verify that:

```text
api → running

db  → healthy
```

Then open:

```text
http://localhost:8000/docs
```

---

# 13. End-to-End Smoke Test

Do not stop at "Swagger loaded."

Verify an actual request flow:

```text
Client
  ↓
FastAPI
  ↓
Middleware
  ↓
Authentication / Authorization
  ↓
Router
  ↓
Service
  ↓
Repository
  ↓
Connection Pool
  ↓
PostgreSQL
```

Perform the available CRUD operations.

At minimum, verify the equivalent of:

```text
Login
Create Student
Read Student
Update Student
Delete Student
```

The exact routes depend on the current Student Management implementation.

---

# 14. Deployment Recovery Drill

A container is replaceable.

Test that assumption.

Stop the API:

```bash
docker compose stop api
```

Inspect:

```bash
docker compose ps
```

Start it again:

```bash
docker compose start api
```

Verify the API works again.

This demonstrates:

```text
Container stops
     ↓
Container starts
     ↓
Application recovers
```

---

# 15. Full Environment Recreation

Now perform the stronger test:

```bash
docker compose down
```

Then:

```bash
docker compose up -d
```

Watch the stack return:

```text
Network
   ↓
PostgreSQL
   ↓
Health Check
   ↓
Healthy
   ↓
FastAPI
   ↓
API Ready
```

Then verify that your database data still exists.

That proves:

```text
Container lifecycle
        ≠
Database data lifecycle
```

because the data lives in the persistent volume.

---

# 16. Host vs Internal Connectivity

Our deployment now has two distinct connection paths.

### Host → API

```text
Browser
   ↓
localhost:8000
   ↓
FastAPI Container
```

### Container → Database

```text
FastAPI Container
   ↓
Docker DNS
   ↓
db:5432
   ↓
PostgreSQL Container
```

### Host → Database (development tooling, when published)

```text
pgAdmin / psql on Host
   ↓
localhost:5433
   ↓
PostgreSQL Container :5432
```

These paths serve different purposes.

---

# 17. Deployment Troubleshooting Flow

When the complete environment fails, use the accumulated troubleshooting discipline from Days 17 and 24–28.

```text
Application failure
       ↓
docker compose ps
       ↓
Container state
       ↓
Health state
       ↓
docker compose logs api
       ↓
docker compose logs db
       ↓
docker compose config
       ↓
Network inspection
       ↓
Environment verification
       ↓
Root cause
       ↓
Fix
       ↓
docker compose up --build
       ↓
Smoke test
```

This is much stronger than randomly changing several settings at once.

---

# 18. Deliberate Failure Drill

A useful final exercise is to break one deployment layer.

Examples:

```text
Wrong DB_HOST
Wrong port
Wrong healthcheck
Wrong environment variable
Wrong startup command
```

Then use the troubleshooting sequence:

```text
Failure
  ↓
State
  ↓
Logs
  ↓
Config
  ↓
Network
  ↓
Root Cause
  ↓
Fix
  ↓
Rebuild
  ↓
Verify
```

The point is to prove that you can recover the system, not simply start it successfully once.

---

# 19. Common Beginner Mistakes

### Mistake 1 — Treating the container as a permanent server

Don't manually repair application files inside a production container.

Prefer:

```text
Change Source
  ↓
Build New Image
  ↓
Replace Container
```

### Mistake 2 — Shipping unnecessary development files

Use `.dockerignore` and inspect what actually enters the build context.

### Mistake 3 — Running everything as root

Use a dedicated user when appropriate and compatible with the application.

### Mistake 4 — Assuming a small image is automatically a better image

Compatibility and operational requirements matter too.

### Mistake 5 — Publishing unnecessary ports

Expose only what must be reachable from outside the Docker network.

### Mistake 6 — Forgetting persistent database storage

Containers are disposable; important data needs persistent storage.

### Mistake 7 — Declaring deployment complete because `/docs` loads

A deployment should be verified through a real end-to-end request and data flow.

---

# 20. Production Best Practices

✅ Build reproducible application images.

✅ Keep images focused and avoid unnecessary packages. citeturn199798view0

✅ Use `.dockerignore` to keep unwanted files out of the build context. citeturn199798view0

✅ Prefer immutable application images for production deployment. citeturn199798view0

✅ Use least-privilege runtime users where appropriate. citeturn199798view2

✅ Keep persistent data outside disposable containers.

✅ Keep production configuration separate from development conveniences. citeturn199798view3

✅ Verify the complete application stack after deployment.

✅ Build and test images through CI/CD as the project matures. citeturn199798view0

---

# 21. Interview Questions

### Q1. What does reproducible deployment mean?

It means the application environment can be recreated consistently from declared configuration and deployment artifacts rather than depending on manually configured machine state.

### Q2. Why should containers be ephemeral?

Because application containers should be replaceable. Persistent state should live in appropriate external storage such as volumes or managed services. Docker explicitly recommends designing containers to be as ephemeral as possible. citeturn199798view0

### Q3. Why keep images small?

Smaller images reduce transfer time, complexity, dependencies, and potential vulnerability surface. citeturn199798view0

### Q4. What is a multi-stage Docker build?

A Dockerfile technique that uses separate build and runtime stages so build-only dependencies do not need to remain in the final runtime image. citeturn199798view0turn199798view1

### Q5. Why run a container as a non-root user?

To reduce unnecessary privileges of the application process and follow the principle of least privilege.

### Q6. What makes a deployment reproducible?

Versioned source code, deterministic application configuration, Docker build instructions, Compose service definitions, and explicit persistent-storage requirements.

### Q7. How do you verify a local deployment?

Check container state and health, inspect logs, verify networking/configuration, open the API, and execute real end-to-end requests against the database.

---

# 22. FastAPI ↔ ASP.NET Core Mapping

The same deployment principles apply to .NET:

```text
ASP.NET Core API
      ↓
Docker Image
      ↓
Container
      ↓
Docker Compose
      ↓
SQL Server / PostgreSQL / Redis
```

The framework changes.

The deployment engineering principles remain:

```text
Reproducibility
+
Configuration
+
Health
+
Networking
+
Persistence
+
Least Privilege
+
Observability
```

---

# 23. Cheat Sheet

```text
docker image inspect <image>
→ Inspect image metadata

docker compose up --build
→ Build/rebuild images and start the stack

docker compose ps
→ Show service/container state

docker compose logs api
→ Inspect API logs

docker compose logs db
→ Inspect PostgreSQL logs

docker compose stop api
→ Stop the API service container

docker compose start api
→ Start it again
docker compose down
→ Remove the running Compose stack

docker compose up -d
→ Start the stack in background

docker compose exec api whoami
→ Inspect the runtime user
```

---

# 24. Final Mental Model

```text
                         REPOSITORY
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
          Dockerfile      compose.yaml    Configuration
              │               │               │
              ▼               └──────┬────────┘
          Docker Image               │
              │                      │
              └──────────┬───────────┘
                         ▼
                  Docker Compose
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        FastAPI Container      PostgreSQL Container
              │                     │
              └────── db:5432 ──────┘
                                    │
                                    ▼
                             Persistent Volume
```

The deployment goal is:

```text
Source
  ↓
Build
  ↓
Image
  ↓
Compose
  ↓
Healthy Services
  ↓
Networked Services
  ↓
Persistent Data
  ↓
Working Application
```

---

# Key Takeaways

- A production-oriented container deployment should be reproducible from source, Dockerfile, Compose configuration, and persistent-storage definitions.
- Containers should be treated as replaceable runtime units rather than manually maintained servers. citeturn199798view0
- Image hygiene matters: exclude irrelevant files, avoid unnecessary packages, and choose an appropriate trusted base image. citeturn199798view0
- Multi-stage builds can keep build-only dependencies out of the final runtime image when the project benefits from that separation. citeturn199798view1turn199798view0
- Running the application with a dedicated non-root user supports least-privilege container design. citeturn199798view2
- Local deployment is successful only when the complete stack works: configuration, networking, health checks, persistence, API requests, and database operations.
- The Student Management backend has now progressed from individual Docker experiments to a reproducible multi-container local deployment foundation.

---

# Project ₹50L — Architecture Evolution

```text
Day 23
Docker Fundamentals
        │
        ▼
Day 24
FastAPI Container
        │
        ▼
Day 25
Multi-Container Compose
        │
        ▼
Day 26
Health Checks + Readiness
        │
        ▼
Day 27
Environment + Restart
        │
        ▼
Day 28
Internal Networking + DNS
        │
        ▼
Day 29
Local Deployment + Production Hardening
        │
        ▼
Student Backend v2
```

This is the culmination of the Docker portion of our current backend build:

```text
Application Code
      ↓
Clean Architecture
      ↓
FastAPI
      ↓
PostgreSQL
      ↓
Docker
      ↓
Docker Compose
      ↓
Health / Config / Network / Persistence
      ↓
Reproducible Local Deployment
```

---

# Revision Checklist

- [ ] Can explain reproducible deployment.
- [ ] Can explain immutable application images.
- [ ] Understand why `.dockerignore` matters.
- [ ] Understand image-size and dependency hygiene.
- [ ] Understand multi-stage builds and when they are useful.
- [ ] Understand the least-privilege principle for container users.
- [ ] Can recreate the complete stack with `docker compose up --build`.
- [ ] Can verify API and database health.
- [ ] Can verify persistence after container recreation.
- [ ] Can troubleshoot deployment failures systematically.
- [ ] Can explain the complete Student Backend v2 deployment architecture.

---

# Exact Resources Used

- Docker Docs — Building best practices: https://docs.docker.com/build/building/best-practices/
- Docker Docs — Multi-stage builds: https://docs.docker.com/build/building/multi-stage/
- Docker Docs — Dockerfile reference / `USER`: https://docs.docker.com/reference/dockerfile/#user
- Docker Docs — Use Compose in production: https://docs.docker.com/compose/how-tos/production/

These resources were selected for Day 029's image hygiene, production container design, least privilege, multi-stage build awareness, and local deployment objectives.
