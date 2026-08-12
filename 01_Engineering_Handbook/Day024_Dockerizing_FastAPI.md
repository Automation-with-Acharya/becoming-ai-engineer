# Day 024 — Dockerizing FastAPI

> **Project ₹50L | 365-Day Career Transformation**  
> **Date:** 12 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Create a Dockerfile for a FastAPI application.
- Understand `FROM`, `WORKDIR`, `COPY`, `RUN`, `EXPOSE`, and `CMD`.
- Build a Docker image from the FastAPI project.
- Run FastAPI inside a Docker container.
- Understand Docker port mapping.
- Understand why Uvicorn should listen on `0.0.0.0` inside a container.
- Use `.dockerignore`.
- Pass configuration into containers without baking secrets into images.
- Access FastAPI Swagger UI through a Docker-published port.
- Inspect container logs.
- Troubleshoot a failed container.
- Understand how Docker fits around Clean Architecture.

---

# 1. From "Understanding Docker" to "Using Docker"

On Day 023:

```text
Dockerfile
    ↓
Docker Image
    ↓
Docker Container
```

Today we apply that to our actual application.

Before:

```text
Windows
   ↓
Python
   ↓
FastAPI
   ↓
Student Management API
```

After:

```text
Windows
   ↓
Docker
   ↓
FastAPI Container
   ↓
Student Management API
```

The application itself hasn't fundamentally changed.

**The runtime environment has.**

---

# 2. Our FastAPI Architecture Inside Docker

Docker sits outside the application's internal architecture.

```text
┌──────────────────────────────────────┐
│          Docker Container            │
│                                      │
│             FastAPI                  │
│                │                     │
│                ▼                     │
│             Router                   │
│                │                     │
│                ▼                     │
│             Service                  │
│                │                     │
│                ▼                     │
│            Repository                │
│                │                     │
│                ▼                     │
│         Connection Pool              │
│                                      │
└──────────────────┬───────────────────┘
                   │
                   ▼
              PostgreSQL
```

> **Clean Architecture defines how our application is structured; Docker defines how that application is packaged and run.**

---

# 3. Dockerfile

A Dockerfile contains instructions for constructing a Docker image.

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

The exact Uvicorn module path depends on where the FastAPI application object exists.

For example, if `main.py` contains:

```python
app = FastAPI()
```

then:

```text
main:app
```

is appropriate.

If the file is `app/main.py`, then:

```text
app.main:app
```

is appropriate.

---

# 4. Dockerfile Instruction Flow

```text
Dockerfile

   │
   ▼
FROM
   │
   ▼
WORKDIR
   │
   ▼
COPY
   │
   ▼
RUN
   │
   ▼
COPY
   │
   ▼
EXPOSE
   │
   ▼
CMD
```

There is an important distinction between build-time and runtime instructions.

---

# 5. `FROM`

```dockerfile
FROM python:3.12-slim
```

This specifies the base image.

We're starting with an existing Python environment instead of constructing an operating system environment ourselves.

```text
python:3.12-slim
        ↓
Python runtime
        ↓
Our application
```

---

# 6. `WORKDIR`

```dockerfile
WORKDIR /app
```

This establishes the working directory inside the image/container.

Subsequent commands operate relative to `/app`.

---

# 7. `COPY`

```dockerfile
COPY requirements.txt .
```

This copies the dependency file from the build context into the image.

Later:

```dockerfile
COPY . .
```

copies the application source into the image.

```text
Your Computer
     │
     │ COPY
     ▼
Docker Image
```

---

# 8. `RUN`

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

`RUN` executes a command **while the image is being built**.

```text
RUN
 ↓
Build time
```

For example:

```text
docker build
     ↓
RUN pip install ...
     ↓
Dependencies installed
     ↓
Image created
```

---

# 9. `CMD`

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`CMD` defines the default command executed when the container starts.

Therefore:

```text
RUN
 ↓
Build time
```

while:

```text
CMD
 ↓
Container runtime
```

### Remember

> **RUN builds the image. CMD starts the application.**

---

# 10. Why `0.0.0.0`?

Inside the container we want Uvicorn to listen on all available network interfaces:

```bash
--host 0.0.0.0
```

and:

```bash
--port 8000
```

So the application listens on:

```text
0.0.0.0:8000
```

This allows Docker's networking layer to forward traffic to the application.

---

# 11. `EXPOSE 8000`

Our Dockerfile contains:

```dockerfile
EXPOSE 8000
```

`EXPOSE` **does not publish the port to your host machine**.

It communicates:

> This containerized application is intended to listen on port 8000.

Think of it as image metadata/documentation.

---

# 12. `-p 8000:8000`

When we run:

```bash
docker run --name student-api -p 8000:8000 student-management-api
```

the `-p` option creates the host-to-container port mapping.

