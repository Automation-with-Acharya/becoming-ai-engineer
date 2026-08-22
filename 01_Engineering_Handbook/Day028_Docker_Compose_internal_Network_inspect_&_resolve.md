# Day 028 — Docker Compose Internal Network, Inspect & Resolve

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 22 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Explain how Docker containers communicate over a user-defined bridge network.
- Understand the difference between host-to-container and container-to-container communication.
- Explain why `DB_HOST=db` works while `DB_HOST=localhost` usually does not.
- Understand Docker's internal DNS/service discovery model.
- Distinguish container ports from published host ports.
- Inspect Docker networks and connected containers.
- Understand how Docker assigns internal IP addresses.
- Troubleshoot container connectivity systematically.
- Explain how Docker Compose networking supports our FastAPI + PostgreSQL architecture.

---

# Big Picture

On Day 25 we moved PostgreSQL into Docker Compose.

On Day 26 we added health checks and service readiness.

On Day 27 we improved configuration and restart behavior.

Today we go one layer deeper:

```text
Day 25
Multi-container application
        ↓
Day 26
Service readiness
        ↓
Day 27
Configuration + restart behavior
        ↓
Day 28
Internal networking + DNS + troubleshooting
```

Our current architecture is:

```text
                         Docker Compose
                              |
                +-------------+-------------+
                |                           |
                v                           v
        +---------------+           +---------------+
        | FastAPI API   |           | PostgreSQL    |
        | Container     |---------->| Container     |
        |               |  db:5432  |               |
        +---------------+           +---------------+
                |
                |
          localhost:8000
                |
                v
           Host Browser
```

The important question today is:

> **How does `db` actually become reachable from the FastAPI container?**

---

# 1. What Is Docker Container Networking?

Docker container networking allows containers to communicate with:

- other containers,
- services outside Docker,
- and the host/network environment.

A container sees a network interface, an IP address, routing information, and DNS configuration. citeturn756014view0

Conceptually:

```text
Container
    |
    +-- Network Interface
    +-- IP Address
    +-- Gateway
    +-- Routing Table
    +-- DNS
```

Docker provides the networking infrastructure around that namespace.

---

# 2. The Bridge Network

For local multi-container applications, the most important network type today is the **bridge network**.

A bridge network provides a private network segment in which connected containers can communicate with one another while remaining isolated from containers on unrelated bridge networks. citeturn756014view1

Visualize it as:

```text
                  Docker Host

        +--------------------------------+
        |        Bridge Network          |
        |                                |
        |   +---------+    +---------+   |
        |   |   api   |    |    db   |   |
        |   |         |--->|         |   |
        |   +---------+    +---------+   |
        |                                |
        +--------------------------------+
```

Docker's bridge networking also supports published ports for exposing container services through host addresses. citeturn756014view1

---

# 3. Default Bridge vs User-Defined Bridge

Docker has a built-in `bridge` network, but user-defined bridge networks are generally the better choice for application stacks.

A key difference:

```text
Default bridge
    ↓
Container-to-container name resolution is limited

User-defined bridge
    ↓
Automatic DNS/service discovery
```

Docker explicitly documents that user-defined bridges provide automatic DNS resolution between containers, allowing a container named or aliased `db` to be reached using `db`. citeturn756014view1

This is one reason Docker Compose networking is so convenient.

---

# 4. Docker Compose Creates the Application Network

When we run:

```bash
docker compose up
```

Compose creates the network required by the application unless the Compose configuration explicitly uses another network.

Conceptually:

```text
student-management
        |
        v
student-management_default
        |
        +----------------+
        |                |
        v                v
       api              db
```

The exact generated network name depends on the Compose project name.

The important point is:

> Both services are attached to a shared network.

---

# 5. Why Does `DB_HOST=db` Work?

Suppose our Compose file contains:

```yaml
services:
  api: ...

  db: ...
```

The database service is logically called:

```text
db
```

Inside the Compose network:

```text
FastAPI Container
        |
        | DNS lookup: "db"
        v
Docker embedded DNS
        |
        v
PostgreSQL Container
```

Docker's embedded DNS allows containers on custom/user-defined networks to resolve service/container names. citeturn756014view0turn756014view1

