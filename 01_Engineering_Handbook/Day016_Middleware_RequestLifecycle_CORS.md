# Day 016 — Middleware, HTTP Request Lifecycle & CORS

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 26 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand what Middleware is.
- Understand the complete HTTP Request → Response lifecycle.
- Create custom middleware in FastAPI.
- Measure request execution time.
- Log incoming requests.
- Understand CORS and why browsers enforce it.
- Compare FastAPI Middleware with ASP.NET Core Middleware.
- Understand where Middleware fits in a Clean Architecture application.

---

# Big Picture

Yesterday our application looked like this:

```text
Client

↓

Authentication

↓

Router

↓

Service

↓

Repository

↓

Database
```

Today we add Middleware.

```text
Client

↓

Middleware

↓

Authentication

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Middleware

↓

Client
```

Middleware wraps the entire request lifecycle.

---

# 1. What is Middleware?

Middleware is a piece of code that executes:

- before a request reaches your router.
- after your router returns a response.

Think of it as a security checkpoint at an airport.

Every passenger passes through it.

Nobody can skip it.

---

# Middleware Diagram

```text
HTTP Request

↓

Middleware

↓

Router

↓

Business Logic

↓

Response

↓

Middleware

↓

Client
```

Middleware surrounds your application.

---

# 2. Why Do We Need Middleware?

Suppose you have 150 API endpoints.

You want to:

- log every request,
- measure execution time,
- add security headers,
- validate JWT,
- enable CORS.

Should you write the same code inside all 150 endpoints?

No.

Write it once.

Middleware automatically executes for every request.

---

# 3. FastAPI Middleware

Basic syntax:

```python
@app.middleware("http")
async def middleware(request, call_next):

    response = await call_next(request)

    return response
```

The important function is:

```python
call_next(request)
```

This forwards the request to the next stage.

Without it, your request never reaches the router.

---

# Request Lifecycle

```text
Browser

↓

HTTP Request

↓

Middleware

↓

Authentication

↓

Dependency Injection

↓

Validation

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Repository

↓

Service

↓

Router

↓

Middleware

↓

HTTP Response

↓

Browser
```

This is the complete backend execution flow.

---

# 4. Request Object

Inside middleware you receive:

```python
request
```

It contains information such as:

- URL
- Method
- Headers
- Client IP
- Cookies
- Query Parameters

Example:

```python
print(request.method)

print(request.url.path)
```

Output:

```text
GET

/students
```

---

# 5. Response Object

After

```python
response = await call_next(request)
```

you receive:

```python
response
```

Now you can:

- modify headers,
- inspect status codes,
- add metadata.

Example:

```python
response.headers["X-Version"] = "1.0"
```

---

# 6. Measuring Response Time

Example:

```python
import time

start = time.time()

response = await call_next(request)

end = time.time()

response.headers["X-Process-Time"] = str(end - start)
```

Now every API response includes:

```text
X-Process-Time

0.0231
```

Very common in production systems.

---

# Response Timing Flow

```text
Request

↓

Record Start Time

↓

Router

↓

Business Logic

↓

Response

↓

Record End Time

↓

Execution Time

↓

Response Header
```

---

# 7. Request Logging

Example:

```python
print(

request.method,

request.url.path

)
```

Example Output:

```text
GET /students

POST /students

DELETE /students/5
```

Logging helps during debugging and production monitoring.

---

# 8. Multiple Middleware

FastAPI executes middleware in layers.

Suppose:

```text
Middleware A

Middleware B

Router
```

Execution order:

```text
Request

↓

A

↓

B

↓

Router

↓

B

↓

A

↓

Response
```

Think of nested boxes.

---

# Middleware Execution Diagram

```text
Request

↓

Middleware A

↓

Middleware B

↓

Router

↓

Middleware B

↓

Middleware A

↓

Response
```

This is called the Middleware Pipeline.

---

# 9. Common Middleware in Real Applications

Production applications often include middleware for:

- Request Logging
- Response Timing
- Authentication
- Authorization
- CORS
- Compression
- GZip
- Rate Limiting
- Security Headers
- Exception Handling
- Correlation IDs

Notice these are all cross-cutting concerns.

None belong inside business logic.

---

# 10. What is CORS?

CORS means:

**Cross-Origin Resource Sharing**

Browsers restrict JavaScript from making requests to different origins.

---

# What is an Origin?

An origin consists of:

```text
Protocol

+

Host

+

Port
```

Example:

```text
http://localhost:5173
```

and

```text
http://localhost:8000
```

Different ports.

Different origins.

---

# Why Browsers Block Requests

Suppose:

React

```text
localhost:5173
```

tries to call

FastAPI

```text
localhost:8000
```

Without CORS:

❌ Browser blocks the request.

With CORS:

✅ Browser allows the request according to your configured policy.

---

# CORS Diagram

