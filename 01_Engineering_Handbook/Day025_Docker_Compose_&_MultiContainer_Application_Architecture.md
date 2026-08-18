# Day 025 — Docker Compose & Multi-Container Application Architecture

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 16 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Explain why Docker Compose exists.
- Understand single-container vs multi-container architecture.
- Understand `compose.yaml`, services, networks, volumes, and environment variables.
- Understand Compose service discovery and container-to-container communication.
- Explain why `localhost` is usually wrong for container-to-container communication.
- Understand why a service name such as `db` can be used as a hostname.
- Run, stop, rebuild, inspect, and troubleshoot a multi-container application.
- Connect the Dockerized FastAPI Student Management API to a PostgreSQL container.
- Understand how Docker Compose fits around our existing Clean Architecture.

---

# Big Picture

On Day 23 we learned Docker fundamentals.

On Day 24 we Dockerized our FastAPI application:

```text
Browser / Swagger
       |
       v
Host :8000
       |
       v
+----------------------+
| FastAPI Container    |
| Student Management   |
+----------+-----------+
           |
           | host.docker.internal
           v
      PostgreSQL
      on Host
```

This works, but the database is still outside Docker.

Today we move toward a real multi-container application:

```text
                 Docker Compose
                       |
          +------------+------------+
          |                         |
          v                         v
   +-------------+           +-------------+
   | FastAPI     |           | PostgreSQL  |
   | Container   |---------->| Container   |
   |             |  db:5432  |             |
   +-------------+           +-------------+
          |                         |
          +------ Docker Network ---+
```

Docker Compose lets us define and run this application stack from one declarative configuration.

---

# 1. What Is Docker Compose?

Docker Compose is a tool for defining and running multi-container applications.

Think:

```text
Docker
  -> runs containers

Docker Compose
  -> defines and coordinates an application made of containers
```

Without Compose:

```text
docker run ...
docker network create ...
docker run ...
docker volume create ...
docker run ...
```

With Compose:

```text
compose.yaml
     |
     v
docker compose up
     |
     +--> API
     +--> PostgreSQL
     +--> Network
     +--> Volumes
```

The important distinction is:

> `docker run` is primarily about running a container. Docker Compose is about describing and running an application stack.

---

# 2. The Compose Application Model

A Compose application is built from concepts such as:

```text
Compose Application
       |
       +--> Services
       +--> Networks
       +--> Volumes
       +--> Configuration
```

For our Student Management project:

```text
services:
    api
    db
```

So:

```text
api
 |
 +--> FastAPI container

db
 |
 +--> PostgreSQL container
```

---

# 3. What Is a Service?

A service is a definition of an application component that Compose runs as a container.

Example:

```yaml
services:

  api:
    build: .

  db:
    image: postgres:latest
```

There are two services:

```text
api -> FastAPI
db  -> PostgreSQL
```

The service name is important because it also becomes the logical hostname other Compose services can use.

---

# 4. Our Multi-Container Architecture

The target architecture is:

```text
                         HOST
                          |
                    localhost:8000
                          |
                          v
              +------------------------+
              |     Docker Compose     |
              |                        |
              | +--------------------+ |
              | | API Service        | |
              | | FastAPI Container   | |
              | +---------+----------+ |
              |           |            |
              |           | db:5432    |
              |           v            |
              | +--------------------+ |
              | | DB Service         | |
              | | PostgreSQL         | |
              | +---------+----------+ |
              |           |            |
              |           v            |
              |    postgres_data       |
              |       Volume           |
              +------------------------+
```

The key change from Day 24 is that PostgreSQL is now another container.

---

# 5. Docker Compose Networking

Compose creates a network for the application.

Conceptually:

```text
              Docker Network
                    |
          +---------+---------+
          |                   |
          v                   v
       +------+            +------+
       | api  |            | db   |
       |      |----------->|      |
       +------+            +------+
```

The API container can communicate with the database container through this internal network.

---

# 6. Service Discovery

Suppose our Compose file says:

```yaml
services:

  api:
    ...

  db:
    ...
```

The database service is named:

```text
db
```

The API can therefore use:

```env
DB_HOST=db
```

The flow is:

```text
FastAPI container
       |
       | "db"
       v
Docker internal DNS
       |
       v
PostgreSQL container
```

The application does not need to know the database container's IP address.

---

# 7. Why `localhost` Is Wrong

This is one of the most important Docker concepts.

Inside the FastAPI container:

