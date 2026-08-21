# Day 027 — Docker Compose Environment Management & Local Deployment

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 21 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand `environment` vs `env_file` in Docker Compose.
- Understand `.env` interpolation and practical precedence.
- Use `docker compose config` to inspect resolved configuration.
- Understand restart policies and how they differ from health checks.
- Understand development vs production Compose configuration.
- Understand why bind mounts are useful in development but generally undesirable in production.
- Apply these concepts to the Student Management backend.

---

# Big Picture

Our Docker architecture has evolved:

```text
Day 23 → Docker Fundamentals
       ↓
Day 24 → FastAPI Container
       ↓
Day 25 → FastAPI + PostgreSQL + Compose
       ↓
Day 26 → Health Checks + Service Readiness
       ↓
Day 27 → Environment Management + Restart + Local Deployment
```

Today we add another operational layer:

```text
                 Docker Compose
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
 Configuration     Health Checks    Restart Policy
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                Application Stack
```

---

# 1. Why Environment Management Matters

The same application can run with different configuration in different environments:

```text
Development
    ↓
Local database
    ↓
Debug enabled

Production
    ↓
Production database
    ↓
Debug disabled
    ↓
Controlled logging
```

The application code should remain the same.

> **Configuration changes; application code should not.**

---

# 2. Configuration Flow

```text
.env / external environment
          │
          ▼
      Docker Compose
          │
          ▼
   Container Environment
          │
          ▼
   Pydantic Settings
          │
          ▼
       FastAPI
```

This extends the centralized configuration model we built on Day 19.

---

# 3. `environment`

Compose can define variables directly:

```yaml
services:
  api:
    environment:
      DB_HOST: db
      DB_PORT: 5432
      LOG_LEVEL: INFO
```

The values become part of the container environment.

---

# 4. `env_file`

Compose can load environment values from a file:

```yaml
services:
  api:
    env_file:
      - .env
```

Conceptually:

```text
.env
  ↓
Container Environment
  ↓
Pydantic Settings
  ↓
FastAPI
```

Keep real secrets out of Git. Use `.env.example` as a safe template.

---

# 5. `environment` vs `env_file`

| `environment`                              | `env_file`                         |
| ------------------------------------------ | ---------------------------------- |
| Values written directly in Compose         | Values loaded from a file          |
| Good for a small number of explicit values | Convenient for groups of values    |
| Visible in `compose.yaml`                  | Externalized from the Compose file |
| Per-variable control                       | File-based management              |

Neither should be treated as a complete production secret-management solution.

---

# 6. `.env` and Compose Interpolation

Example:

```yaml
services:
  api:
    environment:
      DB_HOST: ${DB_HOST}
      DB_PORT: ${DB_PORT}
```

If `.env` contains:

```env
DB_HOST=db
DB_PORT=5432
```

Compose resolves the placeholders before creating the container configuration.

```text
.env
  ↓
Compose interpolation
  ↓
Resolved configuration
  ↓
Container configuration
```

---

# 7. Default Values

Compose supports defaults such as:

```yaml
environment:
  LOG_LEVEL: ${LOG_LEVEL:-INFO}
```

Mental model:

```text
LOG_LEVEL exists?
     │
   YES ──→ use its value
     │
    NO
     │
     ▼
 use INFO
```

---

# 8. Interpolation vs Container Environment

These are related but not identical.

### Compose interpolation

```text
.env
  ↓
Compose substitutes ${VARIABLE}
  ↓
Resolved Compose configuration
```

### Container environment injection

```text
environment / env_file
  ↓
Container environment
  ↓
Application
```

This distinction is important during configuration troubleshooting.

---

# 9. Environment Variable Precedence

A variable can be defined in multiple places. When that happens, Compose applies a defined precedence order.

The practical engineering lesson is:

> **Do not guess which configuration source is winning. Inspect the resolved configuration.**

---

# 10. `docker compose config`

One of the most useful commands for Compose troubleshooting is:

```bash
docker compose config
```

Think of it as:

```text
compose.yaml
   +
.env
   +
interpolation / overrides
   ↓
docker compose config
   ↓
resolved configuration
```

Use it when you are confused about:

- environment variables
- service definitions
- ports
- volumes
- dependencies
- interpolation

---

# 11. Why `docker compose config` Is Powerful

Suppose you expect:

```text
DB_HOST=db
```

but the application behaves as if:

```text
DB_HOST=localhost
```

Instead of guessing:

```bash
docker compose config
```

Then inspect what Compose actually resolved.

This changes debugging from:

