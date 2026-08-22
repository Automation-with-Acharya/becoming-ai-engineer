# Docker Internal Network Exercises

## Exercise 1: Inspect Your Compose Network

Run:

```bash
docker network ls
```

Look for the network created by your Compose project. Then inspect it:

```bash
docker network inspect <network-name>
```

Observe:

- Network driver
- Connected containers
- Internal IP addresses
- Network aliases

### Question

If `db` already has an IP address, why should the API application still use
`db` instead of hardcoding that IP?

### Answer

Because container IP addresses are not a stable application-level contract.
Service names are.

## Exercise 2: Inspect DNS from the API Container

First, check the running services:

```bash
docker compose ps
```

Then enter the API container:

```bash
docker compose exec api sh
```

Inspect the environment:

```bash
env
```

Look for:

```text
DB_HOST=db
```

Experiment with name resolution if your image contains the relevant
utilities.

Your goal is not to memorize commands. Your goal is to understand this flow:

```text
Application
      |
      v
DB_HOST=db
      |
      v
Docker Internal DNS
      |
      v
PostgreSQL Container
```

## Exercise 3: Prove the `localhost` Difference

Your current application configuration should conceptually be:

```text
Inside Docker:
DB_HOST=db
```

Now think through what would happen if you changed it to:

```text
DB_HOST=localhost
```

The FastAPI container would effectively attempt:

```text
API Container
      |
      v
localhost:5432
```

But PostgreSQL is somewhere else:

```text
DB Container
```

Therefore:

> `localhost` is not another container.

This concept is extremely important for troubleshooting future containerized
applications.

## Exercise 4: Remove PostgreSQL's Published Port Experiment

Currently, you may have something like this in `compose.yaml`:

```yaml
db:
  ports:
    - "5432:5432"
```

Temporarily understand what this port mapping is for.

If your FastAPI container connects using:

```text
db:5432
```

the published port mapping is not required for API-to-PostgreSQL
communication. It is useful for connections from the Windows host, such as
pgAdmin:

```text
Windows Host
      |
      v
localhost:5432
      |
      v
PostgreSQL Container
```

The API and the host machine are different clients with different connection
paths.

### Internal API-to-Database Path

```text
                              Docker Network

                    +--------------------+
                    |                    |
                    |   api ------> db   |
                    |       db:5432      |
                    |                    |
                    +--------------------+
```

## Mini Project Task

Update your understanding and documentation around the current architecture.

You do not need to rewrite your whole application today. Instead, document
and verify the existing network architecture.

Your `compose.yaml` should conceptually make sense like this:

```yaml
services:
  api:
    environment:
      DB_HOST: db

  db: ...
```

Then understand the full flow:

```text
Browser
      |
      | localhost:8000
      v
Host Machine
      |
      | published port
      v
FastAPI Container
      |
      | DB_HOST=db
      v
Docker Internal DNS
      |
      v
PostgreSQL Container
      |
      | 5432
      v
PostgreSQL Server
```

That is your main architecture diagram for today.
