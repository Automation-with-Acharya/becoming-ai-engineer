# Day 019 — Application Configuration, Environment Variables & Pydantic Settings

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 30 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand why application configuration should be separated from source code.
- Understand Environment Variables and `.env` files.
- Configure applications using **Pydantic Settings**.
- Build a centralized configuration system.
- Remove hardcoded secrets from applications.
- Configure different environments (Development, Testing, Production).
- Understand how configuration integrates with Clean Architecture.
- Compare FastAPI configuration with ASP.NET Core.

---

# Big Picture

Yesterday our backend looked like this:

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

Global Exception Handler
```

Today we introduce centralized configuration.

```text
                    .env
                      │
                      ▼
              Configuration
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Database        JWT Auth      Logging
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                 Entire Application
```

Instead of hardcoding values, the application now reads them from one centralized source.

---

# 1. What is Application Configuration?

Application configuration is the collection of values that control how an application behaves.

Examples:

- Database URL
- JWT Secret Key
- Token Expiration Time
- Debug Mode
- Log Level
- API Keys
- Application Name

These values usually change between environments but **the application code should not**.

---

# Why Not Hardcode Values?

Bad example:

```python
DATABASE_URL = "postgresql://postgres:password@localhost/student_db"

SECRET_KEY = "my-secret-key"

DEBUG = True
```

Problems:

- Passwords become visible.
- Every environment requires editing source code.
- Secrets may accidentally be committed to GitHub.
- Difficult to maintain.

---

# Professional Approach

Instead:

```text
.env

↓

config.py

↓

Settings()

↓

Application
```

The code remains unchanged,

Only configuration changes.

---

# 2. Environment Variables

Environment variables are values stored **outside** the application.

Example:

```text
DATABASE_URL

SECRET_KEY

LOG_LEVEL

DEBUG
```

The operating system provides these values to the application at runtime.

---

# Why Environment Variables?

Benefits:

- No hardcoded secrets.
- Different values for different environments.
- Easy deployment.
- Better security.
- Industry standard.

---

# 3. The `.env` File

During development, environment variables are commonly stored inside a file named:

```text
.env
```

Example:

```env
APP_NAME=Student Management API

DATABASE_URL=postgresql://postgres:password@localhost/student_db

SECRET_KEY=my_super_secret_key

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

DEBUG=True

LOG_LEVEL=INFO
```

This file is loaded automatically by Pydantic Settings.

---

# Should `.env` be Committed?

No.

Always add:

```text
.env
```

to:

```text
.gitignore
```

Reason:

It often contains:

- passwords
- API keys
- JWT secrets
- database credentials

Never expose them publicly.

---

# 4. Pydantic Settings

FastAPI commonly uses the `pydantic-settings` package.

Install:

```bash
pip install pydantic-settings
```

Example:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    app_name: str
    database_url: str
    secret_key: str
    debug: bool

    class Config:
        env_file = ".env"

settings = Settings()
```

The `Settings` object automatically reads values from `.env`.

---

# Configuration Flow

```text
.env

↓

BaseSettings

↓

Settings Object

↓

Entire Application
```

---

# 5. Centralized Configuration

Create:

```text
config.py
```

Instead of writing:

```python
SECRET_KEY = "abc123"
```

everywhere,

import:

```python
from app.config import settings
```

Then use:

```python
settings.secret_key
```

Every module reads from the same configuration source.

---

# Clean Architecture Placement

Recommended structure:

```text
student_management/

│

├── config.py

├── .env

├── main.py

├── database.py

├── auth/

├── middleware/

├── repositories/

├── services/

├── routers/
```

Configuration belongs to the application's infrastructure layer.

---

# 6. Development vs Production

Development:

```text
DEBUG=True

DATABASE_URL=localhost
```

Production:

```text
DEBUG=False

DATABASE_URL=prod-db.company.com
```

The code remains identical.

Only the configuration changes.

---

# Environment Architecture

```text
             Same Code

        ┌────────┴────────┐

        ▼                 ▼

Development         Production

        │                 │

   .env.dev          .env.prod

        │                 │

        ▼                 ▼

     Settings         Settings
```

One codebase.

Multiple environments.

---

# 7. Database Configuration

Instead of:

```python
psycopg.connect(
    host="localhost",
    user="postgres",
    password="password"
)
```

Use:

```python
psycopg.connect(
    settings.database_url
)
```

Changing databases now requires changing only `.env`.

---

# 8. JWT Configuration

Instead of:

```python
SECRET_KEY = "my_secret"
```

Use:

```python
settings.secret_key
```

Benefits:

- easier rotation
- safer deployment
- no source code changes

---

# 9. Logging Configuration