```text
localhost
   |
   v
THIS container
```

It does NOT mean:

```text
localhost
   |
   v
another container
```

Therefore, if PostgreSQL is running in another container:

```env
DB_HOST=localhost
```

usually causes the FastAPI container to look for PostgreSQL inside itself.

The result is commonly:

```text
Connection refused
```

---

# 8. Why `DB_HOST=db` Works

With:

```yaml
services:
  api:
    ...

  db:
    ...
```

Docker's internal DNS allows:

```text
api container
      |
      | db
      v
Docker DNS
      |
      v
db service
      |
      v
PostgreSQL container
```

Therefore:

```env
DB_HOST=db
```

is the correct logical configuration.

This is the proper multi-container equivalent of the Day 24 `host.docker.internal` workaround.

---

# 9. Service Name vs Container IP

Avoid:

```env
DB_HOST=172.18.0.5
```

Container IP addresses can change when containers are recreated.

Prefer:

```env
DB_HOST=db
```

because:

```text
Service name
     |
     v
Docker DNS
     |
     v
Current container IP
```

This is a general engineering principle:

> Applications should depend on logical service identities rather than ephemeral infrastructure addresses.

---

# 10. The `compose.yaml` File

A minimal starting point:

```yaml
services:

  api:
    build: .
    ports:
      - "8000:8000"

  db:
    image: postgres:latest
```

The important parts are:

```text
services
  |
  +--> api
  |     +--> build
  |     +--> ports
  |
  +--> db
        +--> image
```

---

# 11. `build`

For the API:

```yaml
api:
  build: .
```

means Compose builds the image using the Dockerfile in the current directory.

Flow:

```text
Dockerfile
    |
    v
Build
    |
    v
FastAPI Image
    |
    v
API Container
```

---

# 12. `image`

For PostgreSQL:

```yaml
db:
  image: postgres:latest
```

means Compose uses an existing PostgreSQL image rather than building PostgreSQL from our project Dockerfile.

---

# 13. Ports

For the API:

```yaml
ports:
  - "8000:8000"
```

means:

```text
Host :8000
     |
     v
Container :8000
```

Therefore:

```text
http://localhost:8000/docs
```

can reach Swagger.

---

# 14. Does PostgreSQL Need `5432:5432`?

Not necessarily.

The API and database communicate through the internal Docker network:

```text
FastAPI
   |
   | db:5432
   v
PostgreSQL
```

Therefore PostgreSQL does not need its port published to the host merely for API-to-database communication.

We might publish:

```yaml
ports:
  - "5432:5432"
```

during development if pgAdmin, DBeaver, or another host application needs direct access.

But internal container communication does not require host port publishing.

---

# 15. Environment Variables

Day 19 taught us centralized configuration.

The flow was:

```text
.env
  |
  v
Pydantic Settings
  |
  v
Application
```

Docker Compose adds another layer:

```text
.env / Compose configuration
          |
          v
Container Environment
          |
          v
Pydantic Settings
          |
          v
FastAPI
```

Example:

```yaml
environment:
  DB_HOST: db
```

or:

```yaml
env_file:
  - .env
```

Never commit a real `.env` containing passwords, JWT secrets, or database credentials.

Use `.env.example` for documentation.

---

# 16. PostgreSQL Service Configuration

Conceptually:

```yaml
db:
  image: postgres:latest
  environment:
    POSTGRES_DB: student_db
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: <secret>
```

The API then connects with:

```text
Host     = db
Port     = 5432
Database = student_db
User     = postgres
Password = configured secret
```

---

# 17. Persistent Volumes

Containers are disposable.

We do not want database data to depend on the lifetime of the PostgreSQL container.

Without a volume:

```text
PostgreSQL container
       |
       v
container deleted
       |
       v
database data may disappear
```

With a volume:

```text
PostgreSQL container
       |
       v
Docker Volume
       |
       v
Persistent database data
```

Example:

```yaml
services:

  db:
    image: postgres:latest
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Important mental model:

```text
Container lifecycle
       !=