```text
React

localhost:5173

↓

Browser

↓

FastAPI

localhost:8000

↓

Allowed?

↓

YES

↓

Response
```

---

# FastAPI CORS Configuration

Example:

```python
app.add_middleware(

CORSMiddleware,

allow_origins=["http://localhost:5173"],

allow_credentials=True,

allow_methods=["*"],

allow_headers=["*"]

)
```

This tells the browser:

"This origin is trusted."

---

# 11. Middleware vs Dependency Injection

Middleware:

Runs for **every request**.

Dependency Injection:

Runs only for endpoints that request that dependency.

Example:

```text
Middleware

↓

Every Request
```

vs

```text
Depends()

↓

Only Selected Endpoints
```

Different responsibilities.

---

# 12. Middleware vs Router vs Service

| Layer      | Responsibility         |
| ---------- | ---------------------- |
| Middleware | Cross-cutting concerns |
| Router     | HTTP endpoints         |
| Service    | Business logic         |
| Repository | Database access        |

Keep responsibilities separate.

---

# 13. Clean Architecture Placement

```text
Browser

↓

Middleware

↓

Router

↓

Dependency Injection

↓

Service

↓

Repository

↓

Database
```

Middleware sits outside your application layers.

It should never contain business logic.

---

# 14. ASP.NET Core Comparison

ASP.NET Core:

```csharp
app.UseAuthentication();

app.UseAuthorization();

app.UseRouting();
```

FastAPI:

```python
@app.middleware("http")
```

Same architectural concept.

Different syntax.

---

# Common Beginner Mistakes

❌ Forgetting:

```python
await call_next(request)
```

The request never reaches the router.

---

❌ Writing business logic inside middleware.

---

❌ Logging sensitive information like passwords or JWT secrets.

---

❌ Allowing every origin in production:

```python
allow_origins=["*"]
```

Avoid this in real deployments.

---

# Production Best Practices

✅ Keep middleware focused.

✅ Log useful information only.

✅ Measure execution time.

✅ Add security headers.

✅ Configure CORS explicitly.

✅ Never place business logic inside middleware.

---

# Interview Questions

### Q1. What is Middleware?

Middleware is software that executes before and after every HTTP request.

---

### Q2. Why use Middleware?

To implement cross-cutting concerns such as logging, authentication, CORS, timing, and security without duplicating code.

---

### Q3. What does `call_next(request)` do?

It forwards the request to the next stage of the application.

---

### Q4. What is CORS?

A browser security mechanism that controls which origins are allowed to access another origin's resources.

---

### Q5. Why doesn't Postman require CORS?

Because CORS is enforced by web browsers.

Postman is not a browser.

---

### Q6. Difference between Middleware and Dependency Injection?

Middleware runs for every request.

Dependency Injection runs only where explicitly requested.

---

### Q7. Can Middleware modify responses?

Yes.

It can:

- add headers,
- inspect status codes,
- log execution time,
- modify response metadata.

---

# Cheat Sheet

```text
Request

↓

Middleware

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Response

↓

Middleware
```

---

```python
@app.middleware("http")
```

↓

Every Request

---

```python
await call_next(request)
```

↓

Continue Request Pipeline

---

```python
CORSMiddleware
```

↓

Browser Security

---

# 🏗 Why does this exist?

## What problem does it solve?

Many concerns apply to every request rather than a single endpoint.

Instead of duplicating code across dozens of routers, middleware provides one centralized place to implement those concerns.

---

## Who depends on it?

```text
Browser

↓

Middleware

↓

Entire Application
```

Every incoming HTTP request passes through middleware before reaching your application.

---

## Who should NOT depend on it?

Repositories.

Services.

Business logic.

Middleware should not know how students are created, updated, or deleted.

Its responsibility is infrastructure-level processing.

---

## ASP.NET Core Equivalent

```csharp
app.UseRouting();

app.UseAuthentication();

app.UseAuthorization();
```

---

## FastAPI Equivalent

```python
@app.middleware("http")
```

---

# Key Takeaways

- Middleware executes before and after every HTTP request.
- `call_next(request)` forwards the request through the pipeline.
- Middleware is ideal for logging, timing, security headers, and CORS.
- CORS is a browser security feature that controls cross-origin requests.
- Middleware should never contain business logic.
- Every modern backend framework provides a middleware pipeline.

---

# Revision Checklist

- [ ] Can explain Middleware.
- [ ] Understand the Request → Response lifecycle.
- [ ] Can create custom middleware.
- [ ] Can measure response time.
- [ ] Understand how CORS works.
- [ ] Know why browsers enforce CORS.
- [ ] Can explain Middleware vs Dependency Injection.
- [ ] Can compare FastAPI Middleware with ASP.NET Core Middleware.

---

# Tomorrow's Preview

- Structured Logging
- Python Logging Module
- Log Levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Centralized Logging Configuration
- Exception Logging
- Debugging Production Applications
- Building a professional logging strategy for backend services
