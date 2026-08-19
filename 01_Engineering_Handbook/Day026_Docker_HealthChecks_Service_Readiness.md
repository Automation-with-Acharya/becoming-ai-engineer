# Day 026 — Docker Health Checks & Service Readiness

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 19 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Explain the difference between a container being **running** and a service being **ready**.
- Understand why `depends_on` by itself is not enough for reliable startup sequencing.
- Understand Docker `HEALTHCHECK`.
- Understand `service_started`, `service_healthy`, and `service_completed_successfully`.
- Configure a PostgreSQL health check in Docker Compose.
- Make the FastAPI service wait for PostgreSQL to become healthy.
- Inspect container health status.
- Troubleshoot unhealthy services using Compose status and logs.
- Understand why readiness checks matter in production systems.
- Connect Docker health checks to larger concepts such as load balancers, orchestration, microservices, and Kubernetes.

---

# Big Picture

On Day 25, our application became a real multi-container system:

```text
                         Docker Compose
                              |
                +-------------+-------------+
                |                           |
                v                           v
        +---------------+           +---------------+
        | FastAPI       |           | PostgreSQL    |
        | Container     |---------->| Container     |
        +---------------+   db:5432 +---------------+
                                          |
                                          v
                                   Persistent Volume
```

That architecture works.

But there is an important problem.

When Compose starts services, a dependency can be **running** before it is actually **ready to serve requests**.

For example:

```text
PostgreSQL Container
        |
        v
Process starts
        |
        | still initializing...
        |
        v
FastAPI starts
        |
        v
Database connection attempted
        |
        v
❌ Connection failure
```

Docker Compose documentation explicitly notes that Compose normally waits only until a dependency is running, not until it is ready; `service_healthy` combined with a `healthcheck` is the mechanism for readiness-aware startup. citeturn873023view0

Today's goal is therefore:

```text
Container Started
        ↓
Health Check
        ↓
Service Ready
        ↓
Dependent Service Starts
```

---

# 1. Running vs Ready

These two states are not the same.

## Running

A container is running when its main process has started.

```text
Container
    |
    v
Process Running
    |
    v
Docker says:
"RUNNING"
```

But the application inside may still be:

- initializing files,
- opening sockets,
- loading data,
- running migrations,
- starting database subsystems,
- waiting for another dependency.

---

## Ready

A service is ready when it can actually perform the operation that other services depend on.

For PostgreSQL:

```text
PostgreSQL Process Running
        ≠
PostgreSQL Ready for Connections
```

For our API:

```text
Uvicorn Process Running
        ≠
FastAPI Ready to Serve Requests
```

This distinction is fundamental in distributed systems.

---

# 2. Why `depends_on` Alone Is Not Enough

Suppose we have:

```yaml
services:
  api:
    depends_on:
      - db

  db:
    image: postgres:latest
```

At first glance, it looks like:

```text
db
 ↓
api
```

But what `depends_on` establishes is **dependency order**, not database readiness.

Compose can start:

```text
1. db container
2. api container
```

while PostgreSQL is still initializing.

Official Docker documentation describes exactly this startup-order issue. citeturn873023view0

So:

```text
depends_on
    ↓
"Start db before api"
```

does not automatically mean:

```text
depends_on
    ↓
"Wait until PostgreSQL accepts connections"
```

---

# 3. Health Check

A Docker health check is a command or test used to determine whether the service inside a container is healthy.

Docker's Dockerfile reference describes `HEALTHCHECK` as the instruction used to check a container's health. citeturn873023view1

Conceptually:

```text
Container
   |
   +--> Process running
   |
   +--> Health check
            |
            +--> PASS → healthy
            |
            +--> FAIL → unhealthy
```

This gives Docker another piece of information:

```text
Is the container running?

and

Is the application inside it healthy?
```

---

# 4. Health Status

A health check can move through states such as:

```text
starting
   |
   +----> healthy
   |
   +----> unhealthy
```

Visualize it:

```text
             Container Started
                    |
                    v
               STARTING
                /     \
               /       \
              v         v
          HEALTHY    UNHEALTHY
```

The exact timing depends on:

- `start_period`
- `interval`
- `timeout`
- `retries`

---

# 5. PostgreSQL Health Check