```text
Guess
 ↓
Try
 ↓
Guess again
```

into:

```text
Inspect
 ↓
Understand
 ↓
Fix
```

---

# 12. Restart Policies

Health checks answer:

> **Is the service healthy?**

Restart policies answer:

> **What should Docker do if the container exits?**

Example:

```yaml
services:
  api:
    restart: on-failure
```

Conceptually:

```text
Application process
       ↓
Unexpected failure
       ↓
Container exits
       ↓
Restart policy
       ↓
Container restarted
```

Common restart modes include `none`, `on-failure`, `always`, and `unless-stopped`.

Use restart behavior intentionally; don't use it to hide application defects.

---

# 13. Health Check vs Restart Policy

These are separate mechanisms.

```text
Health Check
    ↓
Is the service healthy?
```

```text
Restart Policy
    ↓
What should happen after container/process exit?
```

Example:

```text
PostgreSQL Container
       │
       ├── Running
       │
       ├── Health Check
       │      ├── Healthy
       │      └── Unhealthy
       │
       └── Process exits
              ↓
         Restart Policy
```

A health check does not automatically mean the container will restart.

---

# 14. Development vs Production

## Development

Developers want fast feedback. A bind mount can be useful:

```text
Host Source Code
       │
       │ bind mount
       ▼
Container
       ↓
Fast feedback
```

## Production

Production generally prefers an immutable application image:

```text
Source Code
    ↓
docker build
    ↓
Immutable Image
    ↓
Container
```

The production mindset is:

> **Build the artifact first; deploy the artifact.**

---

# 15. Development vs Production Comparison

| Development                  | Production                    |
| ---------------------------- | ----------------------------- |
| Fast iteration               | Reproducibility               |
| Bind mounts can help         | Prefer immutable images       |
| Debug configuration          | Debug disabled                |
| Local convenience            | Controlled deployment         |
| Frequent rebuilds acceptable | Versioned image deployment    |
| More tooling exposed locally | Minimize unnecessary exposure |

The goal is not identical configuration. The goal is a reproducible production artifact.

---

# 16. Our Student Management Setup

```text
                     Docker Compose
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
      Services        Configuration     Operations
          │               │             Policies
      ┌───┴───┐           │                │
      ▼       ▼            ▼                ▼
     api      db      Environment      Health/Restart
      │       │            │
      │       └── postgres_data
      │
      └── FastAPI
```

---

# 17. Configuration + Health + Restart

Think of these as three separate operational concerns:

```text
Configuration
     |
     +--> How should the application behave?

Health Check
     |
     +--> Is the service healthy?

Restart Policy
     |
     +--> What happens if the process exits?
```

This mirrors the separation-of-concerns mindset used throughout our application architecture.

---

# 18. Practical Environment Debugging

When a container behaves unexpectedly:

### Step 1

```bash
docker compose config
```

### Step 2

```bash
docker compose ps
```

### Step 3

```bash
docker compose logs api
```

### Step 4

If necessary, inspect the container environment:

```bash
docker compose run --rm api env
```

### Step 5

Compare actual values with expected values.

```text
Compose Config
      ↓
Container State
      ↓
Logs
      ↓
Environment
      ↓
Root Cause
```

---

# 19. Common Beginner Mistakes

### Mistake 1 — Hardcoding secrets

Avoid:

```yaml
environment:
  DB_PASSWORD: my-real-password
```

Use external configuration or an appropriate secret-management mechanism instead.

### Mistake 2 — Assuming `.env` automatically becomes every container's environment

Understand Compose interpolation separately from container environment injection.

### Mistake 3 — Changing multiple configuration layers at once

If you change `.env`, `compose.yaml`, the Dockerfile, and Pydantic Settings simultaneously, debugging becomes unnecessarily difficult.

Change one layer at a time.

### Mistake 4 — Using restart policies to hide bugs

If an application crashes continuously, fix the application instead of relying on Docker to keep restarting it.

### Mistake 5 — Using source-code bind mounts in production

Production should generally run the versioned application image rather than depending on a host filesystem.

---

# 20. Production Best Practices

✅ Keep configuration outside source code.

✅ Keep production images immutable.

✅ Use restart policies intentionally.

✅ Inspect resolved Compose configuration.

✅ Keep real secrets out of Git.

✅ Keep development conveniences separate from production deployment behavior.

---

# 21. Interview Questions

### Q1. What is the difference between `environment` and `env_file`?

`environment` defines variables directly in Compose, while `env_file` loads variables from a file for the service.

### Q2. What is `.env` used for in Docker Compose?