Therefore:

```env
DB_HOST=db
```

works without hardcoding an IP address.

---

# 6. Why `localhost` Does Not Mean "The Other Container"

Inside the FastAPI container:

```text
localhost
    |
    v
FastAPI Container
```

It does not mean:

```text
localhost
    |
    v
PostgreSQL Container
```

The API container has its own network namespace.

Therefore:

```env
DB_HOST=localhost
```

typically makes the application search for PostgreSQL **inside the API container itself**.

The result is commonly:

```text
Connection refused
```

because PostgreSQL is not running there.

---

# 7. `localhost` Has Different Meanings

This is a useful mental model:

```text
Windows Host

localhost
    ↓
Windows Host
```

```text
FastAPI Container

localhost
    ↓
FastAPI Container
```

```text
PostgreSQL Container

localhost
    ↓
PostgreSQL Container
```

The word is the same.

The network namespace is different.

---

# 8. Internal Container Port vs Published Host Port

Suppose PostgreSQL listens on:

```text
5432
```

Inside the Docker network:

```text
api
 |
 | db:5432
 v
db
```

No host port mapping is required for this internal communication.

But suppose pgAdmin is running on your host machine.

Then:

```text
Host pgAdmin
      |
      | localhost:5433
      v
Published Docker Port
      |
      v
PostgreSQL Container :5432
```

This may be configured as:

```yaml
ports:
  - "5433:5432"
```

The two communication paths are therefore:

```text
Container → Container
db:5432
```

and:

```text
Host → Container
localhost:5433
```

These are different network paths.

---

# 9. Why `ports` Is Not Needed for API → DB

Suppose:

```yaml
services:
  api: ...

  db:
    image: postgres
```

The API can still connect to:

```text
db:5432
```

provided both services are on the same network.

Publishing:

```yaml
ports:
  - "5432:5432"
```

is primarily about making that database reachable through the host-side published port.

It is not a prerequisite for normal same-network container communication. Docker documents that containers connected to the same bridge network can communicate without published ports; publishing is needed to make ports available outside that network. citeturn756014view0turn756014view1

---

# 10. Container IP Addresses

Every network-connected container receives an IP address from the network's configured subnet. Docker allocates these addresses dynamically. citeturn756014view0

Conceptually:

```text
Docker Network
      |
      +--> api
      |     IP: 172.x.x.x
      |
      +--> db
            IP: 172.x.x.x
```

You may see values such as:

```text
172.18.0.2
172.18.0.3
```

But applications should generally avoid hardcoding these values.

Why?

```text
Container removed
       ↓
Container recreated
       ↓
New IP possible
```

The service identity:

```text
db
```

is a much better application-level dependency.

---

# 11. Service Name vs Container IP

Bad:

```env
DB_HOST=172.18.0.3
```

Better:

```env
DB_HOST=db
```

The flow becomes:

```text
Application
     |
     | db
     v
Docker DNS
     |
     v
Current PostgreSQL container IP
```

This gives us a stable logical name while Docker handles the infrastructure detail.

---

# 12. Docker's Embedded DNS

On custom/user-defined networks, Docker provides an embedded DNS server for service/container resolution. Docker documents the embedded DNS address as `127.0.0.11` inside the container's DNS configuration. citeturn756014view0

You normally do **not** need to configure this manually.

Instead:

```text
Application
    |
    | db
    v
Docker DNS
    |
    v
PostgreSQL Container
```

The application simply uses the logical name.

---

# 13. Inspecting Docker Networks

One of today's most important skills is learning to inspect the actual runtime state.

Start with:

```bash
docker network ls
```

This shows the networks currently known to Docker.

Conceptually:

```text
NETWORK NAME
student-management_default
bridge
host
none
...
```

---

# 14. Inspect a Network

Use:

```bash
docker network inspect <network-name>
```

This can reveal:

- network driver,
- subnet,
- gateway,
- attached containers,
- container IP addresses,
- network aliases,
- configuration details.

Think:

```text
docker network inspect
        |
        v
"Show me what Docker actually built."
```

This is much more useful than guessing how your network is configured.

