# Day 020 — Database Transactions, ACID Properties & Transaction Management

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 01 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand what a database transaction is.
- Explain the ACID properties.
- Differentiate between `COMMIT` and `ROLLBACK`.
- Understand transaction boundaries.
- Use transactions correctly with PostgreSQL and Psycopg.
- Understand why transactions are critical in enterprise applications.
- Explain how transactions fit into Clean Architecture.
- Compare transaction management in FastAPI and ASP.NET Core.

---

# Big Picture

Yesterday our backend looked like this:

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

Today we strengthen the **database layer**.

```text
Client

↓

Router

↓

Service

↓

Repository

↓

BEGIN Transaction

↓

Database Operations

↓

Success?

↓

YES ─────► COMMIT

NO ──────► ROLLBACK
```

Transactions guarantee that related database operations behave as a single unit.

---

# 1. What is a Database Transaction?

A transaction is a sequence of one or more database operations that are treated as **one logical unit of work**.

A transaction guarantees:

- All operations succeed together.
- Or none of them are saved.

There is no partial success.

---

# Why Do Transactions Exist?

Imagine these operations:

1. Create Student
2. Create Enrollment
3. Generate Student Fee Record

If the third operation fails:

Without transactions:

```text
Student Created

Enrollment Created

Fee Record Failed
```

Database becomes inconsistent.

With transactions:

```text
BEGIN

↓

Create Student

↓

Create Enrollment

↓

Create Fee Record

↓

Failure

↓

ROLLBACK
```

Everything returns to its original state.

---

# Banking Example

Suppose Rahul transfers ₹10,000 to Priya.

Process:

```text
Withdraw ₹10,000

↓

Deposit ₹10,000
```

If the server crashes after withdrawal:

Without transactions:

```text
Rahul loses ₹10,000

Priya receives nothing
```

Money disappears.

With transactions:

```text
BEGIN

↓

Withdraw

↓

Deposit

↓

COMMIT
```

If any step fails:

```text
ROLLBACK
```

Both accounts remain unchanged.

This is why every banking application relies heavily on transactions.

---

# 2. Transaction Lifecycle

```text
BEGIN

↓

SQL Operation

↓

SQL Operation

↓

SQL Operation

↓

COMMIT

or

ROLLBACK
```

Only after `COMMIT` are the changes permanently stored.

---

# SQL Transaction Example

```sql
BEGIN;

INSERT INTO students(name)
VALUES ('Mayank');

UPDATE students
SET city='Ahmedabad'
WHERE student_id=1;

COMMIT;
```

If an error occurs:

```sql
ROLLBACK;
```

---

# 3. Commit

`COMMIT` permanently saves every successful operation performed inside the transaction.

Example:

```python
connection.commit()
```

After commit:

- Data becomes permanent.
- Other users can see the changes.
- The transaction ends.

---

# 4. Rollback

`ROLLBACK` cancels every operation performed during the current transaction.

Example:

```python
connection.rollback()
```

Rollback returns the database to its previous consistent state.

---

# Commit vs Rollback

| Commit                      | Rollback                           |
| --------------------------- | ---------------------------------- |
| Saves changes permanently   | Cancels all pending changes        |
| Ends successful transaction | Ends failed transaction            |
| Data becomes visible        | Database returns to previous state |

---

# 5. ACID Properties

Every relational database transaction follows the ACID principles.

---

## A — Atomicity

Atomicity means:

> **All operations succeed or none succeed.**

```text
Transaction

↓

100%

or

0%
```

Never 50%.

---

## C — Consistency

The database must always remain valid.

Example:

A foreign key relationship must never become invalid because of a partially completed transaction.

---

## I — Isolation

Multiple users can execute transactions simultaneously without corrupting each other's work.

Example:

Two users editing different students should not interfere with one another.

---

## D — Durability

Once a transaction is committed:

- data survives crashes,
- server restarts,
- power failures.

Commit means permanent.

---

# ACID Diagram

```text
Transaction

↓

Atomicity

↓

Consistency

↓

Isolation

↓

Durability
```

---

# 6. Psycopg Transaction Flow

Typical flow:

```python
connection = psycopg.connect(...)

cursor = connection.cursor()

cursor.execute(...)

cursor.execute(...)

connection.commit()

cursor.close()

connection.close()
```

If an exception occurs:

```python
connection.rollback()
```

---

# Transaction Flow in Python

```text
Connect

↓

Execute SQL

↓

Execute SQL

↓

Exception?

↓

NO

↓

Commit

↓

Close

──────────────

YES

↓

Rollback

↓

Close
```

---

# 7. Autocommit

Normally:

Psycopg starts a transaction automatically.

Nothing is permanently saved until:

```python
connection.commit()
```

If:

```python
connection.autocommit = True
```

Every SQL statement becomes permanent immediately.

This is usually **not recommended** for business operations involving multiple related changes.

---

# 8. Clean Architecture Responsibility

Where should transaction management live?

```text
Router

↓

Service

↓

Repository

↓

Database
```

Recommended responsibility:

- Router → HTTP requests
- Service → Business rules
- Repository → Database operations and transaction handling

The Service should not know **how** the database commits or rolls back changes.

---

# Architecture Diagram

