# Day 021 — Database Connection Pooling & FastAPI Lifespan Events

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 04 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand why database connection pooling is required.
- Explain how a connection pool improves application performance.
- Understand the lifecycle of a database connection.
- Use Psycopg ConnectionPool in FastAPI.
- Understand FastAPI Lifespan Events.
- Initialize and clean up application resources correctly.
- Compare FastAPI Lifespan with ASP.NET Core Startup.
- Explain connection pooling confidently in interviews.

---

# Big Picture

Yesterday our backend looked like this:

```text
Client

↓

Router

↓

Service

↓

Repository

↓

Transaction

↓

Database
```

Today we introduce a shared database connection pool.

```text
                 FastAPI

                    │

             Lifespan Startup

                    │

        Create Connection Pool

                    │

          Shared Connection Pool

         ┌────────┼────────┐

         ▼        ▼        ▼

      Conn1    Conn2    Conn3

         │        │        │

         └────────┼────────┘

                  ▼

             PostgreSQL
```

Instead of creating a new database connection for every request, the application reuses existing connections.

---

# 1. Why Database Connections are Expensive

Every time an application creates a new database connection, PostgreSQL must:

- Authenticate the user
- Allocate memory
- Create a backend process
- Establish network communication
- Prepare the session

Creating a connection is much more expensive than executing a SQL query.

---

# Without Connection Pooling

Suppose 100 users access your API simultaneously.

```text
Request 1

↓

Open Connection

↓

Query

↓

Close Connection

────────────────────

Request 2

↓

Open Connection

↓

Query

↓

Close Connection

────────────────────

...

100 Requests

↓

100 New Connections
```

This wastes CPU, memory, and time.

---

# With Connection Pooling

```text
Application Starts

↓

Create Pool (10 Connections)

↓

Request

↓

Borrow Connection

↓

Execute Query

↓

Return Connection

↓

Pool Ready Again
```

Connections are reused instead of recreated.

---

# Visual Comparison

Without Pool

```text
Request

↓

Open

↓

Authenticate

↓

Execute

↓

Close
```

With Pool

```text
Request

↓

Borrow

↓

Execute

↓

Return
```

Notice that authentication only happens once when the pool is created.

---

# 2. What is a Connection Pool?

A connection pool is a collection of already-open database connections maintained by the application.

Instead of opening a new connection every time:

```text
Request

↓

Pool

↓

Existing Connection

↓

Database
```

When finished:

```text
Connection

↓

Returned

↓

Pool
```

The next request reuses the same connection.

---

# Pool Architecture

```text
                 Pool

       ┌──────┬──────┬──────┐

       │      │      │

    Conn1  Conn2  Conn3

       │      │      │

       └──────┴──────┴──────┘

                │

          PostgreSQL
```

---

# 3. Psycopg Connection Pool

Install:

```bash
pip install "psycopg[pool]"
```

Example:

```python
from psycopg_pool import ConnectionPool

pool = ConnectionPool(

    conninfo=settings.database_url,

    min_size=2,

    max_size=10
)
```

The pool automatically manages database connections.

---

# Borrowing a Connection

```python
with pool.connection() as conn:

    with conn.cursor() as cursor:

        cursor.execute(...)
```

The connection is automatically returned to the pool after the `with` block ends.

---

# Pool Lifecycle

```text
Application Starts

↓

Pool Created

↓

Borrow

↓

Execute

↓

Return

↓

Borrow Again

↓

Application Stops

↓

Pool Closed
```

---

# 4. FastAPI Lifespan

FastAPI provides a special mechanism for initializing resources.

Instead of creating resources inside every request:

```python
@app.get(...)
```

Create them once during application startup.

---

# Lifespan Flow

```text
Application Start

↓

Load Configuration

↓

Initialize Logger

↓

Create Connection Pool

↓

Application Running

↓

Serve Requests

↓

Application Shutdown

↓

Close Connection Pool
```