---

# 15. What You Should Look For

When inspecting the Compose network, look for:

```text
Containers
    |
    +--> api
    |
    +--> db
```

Then look at their network addresses:

```text
api
  IPv4Address: 172.x.x.x

db
  IPv4Address: 172.x.x.x
```

This gives you direct evidence that the two containers share the expected network.

---

# 16. Inspecting the Compose Services

Use:

```bash
docker compose ps
```

This tells you:

- which services are running,
- container status,
- ports,
- health state when available.

This pairs nicely with:

```bash
docker network inspect
```

because you can reason about both:

```text
Service State
     +
Network State
```

---

# 17. Entering a Running Container

Use:

```bash
docker compose exec api sh
```

This opens a shell inside the running API container.

You can then inspect:

```bash
env
```

and verify:

```text
DB_HOST=db
```

This gives you an important debugging principle:

> **When something fails, inspect the environment from inside the same container where the application is failing.**

---

# 18. Connectivity Troubleshooting Flow

Suppose the FastAPI application reports:

```text
Could not connect to PostgreSQL
```

Don't immediately edit code.

Use:

```text
Is API container running?
        |
        v
docker compose ps
        |
        v
Is DB container running?
        |
        v
docker compose ps
        |
        v
Are both attached to the same network?
        |
        v
docker network inspect
        |
        v
Is DB_HOST correct?
        |
        v
DB_HOST=db
        |
        v
Is PostgreSQL healthy?
        |
        v
docker compose ps
        |
        v
Check API + DB logs
```

This creates a repeatable troubleshooting process.

---

# 19. Classic Failure Scenario

Suppose:

```env
DB_HOST=localhost
```

Your architecture is:

```text
+----------------------+
| FastAPI Container    |
|                      |
| DB_HOST=localhost    |
|        |             |
|        v             |
|   localhost:5432     |
+----------------------+

       PostgreSQL
       is actually here
              |
              v
+----------------------+
| PostgreSQL Container |
+----------------------+
```

So the connection fails.

The correct version:

```text
+----------------------+
| FastAPI Container    |
|                      |
| DB_HOST=db           |
|        |             |
|        v             |
| Docker DNS           |
+--------+-------------+
         |
         v
+----------------------+
| PostgreSQL Container |
| service: db          |
+----------------------+
```

---

# 20. Classic Port Confusion

Another common mistake is thinking:

```yaml
ports:
  - "5433:5432"
```

means PostgreSQL itself changed from port 5432 to 5433.

It did not.

The mapping means:

```text
Host port 5433
      |
      v
Container port 5432
```

So:

### From host

```text
localhost:5433
```

### From another container

```text
db:5432
```

This distinction is extremely important.

---

# 21. Host → Container vs Container → Container

Keep this diagram permanently:

```text
                 HOST MACHINE
                      |
                      |
              localhost:8000
                      |
                      v
             +----------------+
             | API Container  |
             +-------+--------+
                     |
                     | db:5432
                     v
             +----------------+
             | DB Container   |
             +----------------+
```

Two different routes:

```text
HOST → CONTAINER
    |
    +--> Published port

CONTAINER → CONTAINER
    |
    +--> Shared Docker network
    +--> Service discovery
```

---

# 22. Multiple Networks

A container can be connected to more than one Docker network. Docker compares this to connecting a physical host to multiple network segments. citeturn756014view0

For example:

```text
                 API Container
                 /                            /                             v                v
        frontend_net        backend_net
                                |
                                v
                              db
```

This becomes useful for isolating traffic.

For example:

```text
frontend
   |
   v
API

API
   |
   v
Database
```

while preventing the frontend from directly accessing the database.

This is an important architecture pattern as applications become larger.

---

# 23. Why Network Isolation Matters

User-defined networks can scope which containers communicate with each other. Docker documents this isolation as one of their advantages over putting unrelated containers onto a single default bridge network. citeturn756014view1

Conceptually:

```text
frontend network
   |
   +--> frontend
   +--> api

backend network
   |
   +--> api
   +--> db
```

Notice:

```text
frontend
   X
   |
   X
database
```

The API becomes the controlled boundary.