The format is:

```text
-p HOST_PORT:CONTAINER_PORT
```

Therefore:

```text
-p 8000:8000
   │     │
   │     └── Container port
   │
   └──────── Host port
```

---

# 13. `EXPOSE` vs `-p`

This distinction is important enough to memorize.

```text
CMD
 ↓
Tells Uvicorn:
"Listen on port 8000"
```

```text
EXPOSE 8000
 ↓
Documents:
"The application uses container port 8000"
```

```text
-p 8000:8000
 ↓
Actually maps:
"Host port 8000 → Container port 8000"
```

Complete flow:

```text
Browser
   │
   │ localhost:8000
   ▼
Host Machine :8000
   │
   │ Docker port mapping
   ▼
Container :8000
   │
   ▼
Uvicorn
   │
   ▼
FastAPI
```

---

# 14. Changing the Host Port

The two ports don't have to be identical.

```bash
docker run -p 9000:8000 student-management-api
```

means:

```text
Browser
   │
   │ localhost:9000
   ▼
Host :9000
   │
   │ 9000 → 8000
   ▼
Container :8000
   │
   ▼
FastAPI
```

FastAPI still listens on `8000`, but users access it through `9000` on the host.

---

# 15. Build the Image

From the project root:

```bash
docker build -t student-management-api .
```

Conceptually:

```text
Dockerfile
    +
Application Code
    +
Dependencies
       │
       │ docker build
       ▼
Docker Image
```

---

# 16. Image vs Container

After:

```bash
docker build -t student-management-api .
```

we have an:

```text
IMAGE
```

Then:

```bash
docker run student-management-api
```

creates a:

```text
CONTAINER
```

Therefore:

```text
docker build
      ↓
Image

docker run
      ↓
Container
```

---

# 17. Running the FastAPI Container

```bash
docker run --name student-api -p 8000:8000 student-management-api
```

Breakdown:

```text
docker run
    ↓
Create + start container

--name student-api
    ↓
Give container a readable name

-p 8000:8000
    ↓
Map host port → container port

student-management-api
    ↓
Image from which container is created
```

---

# 18. Swagger Through Docker

Once the container is running:

```text
http://localhost:8000/docs
```

should open our FastAPI Swagger UI.

Request flow:

```text
Browser
   │
   ▼
localhost:8000
   │
   ▼
Docker Host
   │
   ▼
Port Mapping
   │
   ▼
FastAPI Container
   │
   ▼
Uvicorn
   │
   ▼
FastAPI
   │
   ▼
Router
   │
   ▼
Service
   │
   ▼
Repository
```

---

# 19. `.dockerignore`

Create:

```text
.dockerignore
```

Example:

```text
.git
.gitignore
.venv
venv
__pycache__
*.pyc
.pytest_cache
.vscode
.idea
.env
```

The purpose is to prevent unnecessary or sensitive files from being included in the Docker build context.

---

# 20. Why `.env` Must Be Ignored

Our environment file might contain:

```text
DATABASE_PASSWORD=...
JWT_SECRET=...
```

We don't want these secrets accidentally copied into the image.

Therefore:

```text
.env
```

belongs in `.dockerignore`.

The better production pattern is:

```text
Container
   ↑
Environment variables / secrets
```

rather than:

```text
Docker Image
   ↑
Hardcoded secrets
```

---

# 21. Inspecting Containers

List running containers:

```bash
docker ps
```

List all containers:

```bash
docker ps -a
```

```text
docker ps
    ↓
Running containers
```

```text
docker ps -a
    ↓
Running + stopped/exited containers
```

---

# 22. Container Logs

Run:

```bash
docker logs student-api
```

This connects directly to our Day 017 structured logging work.

```text
FastAPI / Uvicorn
       ↓
Application logs
       ↓
stdout / stderr
       ↓
Docker
       ↓
docker logs
```

If Swagger shows:

```text
500 Internal Server Error
```

investigate the container:

```bash
docker logs student-api
```

---

# 23. Container Troubleshooting Workflow

```text
Is the container running?
        │
        ├── YES ──→ docker logs
        │
        └── NO
             │
             ▼
        docker ps -a
             │
             ▼
        Container exited?
             │
             ▼
        docker logs
             │
             ▼
        Read actual error
             │
             ▼
        Identify root cause
             │
             ▼
        Fix
             │
             ▼
        Rebuild
             │
             ▼
        Run again
```

---

# 24. Deliberate Failure Experiment

Temporarily specify an incorrect Uvicorn module, such as:

```text
wrong_module:app
```

Build and run.

The container may:

```text
Start
  ↓
Uvicorn fails
  ↓
Process exits
  ↓
Container stops
```

Then:

```bash
docker ps -a
```

and:

```bash
docker logs student-api
```

Use the error message to identify the problem.

