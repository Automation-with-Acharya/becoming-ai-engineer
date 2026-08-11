# Day 023 — Docker Fundamentals

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 09 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Explain what Docker is and why it exists.
- Explain the problem containers solve.
- Understand Containers vs Virtual Machines.
- Understand Docker Images and Containers.
- Understand Docker Engine and Docker CLI.
- Understand Docker Registries and Docker Hub.
- Run and inspect Docker containers.
- Understand the basic Docker lifecycle.
- Explain how Docker will eventually fit into the Student Management backend.
- Explain Docker fundamentals confidently in an interview.

---

# 1. Why Does Docker Exist?

Imagine that our Student Management application requires:

```text
Python 3.x

FastAPI

Psycopg

Pydantic

Other dependencies

Environment variables

PostgreSQL
```

On our machine:

```text
FastAPI Application

↓

Python installed

↓

Dependencies installed

↓

PostgreSQL configured

↓

Application works
```

Now another developer downloads the project.

Their machine has:

```text
Python 3.12
```

while yours has:

```text
Python 3.14
```

They install a slightly different version of a dependency.

Something breaks.

Then we hear the famous sentence:

> "But it works on my machine."

Docker helps solve this class of environment-consistency problem.

---

# 2. What is Docker?

Docker is a platform for developing, packaging, and running applications using **containers**.

The central idea is:

```text
Application

+

Dependencies

+

Runtime Configuration

↓

Container Image

↓

Run Anywhere Docker is Available
```

Instead of asking another machine to recreate your environment manually, we package the application environment into an image.

---

# 3. The Core Docker Mental Model

The most important relationship to remember:

```text
Dockerfile

↓

Build

↓

Docker Image

↓

Run

↓

Docker Container
```

Think of it like this:

```text
Recipe

↓

Cake Blueprint

↓

Actual Cake
```

Docker equivalent:

```text
Dockerfile

↓

Image

↓

Container
```

---

# 4. Dockerfile

A **Dockerfile** is a text file containing instructions for building a Docker image.

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

This does not represent a running application.

It describes **how to construct the image**.

---

# Dockerfile Flow

```text
Dockerfile

   │
   │ docker build
   ▼

Docker Image

   │
   │ docker run
   ▼

Docker Container
```

---

# 5. Docker Image

A Docker image is a packaged, immutable template used to create containers.

It contains everything required to run the application, such as:

- Application code
- Runtime
- Installed dependencies
- Required filesystem structure
- Configuration defaults

Conceptually:

```text
┌─────────────────────────────┐
│       Docker Image          │
│                             │
│ Python Runtime              │
│ FastAPI                     │
│ psycopg                     │
│ Pydantic                    │
│ Application Code            │
│ Dependencies                │
└─────────────────────────────┘
```

An image is **not itself the running application**.

---

# 6. Docker Container

A container is a running instance of an image.

```text
Image

↓

docker run

↓

Container
```

For example:

```bash
docker run hello-world
```

Docker takes the `hello-world` image and creates a container from it.

---

# Image vs Container

| Image                      | Container                       |
| -------------------------- | ------------------------------- |
| Template                   | Running instance                |
| Immutable package          | Runtime environment             |
| Built                      | Created from image              |
| Can create many containers | Represents one running instance |
| Stored locally/registry    | Exists on Docker host           |

Mental model:

```text
          IMAGE

        ┌───────┐
        │ App   │
        │ Python│
        │ Deps  │
        └───────┘
           │
      ┌────┴────┐
      ▼         ▼
 Container   Container
    #1          #2
```

One image can create multiple containers.

---

# 7. Docker Engine

Docker Engine is the underlying technology that builds and runs containers.

Simplified architecture:

```text
Developer

    │
    ▼
Docker CLI

    │
    ▼
Docker Engine

    │
    ├─────────────┐
    ▼             ▼
 Images       Containers
```

When you execute:

```bash
docker run hello-world
```

the Docker CLI communicates with the Docker Engine, which performs the requested operation.

---

# 8. Docker CLI

The Docker CLI is the command-line interface through which we interact with Docker.

Examples:

```bash
docker --version
```

```bash
docker images
```

```bash
docker ps
```

```bash
docker ps -a
```

```bash
docker pull hello-world
```

```bash
docker run hello-world
```

The CLI is the interface.

The Engine performs the underlying work.

---

# 9. Your First Container

Run:

```bash
docker run hello-world
```

Conceptually:

```text
docker run

↓

Does image exist locally?

↓

No

↓

Pull image

↓

Create container

↓

Start container

↓

Application runs

↓

Container exits
```