PostgreSQL provides a useful readiness command:

```bash
pg_isready
```

It asks PostgreSQL whether the server is accepting connections.

For example:

```bash
pg_isready -U postgres -d student_db
```

A Compose health check can use this command.

Docker's current Compose startup-order documentation demonstrates the pattern:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
  interval: 10s
  retries: 5
  start_period: 30s
  timeout: 10s
```

The documentation uses `pg_isready` specifically to determine PostgreSQL readiness. citeturn873023view0

---

# 6. Anatomy of a Health Check

Example:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
  interval: 10s
  timeout: 10s
  retries: 5
  start_period: 30s
```

Let's understand every field.

---

## `test`

```yaml
test: ["CMD-SHELL", "pg_isready ..."]
```

This is the actual check.

It answers:

> "What command should Docker execute to determine whether the service is healthy?"

For PostgreSQL:

```text
pg_isready
```

---

## `interval`

```yaml
interval: 10s
```

How often the health check runs.

Conceptually:

```text
10s
 ↓
check

10s
 ↓
check

10s
 ↓
check
```

---

## `timeout`

```yaml
timeout: 10s
```

How long an individual health-check attempt is allowed to run before it is considered a failure.

---

## `retries`

```yaml
retries: 5
```

How many consecutive failures are tolerated before Docker considers the container unhealthy.

---

## `start_period`

```yaml
start_period: 30s
```

A startup grace period.

This is useful when the application needs time to initialize and should not immediately be considered unhealthy because the first checks fail.

---

# 7. Why Use `${...}` Carefully?

Notice the PostgreSQL health check example:

```yaml
pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}
```

The doubled dollar sign:

```text
$$
```

is important in Compose when you want the variable reference to reach the container shell rather than being interpolated by Compose first.

Conceptually:

```text
compose.yaml
     |
     v
Compose interpolation
     |
     v
Container shell
     |
     v
POSTGRES_USER / POSTGRES_DB
```

This is another example of why configuration must be understood across layers instead of being treated as magic syntax.

---

# 8. `depends_on` Conditions

Compose supports dependency conditions.

The major ones are:

```text
service_started
service_healthy
service_completed_successfully
```

Docker's current startup-order documentation defines these conditions. citeturn873023view0

---

## `service_started`

```yaml
depends_on:
  db:
    condition: service_started
```

Meaning:

> Start this service after the dependency's container has started.

It does **not** mean:

> The database is ready.

---

## `service_healthy`

```yaml
depends_on:
  db:
    condition: service_healthy
```

Meaning:

> Start this service only after the dependency has passed its health check.

This is what we want for our database.

---

## `service_completed_successfully`

Useful when the dependency is a one-time job:

```text
migration container
        |
        v
success
        |
        v
API starts
```

For our PostgreSQL service, this is not the correct condition.

---

# 9. The Correct Architecture

Our previous design:

```text
Compose
   |
   +---- db starts
   |
   +---- api starts
```

Becomes:

```text
Compose
   |
   v
Start db container
   |
   v
PostgreSQL initializes
   |
   v
Health check begins
   |
   +---- FAIL ----+
   |              |
   |              |
   +--------------+
          |
          v
      HEALTHY
          |
          v
      Start api
```

This is the key architecture of Day 26.

---

# 10. Complete Compose Example

Our conceptual Compose configuration becomes:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"

    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:latest

    environment:
      POSTGRES_DB: student_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: <secret>

    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 10s
      retries: 5
      start_period: 30s
```

The exact values can be tuned for the environment.

---

# 11. Request Lifecycle vs Startup Lifecycle

This is an important distinction.

## Request lifecycle

```text
Client
  |
  v
FastAPI
  |
  v
Router
  |
  v
Service
  |
  v
Repository
  |
  v
PostgreSQL
```

## Startup lifecycle

```text
Compose
  |
  v
PostgreSQL Container
  |
  v
PostgreSQL Ready?
  |
  +---- NO ----> Keep checking
  |
  +---- YES ---> FastAPI Container
```

Today's topic is about the **startup lifecycle**.

---

# 12. Why This Matters in Production

Imagine a real system:

```text
API
 |
 +--> PostgreSQL
 +--> Redis
 +--> Message Broker
 +--> External Service
