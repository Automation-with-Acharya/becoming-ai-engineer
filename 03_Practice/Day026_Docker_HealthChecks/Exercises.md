# Day 026 — Docker Health Checks

## Exercise 1 — Observe the Current Behavior

Start the Compose application:

```bash
docker compose up
```

In another terminal, inspect the service status:

```bash
docker compose ps
```

Observe the following information:

| Field     | Meaning                                         |
| --------- | ----------------------------------------------- |
| `SERVICE` | The Compose service name, such as `db` or `api` |
| `STATUS`  | The current state of the service container      |

Inspect the database logs:

```bash
docker compose logs db
```

Inspect the API logs:

```bash
docker compose logs api
```

### Question

At what exact point does PostgreSQL become usable?

---

## Exercise 2 — Add PostgreSQL Health Checking

The concept for this exercise is:

```text
PostgreSQL container
        |
        v
Docker health check
        |
        +---- Starting
        |
        +---- Healthy
        |
        +---- Unhealthy
```

Your Compose configuration should eventually have the following logical structure:

```yaml
services:
  db:
    healthcheck:
      test: [...]
      interval: ...
      timeout: ...
      retries: ...
```

Do not copy the syntax blindly. Understand every property first.

### Questions

1. What command actually tests PostgreSQL?
2. How frequently should the health check run?
3. What does `timeout` mean?
4. What happens after repeated health-check failures?
5. What does Docker display when the service becomes unhealthy?

---

## Exercise 3 — Make FastAPI Depend on Database Health

The architecture should evolve from starting both services independently:

```text
Compose
  |
  +--> db starts
  |
  +--> api starts
```

to starting the API only after the database is healthy:

```text
Compose
  |
  v
db container starts
  |
  v
PostgreSQL initializes
  |
  v
Health check passes
  |
  v
db becomes HEALTHY
  |
  v
api starts
```

This is the main architecture exercise of Day 026.

---

## Exercise 4 — Inspect Health Status

View the Compose service status:

```bash
docker compose ps
```

Look for health-related status information.

Inspect a specific container:

```bash
docker inspect <container-name>
```

Explore the `Health` section in the output. Docker maintains metadata similar to:

```text
Health
 |
 +--> Status
 |
 +--> FailingStreak
 |
 +--> Log
```

### Health Metadata

| Field           | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| `Status`        | Current state, such as `starting`, `healthy`, or `unhealthy` |
| `FailingStreak` | Number of consecutive failed health checks                   |
| `Log`           | Recent health-check results and output                       |

---

## Exercise 5 — Deliberately Break the Health Check

This exercise demonstrates how Docker reports a failing health check.

Temporarily make the health check fail. For example, intentionally change the health-check command or use incorrect credentials.

Start the application:

```bash
docker compose up
```

Inspect the service status:

```bash
docker compose ps
```

Inspect the database logs:

```bash
docker compose logs db
```

Observe the state transition:

```text
Starting
   |
   v
Unhealthy
```

Finally, restore the correct health-check configuration and verify that the database becomes healthy.