Then fix it and rebuild.

This teaches:

> **How to troubleshoot a containerized application.**

---

# 25. Docker and Configuration

Our configuration architecture becomes:

```text
Docker Container
       │
       ▼
Environment Variables
       │
       ▼
Configuration Layer
       │
       ▼
Application
```

Configuration such as:

```text
DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
JWT_SECRET
```

should be provided externally.

We should not bake secrets into the image.

---

# 26. Docker and Connection Pooling

Our Day 021 architecture fits naturally:

```text
Container Starts
       │
       ▼
FastAPI Lifespan
       │
       ▼
Create Connection Pool
       │
       ▼
Application Ready
```

Shutdown:

```text
Container Shutdown
       │
       ▼
FastAPI Lifespan Shutdown
       │
       ▼
Close Connection Pool
```

---

# 27. Docker and Clean Architecture

Our application remains:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
Database
```

Docker surrounds that architecture:

```text
┌────────────────────────────────────┐
│          Docker Container          │
│                                    │
│  Router                            │
│    ↓                               │
│  Service                           │
│    ↓                               │
│  Repository                        │
│    ↓                               │
│  Connection Pool                   │
│                                    │
└────────────────────────────────────┘
```

Docker is an infrastructure/deployment concern around the application.

---

# 28. What Happens When We Change Code?

If we modify:

```text
students/service.py
```

the existing image doesn't automatically change.

We need:

```text
Modify source
     ↓
docker build
     ↓
New image
     ↓
New container
```

This is the **immutable image** mindset.

---

# 29. Docker Image Lifecycle

```text
Source Code
     │
     ▼
Dockerfile
     │
     │ docker build
     ▼
Docker Image
     │
     │ docker run
     ▼
Container
     │
     ▼
Application
```

---

# 30. Our Current Architecture

```text
                         Browser
                            │
                            │ localhost:8000
                            ▼
                     ┌──────────────┐
                     │ Docker Host  │
                     └──────┬───────┘
                            │
                            │ :8000 → :8000
                            ▼
               ┌──────────────────────────┐
               │     FastAPI Container    │
               │                          │
               │       Uvicorn            │
               │          ↓               │
               │        FastAPI           │
               │          ↓               │
               │        Router             │
               │          ↓               │
               │       Service             │
               │          ↓               │
               │      Repository           │
               │          ↓               │
               │   Connection Pool         │
               └────────────┬─────────────┘
                            │
                            ▼
                       PostgreSQL
```

**Today's PostgreSQL remains outside Docker.**

---

# 31. Why Are We Doing PostgreSQL Separately?

We're learning this incrementally.

Today's:

```text
FastAPI
   ↓
Docker
   ↓
PostgreSQL
```

Later:

```text
FastAPI Container
        ↓
Docker Network
        ↓
PostgreSQL Container
```

And then:

```text
Docker Compose
       ↓
FastAPI
+
PostgreSQL
```

This progression prevents us from throwing Dockerfiles, networking, databases, volumes, and Compose at you all at once.

---

# 32. Common Mistakes

### ❌ Assuming `EXPOSE` publishes the port

It doesn't.

```dockerfile
EXPOSE 8000
```

does not automatically make `localhost:8000` accessible.

You need:

```bash
-p 8000:8000
```

### ❌ Using `127.0.0.1` inside the container

For this setup, Uvicorn should listen on:

```text
0.0.0.0
```

### ❌ Copying `.env` into the image

Use `.dockerignore` and external configuration.

### ❌ Assuming changing source changes the image

You need to rebuild.

### ❌ Treating a stopped container as deleted

A stopped container remains visible through:

```bash
docker ps -a
```

---

# 33. Interview Questions

### Q1. What is a Dockerfile?

A text file containing instructions used to build a Docker image.

### Q2. What is the difference between `RUN` and `CMD`?

```text
RUN
→ Executes during image build.

CMD
→ Defines the default command when a container starts.
```

### Q3. What does `EXPOSE 8000` do?

It documents the intended port on which the containerized application listens. It does not itself publish the port to the host.

### Q4. What does `-p 8000:8000` do?

It maps:

```text
Host port 8000
        ↓
Container port 8000
```

### Q5. Why use `0.0.0.0` inside a container?

Because the application needs to listen on the container's network interfaces so Docker can forward external traffic to it.

### Q6. How do you see logs from a container?

```bash
docker logs <container>
```

### Q7. How do you troubleshoot a container that immediately exits?

```text
docker ps -a
      ↓
Find exited container
      ↓
docker logs <container>
      ↓
Identify root cause
      ↓
Fix
      ↓
Rebuild
      ↓