```

Each dependency may have a different startup time.

If the API assumes:

```text
"Container started = dependency ready"
```

then startup becomes fragile.

A health-aware architecture instead understands:

```text
Dependency Started
        |
        v
Dependency Healthy
        |
        v
Dependent Starts / Becomes Ready
```

This principle is used far beyond Docker Compose.

---

# 13. Health Checks Are Not Only for Databases

The same concept applies to:

### Redis

```text
Can Redis accept commands?
```

### HTTP service

```text
Does /health respond successfully?
```

### Message broker

```text
Can the broker accept connections?
```

### AI model service

```text
Is the model loaded and ready to accept inference requests?
```

The health check should test **the capability that matters**, not merely whether a process exists.

---

# 14. Liveness vs Readiness

This distinction becomes increasingly important as we move toward distributed systems.

## Liveness

Question:

> Is the application process alive?

```text
Process alive?
   |
   +--> YES
   +--> NO
```

## Readiness

Question:

> Can the application safely receive traffic right now?

```text
Application alive
      |
      v
Dependencies ready?
      |
      v
Can accept requests?
```

A service can be:

```text
Liveness = TRUE
Readiness = FALSE
```

For example:

```text
FastAPI process running
        |
        v
PostgreSQL unavailable
        |
        v
API should not be considered ready
```

This distinction becomes very important with load balancers and Kubernetes.

---

# 15. Docker Health Check vs Application `/health`

These are related but not identical concepts.

A container-level health check might be:

```yaml
healthcheck:
  test: ...
```

An application-level endpoint might be:

```text
GET /health
```

Architecture:

```text
Docker
   |
   v
Container health
```

versus:

```text
Load Balancer
      |
      v
GET /health
      |
      v
FastAPI
```

Later, we can make our FastAPI health endpoint more intelligent, for example checking whether critical infrastructure is available.

For today's PostgreSQL exercise, the important lesson is simply:

> Health checks should represent actual service readiness.

---

# 16. Inspecting Health

After starting:

```bash
docker compose up -d
```

run:

```bash
docker compose ps
```

You should be able to see service state.

Then inspect a container:

```bash
docker inspect <container-name>
```

Look for the health information.

Conceptually:

```text
Health
 |
 +--> Status
 |
 +--> FailingStreak
 |
 +--> Logs
```

The logs can help answer:

> Why is this service unhealthy?

---

# 17. Troubleshooting Workflow

Suppose the API isn't starting.

Use:

```bash
docker compose ps
```

Then:

```bash
docker compose logs db
```

Then:

```bash
docker compose logs api
```

Your reasoning process should become:

```text
Is db running?
        |
        v
Is db healthy?
        |
        +---- NO
        |      |
        |      v
        |  Inspect db logs
        |
        +---- YES
               |
               v
          Is api running?
               |
               v
          Inspect api logs
```

This is the same systematic troubleshooting habit you've already developed during Days 24 and 25.

---

# 18. Deliberate Failure Experiment

A very useful experiment is to break the health check.

For example:

```yaml
healthcheck:
  test: ["CMD-SHELL", "this-command-does-not-exist"]
```

Then:

```bash
docker compose up
```

Observe:

```text
db
 |
 v
STARTING
 |
 v
UNHEALTHY
```

Your API dependency condition:

```yaml
condition: service_healthy
```

should prevent the API from being considered ready through that dependency chain.

Now inspect:

```bash
docker compose ps
```

and:

```bash
docker compose logs db
```

Fix the health check afterward.

This experiment teaches the difference between:

```text
Container running
```

and:

```text
Service healthy
```

far better than theory alone.

---

# 19. Health Check Failure Does Not Automatically Mean Container Stopped

This is an important nuance.

A health check can report:

```text
unhealthy
```

while the main process is still running.

Conceptually:

```text
Container
 |
 +--> Main process = RUNNING
 |
 +--> Health status = UNHEALTHY
```

So:

```text
RUNNING
```

and:

```text
HEALTHY
```

are different dimensions.

That is exactly why both states are useful.

---

# 20. Health Check and Restart

A health check tells Docker whether the service is healthy.

It does not automatically mean:

```text
unhealthy
   ↓
restart container
```

Restart behaviour is a separate concern.

Keep these concepts separate:

```text
Health Check
   |
   v
