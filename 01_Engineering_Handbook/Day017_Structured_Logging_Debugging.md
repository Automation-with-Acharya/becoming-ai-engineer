# Day 017 — Structured Logging, Debugging & Python Logging

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 28 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand why logging is essential in backend applications.
- Configure Python's built-in `logging` module.
- Understand different log levels and when to use them.
- Log messages to both the console and files.
- Replace `print()` statements with professional logging.
- Log exceptions correctly with stack traces.
- Understand the role of logging in debugging production applications.
- Compare Python logging with ASP.NET Core's `ILogger`.

---

# Big Picture

Yesterday our backend looked like this:

```text
Client

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
```

Today we introduce logging.

```text
Client

↓

Middleware

↓

Logger

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Logger

↓

Middleware

↓

Client
```

Every significant event inside the application can now be recorded.

---

# 1. What is Logging?

Logging is the process of recording information about what an application is doing while it is running.

Logs help developers:

- Understand application behavior.
- Debug failures.
- Investigate production incidents.
- Monitor application health.
- Audit important operations.

Unlike `print()`, logs are structured, searchable, and can be stored permanently.

---

# Why Not Use print()?

Suppose your application runs on a cloud server.

You are not connected to its terminal.

A `print()` statement disappears after the application stops.

A log entry can be:

- saved,
- searched,
- filtered,
- archived,
- monitored.

That's why production systems use logging instead of `print()`.

---

# print() vs Logging

| print()              | Logging              |
| -------------------- | -------------------- |
| Temporary            | Permanent            |
| Console only         | Console, File, Cloud |
| No severity          | Log Levels           |
| Not searchable       | Searchable           |
| No timestamps        | Timestamps included  |
| Difficult to monitor | Easily monitored     |

---

# Logging Architecture

```text
Application

↓

Logger

↓

Handler

↓

Formatter

↓

Console / File / Cloud
```

Every log message passes through this pipeline.

---

# 2. Python Logging Module

Python provides a built-in module:

```python
import logging
```

Basic configuration:

```python
import logging

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)
```

`__name__` creates a logger specific to the current module.

---

# Logger Flow

```text
Application

↓

logger.info()

↓

Logger

↓

Handler

↓

Output
```

---

# 3. Log Levels

Python defines five commonly used log levels.

---

## DEBUG

Very detailed technical information.

Useful while developing.

Example:

```python
logger.debug("Executing SQL query")
```

---

## INFO

Normal application events.

Example:

```python
logger.info("Student created successfully")
```

---

## WARNING

Something unexpected happened but the application can continue.

Example:

```python
logger.warning("Email address not provided")
```

---

## ERROR

An operation failed.

Example:

```python
logger.error("Database connection failed")
```

---

## CRITICAL

A serious problem that may stop the application.

Example:

```python
logger.critical("Application startup failed")
```

---

# Log Level Hierarchy

```text
DEBUG

↓

INFO

↓

WARNING

↓

ERROR

↓

CRITICAL
```

Each higher level represents a more severe issue.

---

# 4. Formatting Log Messages

Example configuration:

```python
logging.basicConfig(

level=logging.INFO,

format="%(asctime)s - %(levelname)s - %(message)s"

)
```

Example output:

```text
2026-07-28 10:15:23 - INFO - Student created successfully
```

Useful formatting fields:

- `%(asctime)s`
- `%(levelname)s`
- `%(name)s`
- `%(message)s`

---

# 5. Logging to a File

Instead of printing only to the console:

```python
logging.basicConfig(

filename="logs/application.log",

level=logging.INFO

)
```

Now logs are saved permanently.

Project structure:

```text
project/

logs/

application.log
```

---

# Logging to Console + File

A production application often writes logs to both destinations.

```text
Application

↓

Logger

↓

Console

+

application.log
```

This makes debugging easier during development and after deployment.

---

# 6. Exception Logging

Never do this:

```python
except Exception:

    print("Something went wrong")
```

Instead:

```python
except Exception:

    logger.exception("Failed to create student")
```

`logger.exception()` automatically records:

- the message,
- the exception,
- the complete stack trace.

---

# Stack Trace

Example:

```text
Student Creation Failed

↓

ValueError

↓

student_service.py

↓

Line 42
```

The stack trace shows exactly where the failure occurred.

---

# 7. Real Debugging Workflow

Suppose Swagger returns:

```text
500 Internal Server Error
```

Professional debugging looks like this:

```text
Swagger

↓

500

↓

Terminal

↓

Application Logs

↓

Stack Trace

↓

Root Cause

↓

Fix

↓

Retest
```

Logs provide the information that HTTP status codes cannot.

---

# 8. Logging in Clean Architecture

```text
Router

↓

logger.info()

↓

Service

↓

logger.debug()

↓

Repository

↓

logger.error()
```

Each layer logs events relevant to its responsibility.

Examples:

Router:

- Incoming requests

Service:

- Business decisions

Repository:

- Database failures

---

# 9. What Should We Log?

Good candidates:

- Application startup
- Incoming requests
- Successful operations
- Validation failures
- Authentication attempts
- Database errors
- Unexpected exceptions
- Shutdown events

---

# What Should We NEVER Log?

Never log:

- Passwords
- JWT secrets
- API keys
- Credit card numbers
- Personal identification numbers
- Sensitive customer information

Logs often remain stored for months.

Treat them as sensitive data.

---

# 10. Logging Best Practices

✅ Use appropriate log levels.

✅ Log meaningful messages.

✅ Include timestamps.

✅ Keep log messages consistent.

✅ Never expose secrets.

✅ Log exceptions with stack traces.

✅ Prefer structured logging over random text.

---

# Common Beginner Mistakes

❌ Using `print()` everywhere.

❌ Logging passwords.

❌ Logging every variable unnecessarily.

❌ Writing vague messages such as:

```text
Error happened
```

Instead:

```text
Failed to insert student into PostgreSQL database.
```

---

# 11. Logging vs Debugging

Logging:

Records information continuously.

Debugging:

Uses that information to find the cause of a problem.

Relationship:

```text
Application

↓

Logs

↓

Developer

↓

Debugging

↓

Fix
```

Good logging makes debugging much faster.

---

# 12. FastAPI Integration

Instead of:

```python
print("Student created")
```

Use:

```python
logger.info("Student created")
```

Inside middleware:

```python
logger.info(

f"{request.method} {request.url.path}"

)
```

This automatically records every request.

---

# 13. ASP.NET Core Comparison

ASP.NET Core:

```csharp
private readonly ILogger<StudentService> _logger;
```

Logging:

```csharp
_logger.LogInformation("Student created");
```

Python:

```python
logger.info("Student created")
```

Different syntax.

Same engineering principle.

---

# 14. Professional Logging Strategy

```text
Application Starts

↓

INFO

↓

Incoming Request

↓

INFO

↓

Validation

↓

DEBUG

↓

Database Query

↓

DEBUG

↓

Success

↓

INFO

↓

Failure

↓

ERROR

↓

Application Shutdown

↓

INFO
```

This creates a complete history of application activity.

---

# Interview Questions

### Q1. Why is logging better than `print()`?

Logging provides timestamps, severity levels, permanent storage, filtering, and monitoring capabilities.

---

### Q2. What are the standard log levels?

DEBUG, INFO, WARNING, ERROR, and CRITICAL.

---

### Q3. When should `logger.exception()` be used?

Inside an `except` block when you want to record both the error message and the stack trace.

---

### Q4. What information should never be logged?

Passwords, secrets, API keys, JWT secrets, and other sensitive user data.

---

### Q5. Why are logs important in production?

Because developers usually cannot directly observe running applications, logs become the primary source of diagnostic information.

---

# Cheat Sheet

```text
Application

↓

Logger

↓

Handler

↓

Formatter

↓

Console / File
```

---

```python
import logging

logger = logging.getLogger(__name__)
```

---

```python
logger.debug()

logger.info()

logger.warning()

logger.error()

logger.critical()
```

---

```python
logger.exception(...)
```

↓

Automatically logs stack trace.

---

# 🏗 Why does this exist?

## What problem does it solve?

Applications running in production cannot be debugged by watching the terminal.

Logging creates a permanent record of important events so engineers can diagnose problems after they occur.

---

## Who depends on it?

```text
Application

↓

Logger

↓

Developers

↓

Operations Team

↓

Monitoring Systems
```

Everyone responsible for running and maintaining the application depends on reliable logs.

---

## Who should NOT depend on it?

Business logic.

Services and repositories should produce useful log messages, but they should never make business decisions based on log output.

Logging is an observability tool—not application logic.

---

## ASP.NET Core Equivalent

```csharp
ILogger<T>
```

---

## Python Equivalent

```python
logging.getLogger(__name__)
```

---

# Key Takeaways

- Logging records application activity for debugging and monitoring.
- `logging` is Python's built-in logging framework.
- Log levels indicate the severity of events.
- `logger.exception()` automatically records stack traces.
- Never log sensitive information.
- Good logging dramatically reduces debugging time in production.

---

# Revision Checklist

- [ ] Understand why logging is better than `print()`.
- [ ] Can configure Python logging.
- [ ] Know all five log levels.
- [ ] Can log to both console and file.
- [ ] Can use `logger.exception()`.
- [ ] Understand how logs assist debugging.
- [ ] Can explain logging architecture in an interview.
- [ ] Can compare Python logging with ASP.NET Core `ILogger`.

---

# Tomorrow's Preview

- FastAPI Global Exception Handling
- Custom Exception Classes
- Centralized Error Responses
- Exception Middleware
- Building Consistent API Error Formats
- Production Error Handling Strategies