---

# Lifespan Example

```python
from contextlib import asynccontextmanager

@asynccontextmanager

async def lifespan(app):

    # Startup

    create_connection_pool()

    yield

    # Shutdown

    close_connection_pool()
```

Then:

```python
app = FastAPI(

    lifespan=lifespan
)
```

---

# Why Use Lifespan?

Because expensive resources should only be created once.

Examples:

- Database Connection Pool
- Redis Cache
- Machine Learning Model
- Logger
- Configuration
- Message Queue Connections

---

# 5. Application Startup vs Shutdown

Startup responsibilities:

- Load configuration
- Initialize logging
- Create database pool
- Verify external services

Shutdown responsibilities:

- Close connection pool
- Flush logs
- Close external connections
- Release resources

---

# Lifecycle Diagram

```text
Application

↓

Startup

↓

Configuration

↓

Logger

↓

Connection Pool

↓

Requests

↓

Shutdown

↓

Close Pool

↓

Exit
```

---

# 6. Clean Architecture Responsibility

Where should the pool be created?

```text
main.py

↓

Lifespan

↓

Connection Pool

↓

Repository
```

Responsibilities:

- **main.py** → Application lifecycle
- **Lifespan** → Resource initialization
- **Repository** → Borrow and return connections
- **Service** → Business logic
- **Router** → HTTP communication

Repositories should use the pool but never create it themselves.

---

# Request Flow

```text
Client

↓

Router

↓

Service

↓

Repository

↓

Borrow Connection

↓

Execute SQL

↓

Return Connection

↓

Response
```

The repository borrows a connection only for the duration of the database operation.

---

# 7. Pool Configuration

Example:

```python
pool = ConnectionPool(

    conninfo=settings.database_url,

    min_size=2,

    max_size=10
)
```

Meaning:

- Minimum 2 connections are always available.
- Maximum 10 connections may exist simultaneously.

---

# Choosing Pool Size

Too Small:

```text
Requests Waiting

↓

Slow Response
```

Too Large:

```text
Too Many Connections

↓

Database Overloaded
```

A reasonable starting point for small applications is 5–10 connections, then tune based on workload.

---

# 8. Common Production Error

```text
too many clients already
```

Possible causes:

- Connection leak
- Connections never returned
- Pool too small
- Opening new connections for every request

Always check connection management before blaming PostgreSQL.

---

# Logging + Pooling

```text
Request

↓

Borrow Connection

↓

Execute Query

↓

Return Connection

↓

Logger
```

If a connection cannot be obtained, log the event for troubleshooting.

---

# FastAPI vs ASP.NET Core

ASP.NET Core

```csharp
builder.Services.AddDbContext(...);
```

Entity Framework automatically uses connection pooling underneath.

Application startup:

```csharp
var builder = WebApplication.CreateBuilder(args);
```

FastAPI

```python
lifespan

↓

ConnectionPool()

↓

Repositories
```

Different syntax.

Same architectural principle.

---

# Best Practices

✅ Create one shared pool for the application.

✅ Use FastAPI Lifespan to initialize resources.

✅ Return connections immediately after use.

✅ Keep transactions short.

✅ Monitor connection usage in production.

---

# Common Beginner Mistakes

❌ Creating a new connection for every request.

❌ Forgetting to close the pool during shutdown.

❌ Holding connections longer than necessary.

❌ Sharing one connection across multiple requests.

❌ Creating multiple pools unnecessarily.

---

# Real-World Examples

Connection pools are used by:

- Banking systems
- E-commerce platforms
- Payment gateways
- Airline booking systems
- Social media applications
- Enterprise REST APIs

Any application handling multiple concurrent users benefits from connection pooling.

---

# Interview Questions

### Q1. Why is opening a database connection expensive?

Because PostgreSQL must authenticate the user, allocate resources, create backend processes, and establish communication before executing queries.

