# Day 027 — Docker Compose Configuration

## Exercise 1 — Inspect the Resolved Compose Configuration

Before changing anything, run:

```bash
docker compose config
```

This command shows what Compose actually resolves after processing the YAML file and environment values.

Think of the resolution flow as:

```text
compose.yaml
    + .env
    + interpolation
        |
        v
docker compose config
        |
        v
Resolved configuration
```

---

## Exercise 2 — Move Configuration to Explicit Environment Variables

Review your current Compose configuration and identify the following variables:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
JWT_SECRET
```

Determine which variables represent:

- Application configuration
- Secrets
- Infrastructure values

Then refactor the Compose file so values can be supplied externally instead of being hardcoded.

Example:

```yaml
environment:
  DB_HOST: ${DB_HOST}
  DB_PORT: ${DB_PORT}
```

---

## Exercise 3 — Use `.env` and `env_file` Deliberately

You already use `.env`. Experiment with separating the following concerns:

```text
.env
  |
  v
Compose interpolation / project configuration
```

```text
.env.dev
  |
  v
Container environment
```

Do not create a large collection of environment files unnecessarily.

The objective is to understand that **Compose interpolation** and **container environment injection** are related, but they are not exactly the same thing.

---

## Exercise 4 — Environment Precedence Experiment

Deliberately define the same variable in two places.

For example, define the variable in `.env`:

```dotenv
DEBUG=false
```

Then define a different value in the Compose service configuration:

```yaml
environment:
  DEBUG: "true"
```

Inspect the resolved Compose configuration:

```bash
docker compose config
```

You can also inspect the value that reaches the container:

```bash
docker compose run --rm api env
```

Observe which value reaches the container. Restore the configuration after the experiment.

### Goal

Do not simply memorize a precedence table. Understand that when multiple sources define the same variable, Compose resolves them deterministically.

---

## Exercise 5 — Add a Restart Policy

The API currently has this conceptual relationship:

```text
Container
    |
    v
Process
```

Experiment with the following restart policy, or the equivalent configuration for your Compose setup:

```yaml
restart: on-failure
```

Then intentionally make the application process exit.

Observe the service state:

```bash
docker compose ps
```

Inspect the API logs:

```bash
docker compose logs api
```

The expected lifecycle is:

```text
Application exits
        |
        v
Docker sees non-zero exit
        |
        v
Restart policy
        |
        v
Container restarted
```

Do not leave an unnecessary restart policy in place only for experimentation. Decide what makes sense for this project after the test.

---

## Exercise 6 — Development vs. Production

This is the main architecture exercise for today.

### Development Workflow

During development, a source-code bind mount can be useful:

```text
Host source code
        |
        v
Bind mount
        |
        v
Container
```

Changing Python code on the host can then immediately affect the running development environment.

### Production Workflow

Production generally uses an immutable image:

```text
Source
  |
  v
Build image
  |
  v
Immutable image
  |
  v
Container
```

Docker's production guidance recommends removing application-code volume bindings so the application code remains inside the container image.

### Question

Why is a source-code bind mount useful during development but undesirable for a production deployment?

---

## Exercise 7 — Compose Architecture Review

Your Compose architecture should now be mentally organized like this:

```text
                    compose.yaml
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Services       Networks       Volumes
          |
     +----+----+
     v         v
    api        db
     |         |
     |         +---- postgres_data
     |
     +---- environment
```

The surrounding configuration concerns are:

- Configuration
- Health checks
- Restart behavior
- Persistent storage
- Networking

This is becoming a real deployment configuration rather than only a Docker tutorial.