This is an important stepping stone toward real microservice networking.

---

# 24. Our Student Management Network

Our current system is simpler:

```text
                 student-management_default
                           |
              +------------+------------+
              |                         |
              v                         v
         FastAPI API                 PostgreSQL
          Container                  Container
              |                         |
              |                         |
              +------ db:5432 ----------+
```

And the host interacts with the API through:

```text
localhost:8000
```

while host-side database tools may use a separate published port if configured.

---

# 25. How This Connects to Day 26

Day 26 taught us:

```text
db starts
   |
   v
healthcheck
   |
   v
healthy
   |
   v
api starts
```

Day 28 adds:

```text
db starts
   |
   v
healthcheck
   |
   v
healthy
   |
   v
api starts
   |
   v
DNS resolves "db"
   |
   v
api connects to db:5432
```

So:

```text
Readiness
+
Networking
```

are two separate layers that work together.

---

# 26. How This Connects to Day 27

Day 27 taught:

```text
Configuration
```

Today we apply that configuration:

```text
DB_HOST=db
```

And now we understand what the value actually means.

The progression is:

```text
Day 19
Centralized configuration
        ↓
Day 25
DB_HOST=db appears in Compose
        ↓
Day 26
DB must be healthy
        ↓
Day 28
"db" is resolved through Docker networking
```

That is how the project is supposed to evolve.

---

# 27. Common Beginner Mistakes

### Mistake 1 — Using `localhost` for another container

```env
DB_HOST=localhost
```

Usually wrong for container-to-container communication.

---

### Mistake 2 — Hardcoding container IP addresses

```env
DB_HOST=172.18.0.3
```

Fragile because IP allocation is dynamic.

---

### Mistake 3 — Publishing every port

Not every internal service needs a host-facing port.

---

### Mistake 4 — Confusing host and container ports

```text
5433:5432
```

means:

```text
host 5433
    ↓
container 5432
```

not that PostgreSQL internally changed to 5433.

---

### Mistake 5 — Assuming a running container is enough

You learned on Day 26 that:

```text
running
   !=
healthy
```

Now add:

```text
networked
   !=
reachable
```

You still need to verify the network path and configuration.

---

# 28. Production Troubleshooting Mindset

When connectivity fails, inspect in this order:

```text
1. Process
   ↓
2. Container
   ↓
3. Health
   ↓
4. Network
   ↓
5. DNS/service name
   ↓
6. Port
   ↓
7. Credentials
   ↓
8. Application logs
```

This is a much stronger approach than changing five settings at once.

---

# 29. Interview Questions

### Q1. What is a Docker bridge network?

A bridge network is a Docker network that provides communication between containers connected to the same network while providing isolation from containers on other networks. citeturn756014view1

### Q2. How does a Compose service discover another service?

Through the Compose network and Docker's internal DNS/service discovery using the service name.

### Q3. Why does `DB_HOST=db` work?

Because `db` is the logical service name resolvable on the shared Docker network.

### Q4. Why does `localhost` usually fail for container-to-container communication?

Because `localhost` refers to the current container's own network namespace.

### Q5. Does container-to-container communication require published ports?

No. Containers connected to the same network can communicate internally without publishing the destination port to the host. citeturn756014view0turn756014view1

### Q6. Why avoid hardcoding container IPs?

Docker can dynamically allocate container IP addresses, especially when containers are recreated. citeturn756014view0

### Q7. How do you inspect a Docker network?

```bash
docker network inspect <network-name>
```

### Q8. How would you troubleshoot API → PostgreSQL connectivity?

Check:

```text
Container status
+
Health status
+
Shared network
+
DB_HOST
+
Internal port
+
Credentials
+
Logs
```

---

# 30. FastAPI ↔ ASP.NET Core Mapping

The networking concepts are framework-independent.

For example:

```text
ASP.NET Core API Container
          |
          | sqlserver:1433
          v
SQL Server Container
```

The .NET application would still use:

```text
service-name:internal-port
```

rather than:

```text
localhost
```

when the database is another container.

The underlying principle is:

> **Application services communicate through the network topology, not through assumptions about the host machine.**

---

# 31. Cheat Sheet