Data lifecycle
```

---

# 18. Complete Application Architecture

```text
                         USER
                          |
                          v
                    Swagger / Client
                          |
                          | localhost:8000
                          v
              +--------------------------+
              |      Docker Compose      |
              |                          |
              |  +--------------------+  |
              |  | API Container      |  |
              |  |                    |  |
              |  | Middleware         |  |
              |  | Router             |  |
              |  | Service            |  |
              |  | Repository         |  |
              |  | Database Helper    |  |
              |  | Connection Pool    |  |
              |  +---------+----------+  |
              |            |             |
              |            | db:5432     |
              |            v             |
              |  +--------------------+  |
              |  | PostgreSQL         |  |
              |  | Container          |  |
              |  +---------+----------+  |
              |            |             |
              |            v             |
              |      Persistent Volume  |
              +--------------------------+
```

Docker Compose sits around our application. It does not replace Clean Architecture.

---

# 19. How Compose Fits Clean Architecture

Our application still follows:

```text
Router
   |
   v
Service
   |
   v
Repository
   |
   v
Database Helper
   |
   v
Connection Pool
   |
   v
PostgreSQL
```

Docker provides the runtime environment:

```text
+----------------------------------------+
| Docker Compose                         |
|                                        |
|   +-------------------------------+    |
|   | FastAPI Application Container  |    |
|   +---------------+---------------+    |
|                   |                    |
|                   v                    |
|   +-------------------------------+    |
|   | PostgreSQL Container           |    |
|   +-------------------------------+    |
|                                        |
+----------------------------------------+
```

Docker is therefore a deployment/runtime concern, not a replacement for application architecture.

---

# 20. Essential Compose Commands

Start:

```bash
docker compose up
```

Start in background:

```bash
docker compose up -d
```

Build:

```bash
docker compose build
```

Build and start:

```bash
docker compose up --build
```

Show services:

```bash
docker compose ps
```

Show all logs:

```bash
docker compose logs
```

Show API logs:

```bash
docker compose logs api
```

Follow API logs:

```bash
docker compose logs -f api
```

Stop and remove Compose containers/network:

```bash
docker compose down
```

---

# 21. What Happens During `docker compose up`?

Conceptually:

```text
docker compose up
        |
        v
Read compose.yaml
        |
        v
Build / Pull Images
        |
        v
Create Network
        |
        v
Create Volumes
        |
        v
Create Containers
        |
        v
Start Services
        |
        v
Enable Service Discovery
        |
        v
Application Stack Running
```

This is the mental model to remember.

---

# 22. Troubleshooting Workflow

Suppose Swagger returns:

```text
500 Internal Server Error
```

Do not guess.

Use the logging workflow from Day 17:

```text
Swagger
   |
   v
500
   |
   v
docker compose logs api
   |
   v
Actual application error
   |
   v
Root cause
   |
   v
Fix
   |
   v
docker compose up --build
   |
   v
Test again
```

For database connectivity failures, check:

```text
DB_HOST
DB_PORT
DB credentials
db service status
Compose network
PostgreSQL logs
API logs
```

---

# 23. Common Beginner Mistakes

## Mistake 1 — Using `localhost`

```env
DB_HOST=localhost
```

Wrong when PostgreSQL is another container.

Use:

```env
DB_HOST=db
```

---

## Mistake 2 — Using container IP addresses

```env
DB_HOST=172.18.0.5
```

Fragile because container IPs can change.

Use the service name.

---

## Mistake 3 — Thinking `EXPOSE` publishes a port

```dockerfile
EXPOSE 8000
```

documents the intended container port.

Host publishing requires:

```yaml
ports:
  - "8000:8000"
```

---

## Mistake 4 — Publishing every internal service

PostgreSQL does not automatically need:

```yaml
ports:
  - "5432:5432"
```

if only the API container needs access.

---

## Mistake 5 — Forgetting database persistence

Use a volume for database data.

---

## Mistake 6 — Committing secrets

Never commit a real `.env`.

Use `.env.example`.

---

# 24. Docker Run vs Docker Compose

| Docker CLI | Docker Compose |
|---|---|
| Best for individual containers | Best for application stacks |
| Configuration through CLI flags | Configuration in YAML |
| Networking managed manually | Compose-managed networking |
| Manual environment setup | Declarative environment setup |
| Good for experiments | Good for multi-container development |

Mental model:

```text
docker run
    |
    v
"Run this container."

docker compose
    |
    v
"Run this application."
```

---

# 25. Production Thinking

Docker Compose is especially useful for local development, testing, and smaller deployments.

At larger production scale, additional orchestration and infrastructure concerns appear, such as:

```text
Secrets
Health checks
Restart policies
Observability
Scaling
Load balancing
Service discovery
CI/CD
Container orchestration
```

Do not jump to Kubernetes yet.

Our roadmap intentionally builds the foundation first.

---

# 26. Enterprise Mapping

A real enterprise application may contain:

```text
API
 |
 +--> PostgreSQL
 +--> Redis
 +--> Message Broker
 +--> Background Worker
 +--> Search
 +--> Monitoring
