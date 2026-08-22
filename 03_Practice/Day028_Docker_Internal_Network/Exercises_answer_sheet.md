# Docker Internal Network — Exercise Answer Sheet

**Project:** Student Management REST API  
**Day:** 028  
**Date:** 2026-08-22  
**Version at completion:** v21 (14.0.0)

---

## Exercise 1 — Inspect Your Compose Network ✅

**Task:** Run `docker network ls` and `docker network inspect <name>`, then answer: if `db` already has an IP, why use the service name instead?

### Commands run

```bash
docker network ls
docker network inspect miniproject_student_management_default
```

### `docker network ls` output

```
NETWORK ID     NAME                                     DRIVER    SCOPE
40ff4b5244c2   bridge                                   bridge    local
b70bc023557d   host                                     host      local
49a04d53570e   miniproject_student_management_default   bridge    local
1353faae378c   none                                     null      local
```

Compose automatically created `miniproject_student_management_default` — named after the project directory.

### `docker network inspect` output (key sections)

```json
{
  "Name": "miniproject_student_management_default",
  "Driver": "bridge",
  "IPAM": {
    "Config": [
      {
        "Subnet": "172.18.0.0/16",
        "Gateway": "172.18.0.1"
      }
    ]
  },
  "Containers": {
    "...api-1": {
      "Name": "miniproject_student_management-api-1",
      "IPv4Address": "172.18.0.3/16"
    },
    "...db-1": {
      "Name": "miniproject_student_management-db-1",
      "IPv4Address": "172.18.0.2/16"
    }
  }
}
```

### Observed values

| Field            | Value                                    |
| ---------------- | ---------------------------------------- |
| Network name     | `miniproject_student_management_default` |
| Driver           | `bridge`                                 |
| Subnet           | `172.18.0.0/16`                          |
| Gateway          | `172.18.0.1`                             |
| api container IP | `172.18.0.3`                             |
| db container IP  | `172.18.0.2`                             |

### Answer: Why use `db` instead of the IP address?

**Because container IPs are not a stable contract — service names are.**

Every time `docker compose down` + `docker compose up` is run, Docker reassigns container IPs. On the next run, `db` might get `172.18.0.3` instead of `172.18.0.2`. Any application that hardcoded `172.18.0.2` would silently fail after a restart.

Service names, by contrast, are always stable — `db` always resolves to whatever IP the `db` container currently holds. Docker's embedded DNS (`127.0.0.11`) performs this resolution at every connection, not at startup.

---

## Exercise 2 — Inspect DNS from the API Container ✅

**Task:** Enter the api container, check `DB_HOST`, and understand the DNS resolution flow.

### Commands run

```bash
docker compose exec api sh -c "env | grep DB_HOST; cat /etc/resolv.conf"
```

### Output

```
DB_HOST=db

nameserver 127.0.0.11
options ndots:0
```

### What this proves

**`DB_HOST=db`** — the environment variable that our FastAPI application reads is exactly `db`. When `psycopg` opens a connection, it resolves `db` through the OS DNS stack.

**`nameserver 127.0.0.11`** — Docker injects this into `/etc/resolv.conf` for every container. `127.0.0.11` is Docker's internal DNS resolver. When the api container asks "what is the IP of `db`?", the query goes to `127.0.0.11`, which looks up the container on the `miniproject_student_management_default` bridge network and returns `172.18.0.2`.

### The resolution flow

```
Application (FastAPI / psycopg)
      |
      | connect("db", 5432)
      v
OS DNS resolver
      |
      | query: db → nameserver 127.0.0.11
      v
Docker embedded DNS (127.0.0.11)
      |
      | lookup: "db" on miniproject_student_management_default
      | answer: 172.18.0.2
      v
PostgreSQL Container (172.18.0.2:5432)
      |
      v
PostgreSQL Server
```

---

## Exercise 3 — Prove the `localhost` Difference ✅

**Task:** Understand what would happen if `DB_HOST=localhost` were used inside Docker.

### The mental model

Each Docker container runs in its own **network namespace**. A network namespace has its own:

- Loopback interface (`lo`, `127.0.0.1`)
- Network interfaces and routing table

When `DB_HOST=localhost` is set inside the **api** container:

```
API Container
      |
      | connect("localhost", 5432)
      v
Resolves to 127.0.0.1  ← the api container's own loopback
      |
      v
No process listening on 5432 inside the api container
      |
      v
Connection refused / timeout
```

PostgreSQL is in a completely separate container — a separate network namespace. Its `127.0.0.1` is unreachable from the api container.

### What the error would look like

```
error connecting in 'pool-1': failed to connect to host=localhost user=postgres database=student_db
Connection refused
```

(This is exactly the error seen in early Day 025 experiments before `DB_HOST=db` was set correctly.)

### Rule

> Inside Docker Compose: **`DB_HOST` must always be the service name (`db`), never `localhost`.**

`localhost` only works if both the client and the server process run inside the **same** container.

---

## Exercise 4 — Remove PostgreSQL's Published Port Experiment ✅

**Task:** Understand what the `db` port mapping is for and whether the api needs it.

### Current port mapping

```yaml
db:
  ports:
    - "5433:5432" # host port 5433 → container port 5432
```

### Two completely different connection paths

```
                              Docker Network

                    +---------------------------------------+
                    |                                       |
                    |   api (172.18.0.3)                    |
                    |        |                              |
                    |        | DB_HOST=db → db:5432         |
                    |        v                              |
                    |   db  (172.18.0.2:5432)               |
                    |                                       |
                    +---------------------------------------+

    Windows Host
         |
         | localhost:5433 → published port → db container:5432
         v
    pgAdmin / psql / DBeaver
```

**Internal path (api → db):**

- The api container reaches Postgres via `db:5432` through the bridge network.
- **The `ports:` mapping is completely irrelevant for this path.**
- If the `ports:` section were removed entirely, the api would still work perfectly.

**External path (host tools → db):**

- Tools on the Windows host (pgAdmin, psql CLI) have no access to the Docker bridge network.
- The only way they can reach the db container is through the published port.
- `localhost:5433` on the host → Docker port-forwarding → `db:5432` inside the container.

### What happens if the db port mapping is removed?

| Client         | Effect of removing `5433:5432`    |
| -------------- | --------------------------------- |
| FastAPI (api)  | **No effect** — uses internal DNS |
| pgAdmin (host) | **Connection fails** — no path    |
| psql on host   | **Connection fails** — no path    |

**Decision for this project:** Keep `5433:5432` for developer convenience (pgAdmin access). The comment in `compose.yaml` now explicitly documents this distinction.

---

## Mini Project Task — Full Architecture Verified ✅

**Task:** Verify and document the complete network architecture.

### Full end-to-end traffic flow (verified live)

```
Browser
  |
  | http://localhost:8000
  v
Windows Host (port published by Docker)
  |
  | 8000:8000 port mapping
  v
FastAPI Container  (api, 172.18.0.3)
  |
  | DB_HOST=db → Docker DNS (127.0.0.11) → 172.18.0.2
  v
Docker Bridge Network  (miniproject_student_management_default)
  |
  v
PostgreSQL Container  (db, 172.18.0.2) port 5432 internal
  |
  v
PostgreSQL Server (student_db)
```

### Key networking facts from live experiments

| Fact                                 | Evidence                                                       |
| ------------------------------------ | -------------------------------------------------------------- |
| Network driver                       | `bridge`                                                       |
| Subnet                               | `172.18.0.0/16`                                                |
| Docker DNS server IP                 | `127.0.0.11` (from `/etc/resolv.conf` inside api container)    |
| `DB_HOST` value inside api container | `db` (confirmed via `env grep DB_HOST`)                        |
| api container IP                     | `172.18.0.3`                                                   |
| db container IP                      | `172.18.0.2`                                                   |
| IPs stable across restarts?          | **No** — reassigned each `docker compose up`                   |
| Service name stable across restarts? | **Yes** — `db` always resolves to whatever IP db currently has |

### compose.yaml changes made (Day 028)

1. **Header** — added Day 028 note, full end-to-end traffic flow diagram, 3 new diagnostic commands
2. **`api` service** — networking note: why `DB_HOST=db` works and why `localhost` fails
3. **`db` ports** — expanded comment documenting internal vs external connectivity paths
4. **Networks section** — full documentation block at bottom of compose.yaml

---

_Answer sheet written: 2026-08-22_