```text
Docker network
→ Logical network connecting containers

Bridge network
→ Local Docker network driver for container communication

User-defined bridge
→ Custom bridge network with service/container name resolution

Service name
→ Logical hostname such as "db"

Container IP
→ Dynamically assigned IP address

localhost
→ The current container/host network namespace

ports
→ Host ↔ container publishing

Internal communication
→ Container ↔ container over shared network

docker network ls
→ List networks

docker network inspect <network>
→ Inspect network details and attached containers

docker compose ps
→ Inspect Compose service state

docker compose exec api sh
→ Enter running API container

DB_HOST=db
→ Use Compose/Docker service discovery

DB_HOST=localhost
→ Look for PostgreSQL inside the current container
```

---

# 32. Final Mental Model

This is the most important diagram of Day 28:

```text
                         HOST MACHINE
                              |
                              |
                       localhost:8000
                              |
                              v
                    +-------------------+
                    | FastAPI Container |
                    |                   |
                    | DB_HOST=db        |
                    +---------+---------+
                              |
                              | DNS lookup: "db"
                              v
                    +-------------------+
                    | Docker Embedded    |
                    | DNS / Network      |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | PostgreSQL        |
                    | Container         |
                    |                   |
                    | db:5432           |
                    +-------------------+
```

Or, from the infrastructure perspective:

```text
                    Docker Compose
                          |
                          v
              student-management_default
                          |
              +-----------+-----------+
              |                       |
              v                       v
             api                     db
              |                       |
              |                       |
              +---- Docker DNS -------+
                     |
                     v
                 db:5432
```

And the most important rule:

```text
localhost
    ↓
"this network namespace"

service name
    ↓
"that service on my Docker network"
```

---

# Key Takeaways

- Docker networking allows containers to communicate without exposing every service to the host.
- User-defined bridge networks provide useful isolation and automatic name-based resolution between connected containers. citeturn756014view1
- Docker Compose uses networking and service discovery so the API can connect to PostgreSQL through `db:5432`.
- `localhost` inside the FastAPI container refers to the FastAPI container itself.
- Published ports are primarily for host/external access; they are not normally required for same-network container-to-container communication. citeturn756014view0
- Container IPs are dynamically allocated, so applications should use logical service names rather than hardcoded container IP addresses. citeturn756014view0
- `docker network ls` and `docker network inspect` are essential troubleshooting tools.
- Connectivity troubleshooting should proceed systematically through process → container → health → network → DNS → port → credentials → logs.
- Today's networking layer builds directly on the health checks, environment management, and Compose architecture from Days 25–27.

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
Internal Networking
+
DNS
+
Network Inspection
+
Connectivity Troubleshooting
```

The important progression is:

```text
Run Containers
      ↓
Run Services
      ↓
Make Services Healthy
      ↓
Configure Services
      ↓
Connect Services
      ↓
Troubleshoot the System
```

That is the mindset we're building for the ₹50L target: **not merely knowing technologies, but understanding the system they form together.**

---

# Revision Checklist

- [ ] Can explain bridge networking.
- [ ] Can explain user-defined bridge networks.
- [ ] Understand Docker Compose's application network.
- [ ] Understand service-name DNS.
- [ ] Can explain why `DB_HOST=db` works.
- [ ] Can explain why `DB_HOST=localhost` fails.
- [ ] Understand host ports vs internal container ports.
- [ ] Understand why PostgreSQL does not need a published port for API → DB communication.
- [ ] Can inspect Docker networks.
- [ ] Can enter a running container and inspect its environment.
- [ ] Can troubleshoot a connectivity failure systematically.
- [ ] Can explain the complete FastAPI → Docker DNS → PostgreSQL flow.

---

# Exact Resources Used

- Docker Docs — Networking overview: https://docs.docker.com/engine/network/
- Docker Docs — Bridge network driver: https://docs.docker.com/engine/network/drivers/bridge/
- Docker Docs — Networking in Compose: https://docs.docker.com/compose/how-tos/networking/

These resources were selected specifically for Day 028's internal networking, bridge networks, service discovery, published ports, DNS, inspection, and connectivity troubleshooting objectives.