"What is the service's current health?"

Restart Policy
   |
   v
"What should happen when the process/container exits?"
```

This separation is important when designing production systems.

---

# 21. Why This Matters for AI Systems

Eventually our AI platform may look like:

```text
                    API
                     |
        +------------+------------+
        |                         |
        v                         v
    PostgreSQL                  Redis
        |                         |
        +------------+------------+
                     |
                     v
               AI Service
                     |
                     v
                   LLM
```

Now imagine:

```text
AI Service process starts
        |
        v
Model still loading...
        |
        v
API immediately sends inference request
        |
        v
❌ Failure
```

A readiness model allows:

```text
AI Service starts
        |
        v
Model loads
        |
        v
Health check passes
        |
        v
Service becomes ready
```

That is exactly the kind of systems thinking we're building toward with Project ₹50L.

---

# 22. Common Beginner Mistakes

### Mistake 1 — Assuming `depends_on` means "ready"

It primarily establishes dependency startup order unless combined with a readiness condition.

---

### Mistake 2 — Making a health check too weak

Bad:

```text
"Is the process alive?"
```

when you really need:

```text
"Can the service perform the required operation?"
```

---

### Mistake 3 — Health-checking the wrong thing

For PostgreSQL, checking whether a random file exists isn't meaningful.

Use:

```text
pg_isready
```

because it tests database readiness.

---

### Mistake 4 — Treating unhealthy as stopped

A container can be:

```text
running + unhealthy
```

---

### Mistake 5 — Using extremely aggressive intervals

A health check that runs every few hundred milliseconds can add unnecessary overhead.

Choose intervals according to the service and environment.

---

### Mistake 6 — Ignoring startup grace periods

Databases and AI model servers can need significant initialization time.

Use `start_period` when appropriate.

---

# 23. Production Best Practices

## Check meaningful readiness

Test the capability other services depend on.

---

## Keep health checks lightweight

A health check should be cheap enough to run repeatedly.

---

## Use realistic startup grace periods

Allow slow-starting services time to initialize.

---

## Keep liveness and readiness concepts separate

A service can be alive but temporarily unavailable.

---

## Use logs with health status

A health failure tells you **what state** the service is in.

Logs help tell you **why**.

---

# 24. Interview Questions

### Q1. What is the difference between running and ready?

A running container means its main process is active. A ready service has successfully initialized and can perform the capability required by its dependents.

---

### Q2. Why isn't `depends_on` alone enough?

Because dependency ordering can ensure that a container starts before another container, but the dependency may still be initializing and not ready to accept requests.

---

### Q3. What is a Docker health check?

A health check is a test used to determine whether the service inside a container is functioning as expected.

---

### Q4. What is `service_healthy`?

It tells Compose to wait until the dependency reports a healthy status before starting the dependent service.

---

### Q5. What is the difference between `service_started` and `service_healthy`?

```text
service_started
    ↓
Dependency container has started.

service_healthy
    ↓
Dependency has passed its health check.
```

---

### Q6. How do you check PostgreSQL readiness?

A common PostgreSQL readiness test is:

```bash
pg_isready
```

---

### Q7. What do `interval`, `timeout`, and `retries` mean?

```text
interval
→ How often the check runs.

timeout
→ Maximum duration of one check.

retries
→ Consecutive failures before unhealthy.
```

---

### Q8. What is `start_period`?

A startup grace period during which the application can initialize before health-check failures are treated normally.

---

### Q9. Can a container be running but unhealthy?

Yes.

```text
Container = RUNNING
Health    = UNHEALTHY
```

These are separate states.

---

### Q10. Why is readiness important in distributed systems?

Because services often depend on other services that may start at different times. Readiness prevents traffic or dependent work from reaching a service before it can actually handle requests.

---

# 25. FastAPI ↔ ASP.NET Core Mapping

The concept is framework-independent.

In ASP.NET Core deployments you may also encounter:

```text
Health Checks
      |
      +--> Liveness
      |
      +--> Readiness
```

For example, an ASP.NET Core application might expose health-check endpoints that infrastructure components use to determine whether the application can safely receive traffic.

FastAPI can implement equivalent concepts.

The framework changes.

The systems-engineering principle does not.

---

# 26. Docker Compose vs Kubernetes Mental Model

Today:

```text
Docker Compose
      |
      v