Run again
```

### Q8. What happens when application source code changes?

The image needs to be rebuilt so the new source is included.

### Q9. Why use `.dockerignore`?

To prevent unnecessary, sensitive, or unwanted files from being included in the Docker build context.

---

# 34. Cheat Sheet

### Build

```bash
docker build -t student-management-api .
```

### Run

```bash
docker run --name student-api -p 8000:8000 student-management-api
```

### Running containers

```bash
docker ps
```

### All containers

```bash
docker ps -a
```

### Logs

```bash
docker logs student-api
```

### Stop

```bash
docker stop student-api
```

### Remove

```bash
docker rm student-api
```

### Images

```bash
docker images
```

---

# 35. The Three Port Concepts

```text
CMD
 │
 └── Uvicorn listens on 8000
              │
              ▼
       Container :8000
              ▲
              │
EXPOSE 8000 ──┘
(metadata/documentation)

              ▲
              │
      -p 8000:8000
              │
              ▼
        Host :8000
```

Therefore:

> **`CMD` tells the application where to listen. `EXPOSE` documents the container port. `-p` publishes/maps the port to the host.**

---

# 36. Engineering Sprinkle — Container Troubleshooting

When an API running inside Docker fails, don't immediately rebuild everything.

Use:

```text
Is the container running?
        │
        ├── YES ──→ docker logs
        │
        └── NO
             │
             ▼
        docker ps -a
             │
             ▼
        Container exited?
             │
             ▼
        docker logs
             │
             ▼
        Read actual error
             │
             ▼
        Identify root cause
```

This is the same debugging philosophy you've already practiced with your local FastAPI server.

The difference is simply **where the logs are now**.

---

# 37. Revision Checklist

- [ ] What is a Dockerfile?
- [ ] What does `FROM` do?
- [ ] What does `WORKDIR` do?
- [ ] What does `COPY` do?
- [ ] What does `RUN` do?
- [ ] What does `CMD` do?
- [ ] What does `EXPOSE` do?
- [ ] Why does Uvicorn use `0.0.0.0`?
- [ ] What does `-p 8000:8000` mean?
- [ ] Why doesn't `EXPOSE` publish the port?
- [ ] How do you build an image?
- [ ] How do you run a container?
- [ ] How do you inspect stopped containers?
- [ ] How do you inspect container logs?
- [ ] Why do we need `.dockerignore`?
- [ ] How does Docker fit around Clean Architecture?
- [ ] What happens after modifying application code?

---

# 38. Final Mental Model

```text
                    SOURCE CODE
                         │
                         ▼
                    Dockerfile
                         │
                    docker build
                         │
                         ▼
                  ┌─────────────┐
                  │    IMAGE    │
                  └──────┬──────┘
                         │
                    docker run
                         │
                         ▼
               ┌──────────────────┐
               │    CONTAINER     │
               │                  │
               │    Uvicorn       │
               │       ↓          │
               │    FastAPI       │
               │       ↓          │
               │    Application   │
               └────────┬─────────┘
                        │
                 Port 8000
                        │
                        ▼
                     Browser
```

Networking:

```text
localhost:8000
      │
      │ -p 8000:8000
      ▼
container:8000
      │
      ▼
Uvicorn 0.0.0.0:8000
      │
      ▼
FastAPI
```

---

# Key Takeaways

- A **Dockerfile** defines how our FastAPI image is built.
- `docker build` converts the Dockerfile and application context into an image.
- `docker run` creates and starts a container from that image.
- `RUN` happens during image construction; `CMD` runs when the container starts.
- `EXPOSE 8000` documents the intended container port but does **not** publish it.
- `-p 8000:8000` maps the host's port 8000 to the container's port 8000.
- Uvicorn listens on `0.0.0.0` so Docker can forward traffic to the application.
- `.dockerignore` prevents unnecessary and sensitive files from entering the build context.
- Container logs can be inspected with `docker logs`.
- Docker surrounds our Clean Architecture rather than becoming part of the Router/Service/Repository layers.
- Changing source code normally requires rebuilding the image and replacing the container.
- Today's FastAPI container still connects to the existing PostgreSQL instance; PostgreSQL containerization and Docker Compose come later.

---

# Project ₹50L — Architecture Evolution

```text
Day 017
Structured Logging
        │
        ▼
Day 019
Configuration
        │
        ▼
Day 021
Connection Pooling
        │
        ▼
Day 022
Database Indexing
        │
        ▼
Day 023
Docker Fundamentals
        │
        ▼
Day 024
🐳 Dockerized FastAPI
        │
        ▼
Day 025+
Docker + PostgreSQL
        │
        ▼
Docker Compose
        │
        ▼
Local Deployment
```

This is an important milestone: we have moved from **learning Docker conceptually** to **running our actual backend inside a container**.

The next step is to make the infrastructure more realistic: multiple services, environment configuration, networking, and eventually our PostgreSQL database running alongside the FastAPI container.