Instead of:

```python
logging.basicConfig(level=logging.INFO)
```

Use:

```python
logging.basicConfig(

level=settings.log_level
)
```

Now logging changes automatically between environments.

---

# Configuration Flow

```text
.env

↓

Settings

↓

Database

↓

Authentication

↓

Logging

↓

Application
```

Everything shares one configuration source.

---

# 10. Twelve-Factor App Principle

One of the most important software engineering principles states:

> **Store configuration in the environment, not in the code.**

Advantages:

- secure
- portable
- deployable
- cloud-friendly

Most modern cloud platforms follow this principle.

---

# 11. FastAPI vs ASP.NET Core

ASP.NET Core:

```text
appsettings.json

↓

IConfiguration

↓

Dependency Injection

↓

Controllers
```

FastAPI:

```text
.env

↓

Pydantic Settings

↓

Settings Object

↓

Routers / Services
```

Different implementation.

Same architectural idea.

---

# 12. Security Best Practices

Never hardcode:

- Database passwords
- JWT Secret Keys
- API Keys
- SMTP Passwords
- OAuth Client Secrets

Always load them from configuration.

---

# Common Beginner Mistakes

❌ Hardcoding passwords.

❌ Committing `.env` to GitHub.

❌ Duplicating configuration values across files.

❌ Reading environment variables manually in every module.

❌ Mixing business logic with configuration.

---

# Production Configuration Strategy

```text
.env

↓

config.py

↓

settings

↓

Application
```

Every component reads configuration from one location.

No duplication.

No inconsistency.

---

# Interview Questions

### Q1. Why shouldn't secrets be hardcoded?

Because they become difficult to change, insecure, and may be accidentally exposed through source control.

---

### Q2. What is the purpose of a `.env` file?

It stores environment-specific configuration values during development.

---

### Q3. Why use Pydantic Settings?

It automatically loads configuration from environment variables while providing validation and type safety.

---

### Q4. Why centralize configuration?

To avoid duplication, improve maintainability, and keep application behavior consistent across all modules.

---

### Q5. What changes between Development and Production?

Configuration values such as database URLs, debug flags, log levels, and secrets.

The application code should remain the same.

---

# Cheat Sheet

```text
.env

↓

Settings

↓

Database

JWT

Logging

↓

Application
```

---

```python
from app.config import settings
```

---

```python
settings.database_url

settings.secret_key

settings.debug

settings.log_level
```

---

# 🏗 Why does this exist?

## What problem does it solve?

Without centralized configuration:

- secrets are duplicated,
- deployments become difficult,
- changing environments requires editing source code.

Configuration management separates environment-specific values from application logic.

---

## Who depends on it?

```text
Application

↓

Settings

↓

Database

↓

Authentication

↓

Logging

↓

Developers

↓

DevOps
```

Everyone running or deploying the application depends on configuration.

---

## Who should NOT depend on it?

Business logic.

Services should consume configuration when necessary, but they should not know **how** configuration values are loaded.

---

## ASP.NET Core Equivalent

```csharp
IConfiguration

appsettings.json

IOptions<T>
```

---

## FastAPI Equivalent

```python
BaseSettings

Settings()

.env
```

---

# Key Takeaways

- Configuration should always be separated from application code.
- Environment variables are the industry-standard way to store configuration.
- `.env` files simplify local development.
- Pydantic Settings provides type-safe configuration management.
- Never commit secrets to GitHub.
- Centralized configuration improves maintainability, security, and deployment flexibility.

---

# Revision Checklist

- [ ] Understand why configuration is separated from code.
- [ ] Know what environment variables are.
- [ ] Can create and use a `.env` file.
- [ ] Can configure Pydantic Settings.
- [ ] Can remove hardcoded secrets.
- [ ] Understand Development vs Production configuration.
- [ ] Can compare FastAPI configuration with ASP.NET Core.
- [ ] Can explain configuration management in an interview.

---

# 🏗 Engineering Evolution

Let's look at how our Student Management project has evolved over the last several days:

```text
Day 015
JWT Authentication
        │
        ▼
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
```

Notice something important.

None of these features add a new business capability like "Add Student" or "Delete Student."

Instead, each one strengthens the **foundation** of the application.

A production backend isn't defined by how many endpoints it has—it's defined by how well it is structured, secured, configured, monitored, and maintained.

By Day 019, your Student Management project has evolved from a simple CRUD application into a backend that already contains many of the infrastructure components used in enterprise systems.

---

# Tomorrow's Preview

- Database Transactions
- Commit & Rollback
- ACID Properties
- Unit of Work Concept
- Transaction Management in FastAPI
- Building Reliable Multi-Step Database Operations