```text
Client

↓

Router

↓

Service

↓

Repository

↓

BEGIN

↓

INSERT

↓

UPDATE

↓

DELETE

↓

Success?

↓

Commit

or

Rollback

↓

Database
```

---

# 9. Logging + Transactions

Yesterday:

```text
Exception

↓

Logger

↓

Global Handler
```

Today:

```text
Exception

↓

Rollback

↓

Logger

↓

Global Exception Handler

↓

Client
```

Rollback protects the database.

Logging helps developers investigate the failure.

---

# 10. Transaction Boundaries

A transaction should contain **one complete business operation**.

Good example:

```text
Create Student

+

Create Enrollment

+

Create Fee Record
```

Bad example:

Keeping a transaction open while waiting for user input or making slow external API calls.

Long-running transactions reduce database performance and increase locking.

---

# FastAPI vs ASP.NET Core

ASP.NET Core

```csharp
using var transaction =
await db.Database.BeginTransactionAsync();

...

await transaction.CommitAsync();
```

FastAPI / Psycopg

```python
connection.commit()

connection.rollback()
```

Different syntax.

Same architectural principle.

---

# Best Practices

✅ Keep transactions short.

✅ Commit only after every operation succeeds.

✅ Rollback immediately when an exception occurs.

✅ Log transaction failures.

✅ Group related database operations into one transaction.

---

# Common Beginner Mistakes

❌ Forgetting `commit()`.

❌ Calling `commit()` too early.

❌ Ignoring exceptions.

❌ Keeping transactions open for too long.

❌ Mixing unrelated business operations into one transaction.

❌ Using autocommit for multi-step business operations.

---

# Real-World Examples

Use transactions when:

- Bank transfer
- Student registration
- Order placement
- Invoice generation
- Inventory updates
- Payment processing

Avoid transactions for:

- Read-only queries
- Simple reporting
- Analytics dashboards

---

# Interview Questions

### Q1. What is a database transaction?

A transaction is a group of database operations treated as one logical unit that either succeeds completely or fails completely.

---

### Q2. Why are transactions important?

They prevent inconsistent data by ensuring related operations are committed together or rolled back together.

---

### Q3. What is the difference between `COMMIT` and `ROLLBACK`?

`COMMIT` permanently saves changes, while `ROLLBACK` discards all pending changes in the current transaction.

---

### Q4. What does Atomicity mean?

Atomicity guarantees that all operations inside a transaction succeed together or none are applied.

---

### Q5. Where should transaction management be handled in Clean Architecture?

Transaction handling belongs close to the database layer (Repository or Unit of Work), while the Service layer focuses on business rules.

---

### Q6. Why should transactions be kept short?

Long-running transactions hold locks longer, reduce concurrency, and negatively impact database performance.

---

# Cheat Sheet

```text
BEGIN

↓

SQL

↓

SQL

↓

SQL

↓

COMMIT

or

ROLLBACK
```

---

```python
try:

    cursor.execute(...)

    cursor.execute(...)

    connection.commit()

except Exception:

    connection.rollback()
```

---

# 🏗 Why does this exist?

## What problem does it solve?

Without transactions:

- partial updates occur,
- data becomes inconsistent,
- failures leave the database in an invalid state.

Transactions ensure the database always remains consistent.

---

## Who depends on it?

```text
Router

↓

Service

↓

Repository

↓

Database
```

Every write operation depends on transactions to maintain data integrity.

---

## Who should NOT depend on it?

Business logic should not directly control database commits and rollbacks.

The Service layer should express **what** needs to happen.

The Repository (or a future Unit of Work) should manage **how** those database changes are committed safely.

---

## ASP.NET Core Equivalent

```csharp
BeginTransaction()

CommitAsync()

RollbackAsync()
```

---

## FastAPI Equivalent

```python
connection.commit()

connection.rollback()
```

---

# Key Takeaways

- A transaction groups multiple database operations into one logical unit.
- ACID properties guarantee reliable and consistent database behavior.
- `COMMIT` permanently saves changes.
- `ROLLBACK` restores the database after failures.
- Transactions are essential for financial systems and any operation involving multiple related database changes.
- In Clean Architecture, transaction management belongs near the data access layer rather than the business layer.

---

# Revision Checklist

- [ ] Understand what a database transaction is.
- [ ] Can explain the four ACID properties.
- [ ] Know when to use `COMMIT`.
- [ ] Know when to use `ROLLBACK`.
- [ ] Understand transaction boundaries.
- [ ] Know where transaction handling belongs in Clean Architecture.
- [ ] Can compare FastAPI and ASP.NET Core transaction management.
- [ ] Can confidently explain transactions in an interview.

---

# 🏗 Engineering Evolution

Our Student Management backend has evolved significantly over the last few days:

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
        │
        ▼
Day 020
Database Transactions
```

Notice the pattern.

We are no longer adding business features.

We are strengthening the **reliability** of the backend.

This is exactly how enterprise software evolves—by improving security, observability, maintainability, configuration, and data integrity before adding more functionality.

---

# Tomorrow's Preview

- Database Connection Pooling
- Why Connection Pools Improve Performance
- Pool Size & Resource Management
- FastAPI Lifespan Events
- Building a Production-Ready Database Access Layer