depends_on + healthcheck
```

Later in the roadmap:

```text
Kubernetes
      |
      +--> readinessProbe
      +--> livenessProbe
      +--> startupProbe
```

Do not learn Kubernetes yet.

Just recognize the progression:

```text
Docker Health
      ↓
Compose Readiness
      ↓
Kubernetes Probes
      ↓
Production Orchestration
```

This is one reason today's seemingly small topic matters for your eventual systems-engineering goal.

---

# 27. Our Architecture After Day 26

```text
                         Docker Compose
                              |
                              v
                    PostgreSQL Container
                              |
                              v
                         Healthcheck
                              |
                  +-----------+-----------+
                  |                       |
                FAIL                    PASS
                  |                       |
                  v                       v
             UNHEALTHY                HEALTHY
                                          |
                                          v
                                  FastAPI Container
                                          |
                                          v
                                     Connection
                                          |
                                          v
                                      db:5432
```

And the overall application request flow remains:

```text
Client
  |
  v
FastAPI Container
  |
  v
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
PostgreSQL Container
```

The new piece is the **startup/readiness control around the services**.

---

# 28. Cheat Sheet

```text
depends_on
→ Defines dependency relationship / startup ordering.

service_started
→ Dependency container has started.

service_healthy
→ Dependency has passed its health check.

service_completed_successfully
→ Dependency completed successfully.

healthcheck
→ Defines how Docker determines container health.

interval
→ Time between health checks.

timeout
→ Maximum duration of one check.

retries
→ Consecutive failures allowed before unhealthy.

start_period
→ Startup grace period.

pg_isready
→ PostgreSQL readiness utility.

RUNNING
→ Main process is active.

HEALTHY
→ Health check is passing.

UNHEALTHY
→ Health check is failing.
```

---

# 29. Final Mental Model

Remember this entire flow:

```text
                     Docker Compose
                            |
                            v
                  Start PostgreSQL
                            |
                            v
                    Container Running
                            |
                            v
                     Health Check
                     /          \
                   FAIL          PASS
                    |             |
                    v             v
                UNHEALTHY      HEALTHY
                                  |
                                  v
                           Start FastAPI
                                  |
                                  v
                              API Ready
```

The most important sentence from Day 26 is:

> **A container being running does not necessarily mean the service inside it is ready.**

And the most important Compose pattern is:

```yaml
depends_on:
  db:
    condition: service_healthy
```

combined with a meaningful:

```yaml
healthcheck: ...
```

This is the bridge from **"my containers start"** to **"my services start in a controlled, dependency-aware way."**

---

# Key Takeaways

- `depends_on` establishes dependency relationships and startup order, but a running dependency may still not be ready.
- `healthcheck` provides an explicit mechanism for determining whether a service is healthy.
- `service_healthy` allows Compose to wait for a dependency's health check before starting the dependent service. citeturn873023view0
- PostgreSQL's `pg_isready` is a useful readiness check for PostgreSQL. citeturn873023view0
- `interval`, `timeout`, `retries`, and `start_period` control how health checks are evaluated.
- A container can be running while its health status is unhealthy.
- Health checks should test meaningful service capability, not merely process existence.
- Liveness and readiness are different concepts.
- Logs explain **why** a service is unhealthy; health status tells you **what state** it is in.
- This same mental model eventually leads to Kubernetes readiness/liveness/startup probes and production orchestration.

---

# Project ₹50L — Architecture Evolution

```text
Day 23
Docker Fundamentals
        |
        v
Day 24
FastAPI Container
        |
        v
Day 25
Docker Compose
+
FastAPI + PostgreSQL
        |
        v
Day 26
Health Checks
+
Service Readiness
        |
        v
Production-Style
Startup & Dependency Management
        |
        v
Future
Cloud Deployment
+
Kubernetes
+
Distributed Systems
+
AI Platforms
```

This is an important systems-engineering milestone.

We're no longer only learning how to **run containers**.

We're learning how to make a collection of services **start, communicate, fail, recover, and become ready in a controlled way**—which is exactly the kind of thinking required as we move toward the larger AI platform and systems engineering goal.