```

Docker Compose lets us model these components as services.

The underlying engineering principles remain the same across Python, .NET, Java, Node.js, and other stacks:

- Containerization
- Configuration
- Networking
- Persistent storage
- Logging
- Deployment automation

---

# 27. Interview Questions

### Q1. What is Docker Compose?

Docker Compose is a tool for defining and running multi-container applications using a declarative Compose file.

### Q2. Why do we need Docker Compose?

It simplifies management of multiple containers, networks, volumes, environment variables, and services by defining the application stack in one configuration.

### Q3. What is a service?

A service is a definition of an application component that Compose runs as a container.

### Q4. How do containers communicate in Compose?

Compose creates a network and provides service discovery. Containers can communicate using service names as hostnames.

### Q5. Why doesn't `localhost` work for container-to-container communication?

Because `localhost` inside a container refers to that container itself.

### Q6. Why does `db` work as the database hostname?

Because `db` is the Compose service name and Docker's internal DNS resolves it to the corresponding container.

### Q7. Does PostgreSQL need to publish port 5432?

No, not merely for communication with other containers on the same Compose network.

### Q8. Why do databases need volumes?

Containers are disposable; volumes separate persistent data from container lifecycle.

### Q9. What is the difference between `build` and `image`?

`build` tells Compose to build an image from a Dockerfile/context. `image` tells Compose to use an existing image.

### Q10. How would you troubleshoot a Compose application returning HTTP 500?

Start with:

```bash
docker compose logs api
```

Then identify the root cause, fix it, rebuild/restart as needed, and verify again.

---

# 28. FastAPI ↔ ASP.NET Core Mapping

The concepts are framework-independent.

For .NET:

```text
Dockerfile
    |
    v
ASP.NET Core Image
    |
    v
Container
```

A Compose stack might be:

```text
ASP.NET Core API
       +
SQL Server
       +
Redis
```

The framework changes.

The engineering principles do not.

---

# 29. Final Mental Model

Remember this:

```text
                 Docker Compose
                       |
        +--------------+--------------+
        |                             |
        v                             v
      API                             DB
   Container                       Container
        |                             |
        +------ Docker Network -------+
                       |
                 Service DNS
                       |
                  api -> db:5432
```

And the most important rule:

```text
Inside a container:

localhost
    |
    v
THIS container

service name
    |
    v
ANOTHER Compose service
```

Therefore:

```text
DB_HOST=localhost
```

means:

> Find PostgreSQL inside the FastAPI container.

Whereas:

```text
DB_HOST=db
```

means:

> Find the Compose service named `db`.

---

# 30. Cheat Sheet

```text
Docker
-> Container runtime

Dockerfile
-> Instructions for building an image

Image
-> Template for containers

Container
-> Running instance of an image

Docker Compose
-> Define and run multi-container applications

compose.yaml
-> Declarative application stack configuration

Service
-> Application component/container definition

Network
-> Enables container-to-container communication

Service name
-> Internal hostname

Volume
-> Persistent storage

ports
-> Host <-> Container port publishing

environment
-> Define container environment variables

env_file
-> Load environment variables from a file

docker compose up
-> Start application stack

docker compose up -d
-> Start in background

docker compose up --build
-> Rebuild and start

docker compose ps
-> Show Compose services

docker compose logs
-> Show logs

docker compose down
-> Stop/remove Compose resources
```

---

# Final Takeaway

Docker answers:

> **"How do I package and run this application?"**

Docker Compose answers:

> **"How do I define and run this entire application stack?"**

The most important networking idea from today:

```text
Container A
     |
     | service name
     v
Container B
```

not:

```text
Container A
     |
     | localhost
     v
Container B
```

Our Student Management project has now evolved through:

```text
Python Application
       |
       v
PostgreSQL-backed Application
       |
       v
Clean Architecture
       |
       v
FastAPI Backend
       |
       v
Authentication / Middleware / Logging
       |
       v
Transactions / Pooling / Query Optimization
       |
       v
Dockerized FastAPI
       |
       v
Multi-Container Application
       |
       v
Docker Compose
```

This is the foundation we need before moving deeper into scalable deployment and systems engineering.
