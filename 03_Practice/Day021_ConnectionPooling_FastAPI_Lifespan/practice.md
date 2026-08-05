# Day 021: Connection Pooling and FastAPI Lifespan

## Exercise 1

- Create a simple `ConnectionPool`.
- Borrow one connection.
- Return the connection to the pool.

## Exercise 2

- Create multiple queries using the same pool.
- Observe that new connections are not created every time.

## Exercise 3

- Refactor your Student Management project.
- Instead of creating a new connection inside every operation:

```python
psycopg.connect(...)
```

- Use a shared connection pool.

## Exercise 4

- Implement FastAPI Lifespan.

### During Startup

- Load configuration.
- Initialize logger.
- Create database pool.

### During Shutdown

- Close database pool.

## Exercise 5

- Trace the request flow:

```text
Client
  ↓
Router
  ↓
Service
  ↓
Repository
  ↓
Pool
  ↓
Database
```

- Understand exactly where the connection is acquired and released.