It is commonly used as a source for Compose interpolation and local configuration. Values still need to be provided to containers through the appropriate Compose mechanism.

### Q3. Why is `docker compose config` useful?

It shows the resolved Compose configuration after variable interpolation and configuration processing, making it extremely useful for diagnosing configuration problems.

### Q4. What is a restart policy?

A rule that determines whether Docker should restart a container after its process exits.

### Q5. Health check vs restart policy?

```text
Health Check
→ Determines service health.

Restart Policy
→ Determines what Docker does after container/process exit.
```

### Q6. Why avoid source-code bind mounts in production?

They make the deployment depend on host filesystem state instead of a reproducible, immutable application image.

### Q7. Why separate configuration from application code?

Because configuration changes between environments while application code should remain unchanged.

---

# 22. FastAPI ↔ ASP.NET Core Mapping

The same engineering principles exist in .NET systems.

```text
ASP.NET Core
      +
SQL Server
      +
Redis
      +
Docker Compose
```

Whether the framework is FastAPI or ASP.NET Core, the engineering concerns remain:

```text
Configuration
+
Health
+
Resilience
+
Observability
+
Deployment
```

---

# 23. Cheat Sheet

```text
environment
→ Define environment variables directly in Compose

env_file
→ Load environment variables from a file

.env
→ Common source for Compose interpolation/local configuration

${VAR}
→ Compose variable interpolation

${VAR:-default}
→ Use default if VAR is missing

docker compose config
→ Show resolved Compose configuration

restart: on-failure
→ Restart container after failure

healthcheck
→ Determine service health

bind mount
→ Map host filesystem into a container

immutable image
→ Build once, deploy the built artifact
```

---

# 24. Final Mental Model

```text
                    Docker Compose
                          │
          ┌───────────────┼──────────────────┐
          │               │                  │
          ▼               ▼                  ▼
     Configuration    Health Checks      Restart Policy
          │               │                  │
          ▼               ▼                  ▼
   How app behaves    Is it healthy?    What after exit?
          │               │                  │
          └───────────────┼──────────────────┘
                          ▼
                  Running Services
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                   api          db
```

Development vs production:

```text
DEVELOPMENT

Source Code
    ↓
Bind Mount
    ↓
Container
    ↓
Fast Feedback


PRODUCTION

Source Code
    ↓
Build Image
    ↓
Immutable Image
    ↓
Container
    ↓
Predictable Deployment
```

---

# Key Takeaways

- `environment` and `env_file` are different mechanisms for supplying container environment variables.
- `.env` is commonly used for Compose interpolation and local configuration, but values must still be provided to containers through the appropriate mechanism.
- `docker compose config` is one of the most useful tools for debugging resolved Compose configuration.
- Health checks answer **"Is this service healthy?"**, while restart policies answer **"What should happen if the container exits?"**
- Development and production should not necessarily use identical Compose configurations.
- Development bind mounts can improve iteration speed, while production should generally use immutable application images.
- Configuration, health, restart behavior, networking, and persistent storage are distinct operational concerns.
- These operational concepts are the next step from simply running containers toward operating a production-oriented backend.

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
FastAPI + PostgreSQL + Compose
        │
        ▼
Day 26
Health Checks + Service Readiness
        │
        ▼
Day 27
Environment Management
+
Restart Behaviour
+
Local Deployment Configuration
```

We are no longer merely learning Docker commands.

We're learning how to **operate a multi-container application deliberately**.

---

# Revision Checklist

- [ ] Can explain `environment` vs `env_file`.
- [ ] Can explain what `.env` does in Compose.
- [ ] Understand Compose variable interpolation.
- [ ] Know why environment-variable precedence matters.
- [ ] Can use `docker compose config`.
- [ ] Understand restart policies.
- [ ] Understand health checks separately from restart policies.
- [ ] Can explain development vs production container configuration.
- [ ] Understand why production should prefer immutable images.
- [ ] Can troubleshoot a configuration problem systematically.
- [ ] Can explain how today's concepts fit into the Student Management architecture.

---

# Exact Resources Used

- Docker Docs — Environment variables: https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/
- Docker Docs — Environment variable precedence: https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/
- Docker Docs — Variable interpolation: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- Docker Docs — Compose in production: https://docs.docker.com/compose/how-tos/production/
- Docker Docs — Restart policy reference: https://docs.docker.com/reference/compose-file/deploy/#restart_policy

These resources were selected for Day 027's environment management, configuration resolution, restart behavior, and development-vs-production learning objectives.