The `hello-world` example normally finishes immediately, so the container exits after displaying its message.

---

# 10. Docker Images

List locally available images:

```bash
docker images
```

or:

```bash
docker image ls
```

You may see:

```text
REPOSITORY      TAG       IMAGE ID
hello-world     latest    ...
```

Important concepts:

### Repository

The image name.

Example:

```text
hello-world
```

### Tag

A version/variant label.

Example:

```text
latest
```

### Image ID

A unique identifier for the image.

---

# 11. Docker Containers

List running containers:

```bash
docker ps
```

List all containers, including stopped ones:

```bash
docker ps -a
```

This distinction is important.

```text
docker ps

↓

Currently running
```

```text
docker ps -a

↓

Running + Stopped
```

---

# Container Lifecycle

A container can conceptually move through:

```text
Created

   ↓

Running

   ↓

Stopped

   ↓

Removed
```

For a short-lived container:

```text
Created

↓

Running

↓

Exited
```

The container isn't necessarily deleted just because its process stopped.

---

# 12. Docker Registry

A registry stores Docker images.

Conceptually:

```text
Developer

↓

docker push

↓

Docker Registry

↓

docker pull

↓

Another Machine
```

One famous public registry is **Docker Hub**.

Docker Hub:

[Docker Hub](https://hub.docker.com/)

---

# Image Distribution

Imagine we build our Student Management API:

```text
Developer Machine

↓

Docker Image

↓

Push

↓

Docker Hub / Private Registry

↓

Production Server

↓

Pull Image

↓

Run Container
```

This is one of the major reasons containers are useful in deployment pipelines.

---

# 13. Containers vs Virtual Machines

This is one of the most important Docker interview questions.

## Virtual Machine

```text
Physical Machine

↓

Host OS

↓

Hypervisor

├── VM 1
│    └── Guest OS
│         └── Application
│
├── VM 2
│    └── Guest OS
│         └── Application
│
└── VM 3
     └── Guest OS
          └── Application
```

Each VM includes a complete guest operating system.

---

# Containers

```text
Physical Machine

↓

Host OS

↓

Container Runtime

├── Container 1
│    └── Application
│
├── Container 2
│    └── Application
│
└── Container 3
     └── Application
```

Containers share the host operating system's kernel while providing isolated user-space environments.

---

# VM vs Container

| Virtual Machine           | Container                           |
| ------------------------- | ----------------------------------- |
| Includes guest OS         | Shares host kernel                  |
| Heavier                   | Lightweight                         |
| Usually slower to start   | Usually starts quickly              |
| Strong OS-level isolation | Process-level/application isolation |
| Larger resource footprint | Smaller resource footprint          |

The important point:

> A container is not simply a lightweight virtual machine.

That distinction matters.

---

# 14. Docker Architecture

Our mental model:

```text
                     Developer
                         │
                         ▼
                   Docker CLI
                         │
                         ▼
                  Docker Engine
                  /            \
                 /              \
                ▼                ▼
             Images          Containers
                │                │
                │                │
                └──────┬─────────┘
                       │
                       ▼
                 Application
```

---

# 15. Docker and Our FastAPI Application

Today our application runs directly on Windows:

```text
Windows

↓

Python

↓

FastAPI

↓

Application
```

After Dockerization:

```text
Windows

↓

Docker

↓

FastAPI Container

┌─────────────────────────┐
│ Python                  │
│ FastAPI                 │
│ psycopg                 │
│ Pydantic                │
│ Application Code        │
└─────────────────────────┘
```

The host machine no longer needs to manually recreate every Python dependency inside the container.

---

# 16. Our Future Architecture

We are eventually moving toward:

```text
                  Client
                    │
                    ▼
              FastAPI Container
                    │
                    ▼
              Service Layer
                    │
                    ▼
             Repository Layer
                    │
                    ▼
             Connection Pool
                    │
                    ▼
            PostgreSQL Container
```

This is where Docker becomes especially useful.

Our application and database can run as isolated services.

Later, Docker Compose will allow us to manage these services together.

---

# 17. Why We Didn't Start Docker Earlier

This is important for your learning journey.

We deliberately waited.

Earlier, you would have learned:

```text
Docker

↓

Commands

↓

Containers

↓

Images
```

without having a meaningful application to containerize.

Now you already understand:

```text
FastAPI
PostgreSQL
Configuration
Environment Variables
Connection Pool
Logging
Transactions
Indexes
```

So Docker now answers a real question:

> "How do I package and run this backend consistently?"

This makes the concept much easier to understand.

---

# 18. Basic Docker Commands

## Check Docker Version

```bash
docker --version
```

---

## List Images

```bash
docker images
```

or:

```bash
docker image ls
```

---

## List Running Containers

```bash
docker ps
```

---

## List All Containers

```bash
docker ps -a
```

---

## Download an Image

```bash
docker pull hello-world
```

---

## Run a Container

```bash
docker run hello-world
```

---

## Stop a Container

```bash
docker stop <container_id>
```

---

## Remove a Container

```bash
docker rm <container_id>
```

---

## Remove an Image

```bash
docker rmi <image_id>
```

Don't memorize all commands today.

Understand what each operation represents.

---

# 19. Dockerfile Example for FastAPI

We will eventually create something similar to:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Let's understand the instructions.

---

## `FROM`

```dockerfile
FROM python:3.12-slim
```

Defines the base image.

We're starting from a lightweight Python environment.

---

## `WORKDIR`

```dockerfile
WORKDIR /app
```

Sets the working directory inside the image/container.

---

## `COPY`

```dockerfile
COPY requirements.txt .
```

Copies files from the build context into the image.

---

## `RUN`

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

Executes a command while building the image.

---

## `CMD`

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Defines the default command used when the container starts.

---

# 20. Build vs Run

This distinction is extremely important.

### Build

```bash
docker build
```

Creates:

```text
Dockerfile

↓

Image
```

### Run

```bash
docker run
```

Creates:

```text
Image

↓

Container
```

Therefore:

```text
docker build

Dockerfile → Image
```

while:

```text
docker run

Image → Container
```

---

# 21. Environment Variables

Remember our Day 019 work.

We should **not** put secrets directly inside a Dockerfile.

Bad:

```dockerfile
ENV DATABASE_PASSWORD=mysecretpassword
```

Instead:

```text
Container

↓

Environment Variables

↓

Application Configuration

↓

Database
```

For example:

```text
DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
```

Docker fits naturally with the configuration system we already built.

---

# 22. Docker + Clean Architecture

Docker does not replace Clean Architecture.

It sits outside the application architecture.

```text
┌──────────────────────────────────────┐
│           Docker Container           │
│                                      │
│   ┌──────────────────────────────┐   │
│   │          FastAPI App         │   │
│   │                              │   │
│   │ Router                       │   │
│   │   ↓                          │   │
│   │ Service                      │   │
│   │   ↓                          │   │
│   │ Repository                   │   │
│   │   ↓                          │   │
│   │ Connection Pool              │   │
│   └──────────────────────────────┘   │
└──────────────────────────────────────┘
                    │
                    ▼
              PostgreSQL
```

Docker is the **deployment/runtime boundary**.

Clean Architecture is the **application design boundary**.

These solve different problems.

---

# 23. Docker + Connection Pool

We learned connection pooling on Day 021.

Now combine the concepts:

```text
FastAPI Container

        │
        ▼
Application Lifespan

        │
        ▼
Connection Pool

        │
        ▼
PostgreSQL
```

When the container starts:

```text
Container Starts

↓

FastAPI Starts

↓

Lifespan Startup

↓

Create Connection Pool

↓

Application Ready
```

When the container stops:

```text
Container Shutdown

↓

FastAPI Shutdown

↓

Lifespan Shutdown

↓

Close Connection Pool
```

This is why today's Docker topic connects directly with Day 021.

---

# 24. Docker + Logging

Our structured logging from Day 017 also becomes important.

A production container should generally write logs in a way that the container runtime/platform can collect.

Conceptually:

```text
FastAPI

↓

Logger

↓

Container stdout/stderr

↓

Docker / Platform

↓

Centralized Logging
```

We don't want debugging to depend on manually opening files inside containers.

---

# 25. Docker + PostgreSQL

Eventually we can run:

```text
┌─────────────────────────┐
│ FastAPI Container       │
│                         │
│ Application             │
└────────────┬────────────┘
             │
             │ Network
             ▼
┌─────────────────────────┐
│ PostgreSQL Container    │
│                         │
│ Database                │
└─────────────────────────┘
```

The containers communicate through a Docker network.

We will learn the practical implementation with **Docker Compose** later.

---

# 26. Why Containers Help Deployment

Without Docker:

```text
Production Server

↓

Install Python

↓

Install Dependencies

↓

Configure Environment

↓

Copy Application

↓

Configure Runtime

↓

Hope Everything Matches
```

With Docker:

```text
Build Image

↓

Push Image

↓

Production Server

↓

Pull Image

↓

Run Container
```

The environment becomes reproducible.

---

# 27. Container Isolation

Containers provide isolation between applications.

For example:

```text
Server

├── FastAPI Container
│
├── Redis Container
│
├── PostgreSQL Container
│
└── Worker Container
```

Each service has its own filesystem/process environment.

This makes service boundaries clearer.

---

# 28. Container ≠ Permanent Server

Containers are designed to be replaceable.

A healthy deployment mindset is:

```text
Old Container

↓

Stop

↓

Remove

↓

Start New Container

↓

Same Image
```

The application should not depend on manually modifying a running container.

Instead:

> Build a new image and replace the container.

---

# 29. Immutable Infrastructure Mental Model

Think:

```text
Don't repair container.

↓

Build corrected image.

↓

Deploy new container.
```

This creates predictable deployments.

---

# 30. Common Beginner Mistakes

### ❌ Treating containers like VMs

A container isn't a miniature complete operating system.

---

### ❌ Editing application files manually inside a running container

Those changes are generally not how production deployments should be managed.

Change the source.

Build a new image.

---

### ❌ Putting passwords inside Dockerfiles

Use environment variables/secrets.

---

### ❌ Assuming an image is a container

Image:

```text
Template
```

Container:

```text
Running instance
```

---

### ❌ Installing Docker and immediately learning Kubernetes

Don't.

First become comfortable with:

```text
Docker

↓

Dockerfile

↓

Images

↓

Containers

↓

Networking

↓

Volumes

↓

Docker Compose
```

Then Kubernetes becomes much easier.

---

# 31. Docker vs Kubernetes

They are not the same thing.

Docker:

> Containerization and container runtime tooling.

Kubernetes:

> Container orchestration platform.

Conceptually:

```text
Docker

↓

Run Containers
```

while:

```text
Kubernetes

↓

Manage Many Containers

↓

Scaling

↓

Networking

↓

Health Checks

↓

Rolling Deployments
```

Kubernetes comes much later in our roadmap.

---

# 32. Interview Questions

## Q1. What is Docker?

Docker is a platform for packaging and running applications in containers, providing a consistent runtime environment across development, testing, and deployment environments.

---

## Q2. What is a container?

A container is an isolated runtime instance created from a Docker image.

---

## Q3. What is a Docker image?

An image is an immutable package/template containing the application and its required runtime/dependencies, from which containers are created.

---

## Q4. Image vs Container?

```text
Image = Template

Container = Running Instance
```

---

## Q5. What is a Dockerfile?

A Dockerfile is a text file containing instructions used to build a Docker image.

---

## Q6. What is Docker Engine?

Docker Engine is the underlying containerization technology responsible for building and running containers.

---

## Q7. What is Docker Hub?

Docker Hub is a public registry for storing and distributing Docker images.

---

## Q8. Docker vs VM?

A VM virtualizes an entire machine and normally includes a guest OS.

Containers share the host kernel and isolate application processes, making them generally lighter and faster to start.

---

## Q9. Why use Docker?

To create reproducible application environments and reduce differences between development, testing, and production environments.

---

## Q10. What happens when you run `docker run hello-world`?

Conceptually:

```text
Docker CLI

↓

Docker Engine

↓

Check Image

↓

Pull if Missing

↓

Create Container

↓

Start Container

↓

Application Runs

↓

Container Exits
```

---

# 33. Cheat Sheet

## Fundamental Relationship

```text
Dockerfile

    ↓ build

Docker Image

    ↓ run

Docker Container
```

---

## Architecture

```text
Developer

↓

Docker CLI

↓

Docker Engine

├── Images
│
└── Containers
```

---

## Core Commands

```bash
docker --version

docker images

docker ps

docker ps -a

docker pull <image>

docker run <image>

docker stop <container>

docker rm <container>

docker rmi <image>
```

---

# 34. Why Does Docker Exist?

## Problem

Applications depend on:

- Runtime versions
- Libraries
- Dependencies
- Configuration
- OS-level assumptions

Different environments can behave differently.

---

## Solution

Package the application environment into a reproducible image.

```text
Application

+

Dependencies

+

Runtime

↓

Image

↓

Consistent Container
```

---

# 35. Who Depends on Docker?

Docker is outside our application layers.

```text
                 Docker
┌──────────────────────────────────┐
│                                  │
│          FastAPI Application     │
│                                  │
│ Router                           │
│   ↓                              │
│ Service                          │
│   ↓                              │
│ Repository                       │
│   ↓                              │
│ Connection Pool                  │
│                                  │
└──────────────────────────────────┘
```

Docker packages and runs the entire application.

It doesn't belong inside the Router, Service, or Repository layer.

---

# 36. Our Student Management Evolution

### Early Project

```text
Python

↓

Text File
```

### Database Project

```text
Python

↓

psycopg

↓

PostgreSQL
```

### Current Backend

```text
FastAPI

↓

Clean Architecture

↓

Repository

↓

Connection Pool

↓

PostgreSQL
```

### Dockerized Backend

```text
Docker

┌─────────────────────────────┐
│ FastAPI Container           │
│                             │
│ FastAPI                     │
│ Clean Architecture          │
│ Connection Pool             │
└──────────────┬──────────────┘
               │
               ▼
       PostgreSQL Container
```

### Future

```text
Docker Compose

↓

FastAPI

+

PostgreSQL

+

Other Services
```

---

# 37. Engineering Principle

Today's most important principle:

> **Build once, run consistently.**

Instead of manually recreating the environment on every machine:

```text
Machine A
Machine B
Machine C
Production
```

we create:

```text
One Image

↓

Many Containers
```

---

# Revision Checklist

Before considering Docker fundamentals mastered, make sure you can answer these without notes:

- [ ] What problem does Docker solve?
- [ ] What is a container?
- [ ] What is an image?
- [ ] What is a Dockerfile?
- [ ] What is Docker Engine?
- [ ] What does Docker CLI do?
- [ ] What is Docker Hub?
- [ ] What happens during `docker run`?
- [ ] Difference between image and container?
- [ ] Difference between container and VM?
- [ ] What happens during `docker build`?
- [ ] Why shouldn't secrets be hardcoded in Dockerfiles?
- [ ] How will Docker eventually run our FastAPI application?
- [ ] Why does Docker fit naturally with our existing configuration and lifespan architecture?

---

# Final Mental Model

If you remember only one diagram from Day 023, remember this:

```text
                 DOCKER

              Dockerfile
                   │
                   │ docker build
                   ▼
             ┌───────────┐
             │   IMAGE   │
             └─────┬─────┘
                   │
                   │ docker run
                   ▼
             ┌───────────┐
             │ CONTAINER │
             └─────┬─────┘
                   │
                   ▼
             APPLICATION
```

And for our actual project:

```text
                 Docker
                   │
                   ▼
        ┌─────────────────────┐
        │   FastAPI Container │
        │                     │
        │ Router              │
        │   ↓                 │
        │ Service             │
        │   ↓                 │
        │ Repository          │
        │   ↓                 │
        │ Connection Pool     │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ PostgreSQL          │
        │ Container            │
        └─────────────────────┘
```

---

# Key Takeaways

- Docker packages applications into reproducible containers.
- A **Dockerfile builds an image**.
- An **image creates containers**.
- Docker Engine performs the underlying container operations.
- Docker CLI is the interface used to interact with Docker.
- Containers are generally lighter than virtual machines because they share the host kernel.
- Docker helps eliminate environment inconsistencies between development and production.
- Docker is a deployment/runtime concern and does not replace Clean Architecture.
- Environment variables and secrets should be supplied separately rather than hardcoded into images.
- Our existing configuration, logging, connection pooling, and FastAPI Lifespan concepts all fit naturally into a containerized application.
- Docker Compose and more advanced container orchestration will come later; today's goal is to establish a strong Docker mental model.

---

# Project ₹50L — Architecture Evolution

```text
Day 09
Clean Architecture
        │
        ▼
Day 12
Dependency Injection
        │
        ▼
Day 15
JWT Authentication
        │
        ▼
Day 17
Structured Logging
        │
        ▼
Day 18
Global Exception Handling
        │
        ▼
Day 19
Configuration
        │
        ▼
Day 20
Transactions
        │
        ▼
Day 21
Connection Pooling
        │
        ▼
Day 22
Database Indexing
        │
        ▼
Day 23
🐳 Docker Fundamentals
```

This is an important transition point.

We are moving from:

> **"How do I build the backend?"**

toward:

> **"How do I package, run, deploy, and eventually scale the backend?"**

That is the beginning of the systems-engineering side of Project ₹50L.

---

# Tomorrow's Preview

## Day 024

**Dockerizing the FastAPI Application**

We'll move from:

```text
"I understand Docker"
```

to:

```text
"My FastAPI application actually runs inside Docker."
```

The focus will be:

- Creating our first project `Dockerfile`
- Building the FastAPI image
- Running the FastAPI container
- Port mapping
- Container environment variables
- `.dockerignore`
- Inspecting container logs
- Testing Swagger UI through the container
- Understanding the complete request flow through Docker