---

### Q2. What is a connection pool?

A collection of reusable database connections shared across requests to improve performance and reduce overhead.

---

### Q3. Why use FastAPI Lifespan?

It allows expensive resources such as database pools, loggers, and ML models to be initialized once during startup and cleaned up during shutdown.

---

### Q4. Where should a connection pool be created?

During application startup, typically in `main.py` using FastAPI Lifespan.

---

### Q5. Should repositories create database connections?

No.

Repositories should borrow connections from the shared pool and return them when finished.

---

### Q6. What happens if connections are never returned?

The pool becomes exhausted, leading to errors such as:

```text
too many clients already
```

---

# Cheat Sheet

```text
Application Start

↓

Create Pool

↓

Borrow

↓

Execute

↓

Return

↓

Shutdown

↓

Close Pool
```

---

```python
pool = ConnectionPool(...)

with pool.connection() as conn:

    ...
```

---

# 🏗 Why does this exist?

## What problem does it solve?

Without pooling:

- Every request creates a new database connection.
- Applications become slower.
- Database resources are wasted.
- Scalability decreases.

Connection pooling solves these problems by reusing existing connections.

---

## Who depends on it?

```text
Router

↓

Service

↓

Repository

↓

Connection Pool

↓

PostgreSQL
```

Every repository performing database operations depends on the connection pool.

---

## Who should NOT depend on it?

Business logic.

The Service layer should never know whether connections come from a pool or are created directly.

That responsibility belongs to the infrastructure layer.

---

## ASP.NET Core Equivalent

```csharp
AddDbContext()

Connection Pooling

Program.cs
```

---

## FastAPI Equivalent

```python
ConnectionPool()

lifespan

main.py
```

---

# Key Takeaways

- Database connections are expensive resources.
- Connection pooling dramatically improves performance by reusing existing connections.
- FastAPI Lifespan provides a clean mechanism for application startup and shutdown.
- Connection pools belong to the application's infrastructure layer.
- Repositories should borrow connections from the pool instead of creating new ones.
- Proper connection management is essential for scalable, production-ready backend systems.

---

# Revision Checklist

- [ ] Understand why database connections are expensive.
- [ ] Can explain what a connection pool is.
- [ ] Know how Psycopg ConnectionPool works.
- [ ] Understand FastAPI Lifespan events.
- [ ] Know where connection pools belong in Clean Architecture.
- [ ] Can compare FastAPI and ASP.NET Core connection management.
- [ ] Can explain connection pooling confidently in an interview.

---

# 🏗 Engineering Evolution

Our Student Management backend now includes another enterprise-grade capability:

```text
Day 016
Middleware
        │
        ▼
Day 017
Structured Logging
        │
        ▼
Day 018
Global Exception Handling
        │
        ▼
Day 019
Configuration Management
        │
        ▼
Day 020
Database Transactions
        │
        ▼
Day 021
Connection Pooling
```

Notice the progression.

We're moving from writing correct code to building systems that are **efficient**, **scalable**, and **production-ready**.

A backend can function perfectly with a single database connection, but it cannot scale to hundreds or thousands of concurrent users without proper connection management.

---

# Connection Pool Mental Model

Imagine a restaurant.

Without a pool:

```text
Every Customer

↓

Restaurant Builds New Table

↓

Customer Eats

↓

Destroy Table
```

Ridiculous!

Instead:

```text
Restaurant Opens

↓

10 Tables Ready

↓

Customer Uses Table

↓

Leaves

↓

Next Customer Uses Same Table
```

A connection pool works exactly the same way.

The database connections (tables) are created once, reused many times, and finally cleaned up when the application shuts down.

---

# Tomorrow's Preview

- Database Indexing
- Query Performance
- EXPLAIN & EXPLAIN ANALYZE
- Primary Index vs Secondary Index
- Optimizing Slow Queries
- Reading Query Execution Plans
