# Docker Compose Exercises

## Exercise 1 — Create the Compose file

Your project already has a `compose.yaml` placeholder.

Today, turn it into an actual Compose configuration.

**Start with only:**

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"

  db:
    image: postgres:latest
```

**Don't blindly copy this and move on.**

**Understand the structure:**

```
services
│
├── api
│   └── build: .
│
└── db
    └── image: postgres
```

---

## Exercise 2 — Create the PostgreSQL container properly

Now configure the PostgreSQL service with:

- PostgreSQL image
- Database name
- Username
- Password
- Persistent volume

**Your goal structure:**

```
db service
│
├── PostgreSQL image
├── POSTGRES_DB (environment variable)
├── POSTGRES_USER (environment variable)
├── POSTGRES_PASSWORD (environment variable)
└── volume (persistent storage)
```

**⚠️ Important:** Don't commit real passwords/secrets to GitHub.

---

## Exercise 3 — Fix the database configuration

This is where today's lesson becomes real.

Your current Dockerized application was using:

```
DB_HOST=host.docker.internal
```

This was necessary because PostgreSQL was running on your host machine.

**Now PostgreSQL is inside Compose.**

**Change the configuration conceptually to:**

```
DB_HOST=db
```

**Why?** Because `db` is the service name in your Docker Compose file.

**Then understand the complete flow:**

```
FastAPI Container
│
│ (uses DB_HOST=db)
▼
Docker DNS
│
▼
db service name
│
▼
PostgreSQL container
```

---

## Exercise 4 — Start the entire application with ONE command

**Run:**

```bash
docker compose up
```

**Then inspect:**

```bash
docker compose ps
```

You should see both services running.

**Expected output (names may differ):**

```
NAME                 SERVICE   STATUS
student-api-1        api       Up
student-db-1         db       Up
```

---

## Exercise 5 — Verify the API

**Open your browser and navigate to:**

```
http://localhost:8000/docs
```

**Verify all endpoints work:**

- ✅ Swagger UI loads
- ✅ GET /students works
- ✅ POST /students works
- ✅ GET /students/{id} works
- ✅ PUT /students/{id} works
- ✅ DELETE /students/{id} works

**Your complete architecture should now be:**

```
Browser
│
▼
localhost:8000
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
PostgreSQL Container
```

---

## Exercise 6 — Prove that service-name networking works

**This is your must-do experiment.**

Intentionally break the configuration to understand networking:

1. **Change:** `DB_HOST=db` **to:** `DB_HOST=localhost`
2. **Restart the Compose stack:**
   ```bash
   docker compose down
   docker compose up
   ```
3. **Observe the failure** (API cannot connect to database)
4. **Inspect the error logs:**
   ```bash
   docker compose logs api
   ```
5. **Find the actual connection error** in the output
6. **Then restore:** `DB_HOST=db`
7. **Restart again** and verify it works

**Why this matters:** This experiment is worth more than memorizing the networking explanation. You'll understand at a visceral level why Docker Compose service-name networking is essential.

**By the end,** you should be able to explain exactly why `DB_HOST=localhost` fails inside a Docker container.

---

## Exercise 7 — Learn the essential Compose commands

You should be able to explain each of these without looking them up:

**Basic operations:**

```bash
docker compose up          # Start services in foreground
docker compose up -d       # Start services in background (detached)
docker compose down        # Stop and remove containers
```

**Monitoring:**

```bash
docker compose ps          # Show running services
docker compose logs        # Show logs from all services
docker compose logs api    # Show logs from specific service
```

**Building:**

```bash
docker compose build       # Build images without starting
docker compose up --build  # Rebuild images and start
```
