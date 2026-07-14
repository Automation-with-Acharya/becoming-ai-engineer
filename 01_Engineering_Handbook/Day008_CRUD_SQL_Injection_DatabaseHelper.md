# Day 008 — CRUD Operations, SQL Injection & Database Helper

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 12 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Perform CRUD operations from Python.
- Understand SQL Injection attacks.
- Prevent SQL Injection using parameterized queries.
- Understand why string concatenation is dangerous for SQL.
- Build a reusable Database Helper class.
- Write cleaner, reusable database code.

---

# 1. What is CRUD?

CRUD represents the four basic operations performed on persistent data.

| Operation | SQL Command | Purpose                 |
| --------- | ----------- | ----------------------- |
| Create    | INSERT      | Add new records         |
| Read      | SELECT      | Retrieve records        |
| Update    | UPDATE      | Modify existing records |
| Delete    | DELETE      | Remove records          |

Almost every backend application is built around these four operations.

---

# CRUD Flow

```text
Application

↓

Create

Read

Update

Delete

↓

Database
```

---

# 2. CREATE Operation

Adding a new record.

```python
cur.execute(
    """
    INSERT INTO students(name, age, city)
    VALUES (%s, %s, %s)
    """,
    ("Mayank", 27, "Gandhinagar")
)

conn.commit()
```

---

# 3. READ Operation

Retrieve records.

```python
cur.execute(
    "SELECT * FROM students"
)

students = cur.fetchall()

for student in students:
    print(student)
```

---

# Reading a Single Record

```python
cur.execute(
    """
    SELECT *
    FROM students
    WHERE student_id = %s
    """,
    (1,)
)

student = cur.fetchone()

print(student)
```

---

# 4. UPDATE Operation

Modify an existing record.

```python
cur.execute(
    """
    UPDATE students
    SET city = %s
    WHERE student_id = %s
    """,
    ("Ahmedabad", 1)
)

conn.commit()
```

---

# 5. DELETE Operation

Remove data.

```python
cur.execute(
    """
    DELETE
    FROM students
    WHERE student_id = %s
    """,
    (1,)
)

conn.commit()
```

---

# 6. Why commit()?

PostgreSQL uses transactions.

Changes remain temporary until committed.

```python
conn.commit()
```

Without this:

- INSERT disappears
- UPDATE disappears
- DELETE disappears

when the connection closes.

---

# 7. SQL Injection

## Definition

SQL Injection is a security vulnerability where malicious SQL is inserted into an application's query through user input.

Instead of executing only the intended query, the database may execute unintended or harmful SQL.

---

# Unsafe Example

Imagine:

```python
username = input("Username: ")

query = (
    "SELECT * FROM users "
    f"WHERE username = '{username}'"
)

cur.execute(query)
```

If the user enters:

```text
' OR 1=1 --
```

The query becomes:

```sql
SELECT *
FROM users
WHERE username = '' OR 1=1 --'
```

`1=1` is always true.

The attacker now retrieves all rows.

---

# Why String Concatenation is Dangerous

Never do this:

```python
query = (
    "SELECT * FROM students WHERE name = '"
    + name +
    "'"
)
```

or

```python
query = f"""
SELECT *
FROM students
WHERE name = '{name}'
"""
```

Even if the application works, it is vulnerable to SQL Injection.

---

# 8. Parameterized Queries

Parameterized queries separate:

- SQL logic
- User data

Python sends the values safely to PostgreSQL.

Example:

```python
cur.execute(
    """
    SELECT *
    FROM students
    WHERE student_id = %s
    """,
    (student_id,)
)
```

Notice:

```text
%s
```

is only a placeholder.

Never surround it with quotes.

---

# Multiple Parameters

```python
cur.execute(
    """
    INSERT INTO students
    (name, age, city)
    VALUES (%s, %s, %s)
    """,
    ("Rahul", 25, "Ahmedabad")
)
```

---

# Why Parameterized Queries are Safe

Instead of building SQL manually:

```text
Python

↓

Driver

↓

Database
```

The driver sends:

- SQL separately
- Values separately

The database never treats user input as executable SQL.

---

# 9. fetchone() vs fetchall()

## fetchone()

Returns one row.

```python
student = cur.fetchone()
```

Useful when searching by Primary Key.

---

## fetchall()

Returns every matching row.

```python
students = cur.fetchall()
```

Useful for reports and listings.

---

# 10. Database Helper

Imagine writing this in every file:

```python
connection = psycopg.connect(...)
cursor = connection.cursor()
```

Again.

Again.

Again.

That's duplication.

Instead:

Create one reusable helper.

---

# Database Helper Responsibilities

```text
DatabaseHelper

↓

Connect

Execute Query

Commit

Fetch

Close
```

Every other module simply calls these methods.

---

# Example Database Helper

```python
import psycopg


class DatabaseHelper:

    def __init__(self):
        self.connection = psycopg.connect(
            dbname="student_db",
            user="postgres",
            password="YOUR_PASSWORD",
            host="localhost",
            port="5432"
        )

    def fetch_all(self, query, params=None):
        with self.connection.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute(self, query, params=None):
        with self.connection.cursor() as cur:
            cur.execute(query, params)
            self.connection.commit()

    def close(self):
        self.connection.close()
```

---

# Benefits of a Database Helper

✅ Reusable

✅ Cleaner code

✅ Easier maintenance

✅ Centralized connection handling

✅ Easier testing

---

# Project Evolution

```text
Day 003

Student Manager

↓

students.txt

────────────────────────────

Day 007

Student Manager

↓

Python

↓

PostgreSQL

────────────────────────────

Day 008

Student Manager

↓

Database Helper

↓

PostgreSQL
```

The application is becoming modular.

---

# Best Practices

✅ Always use parameterized queries.

✅ Commit after modifying data.

✅ Close database connections.

✅ Avoid duplicate connection code.

✅ Keep SQL readable.

✅ Separate business logic from database logic.

---

# Common Mistakes

❌ Building SQL using string concatenation.

❌ Forgetting `commit()`.

❌ Leaving connections open.

❌ Writing duplicate database code in multiple files.

❌ Hardcoding passwords in production applications.

---

# Interview Questions

### Q1. What is CRUD?

CRUD stands for Create, Read, Update, and Delete—the four fundamental operations performed on persistent data.

---

### Q2. What is SQL Injection?

A security vulnerability where malicious SQL is injected through user input, causing unintended queries to execute.

---

### Q3. How do parameterized queries prevent SQL Injection?

They separate SQL commands from user input. The database driver sends parameter values safely instead of treating them as executable SQL.

---

### Q4. Why is `commit()` necessary?

`INSERT`, `UPDATE`, and `DELETE` changes remain inside the current transaction until committed. `commit()` permanently saves those changes.

---

### Q5. What is the purpose of a Database Helper class?

It centralizes database connection and query logic, reduces duplication, improves maintainability, and makes the application easier to extend.

---

### Q6. Difference between `fetchone()` and `fetchall()`?

| fetchone()                     | fetchall()                 |
| ------------------------------ | -------------------------- |
| Returns one row                | Returns all matching rows  |
| Used for single-record lookups | Used for lists and reports |

---

# Cheat Sheet

```text
CRUD

Create  → INSERT

Read    → SELECT

Update  → UPDATE

Delete  → DELETE
```

---

```python
cur.execute(
    query,
    params
)
```

Always use parameters.

Never concatenate SQL strings.

---

```python
conn.commit()
```

Save changes.

---

```python
student = cur.fetchone()

students = cur.fetchall()
```

---

# Key Takeaways

- CRUD operations form the foundation of every backend application.
- SQL Injection is one of the most common database security vulnerabilities and must be prevented by using parameterized queries.
- Never build SQL statements through string concatenation or f-strings when including user input.
- `fetchone()` and `fetchall()` serve different retrieval scenarios.
- `commit()` is required to permanently save database modifications.
- A Database Helper class reduces duplication and creates a cleaner architecture by centralizing database access.

---

# Revision Checklist

- [ ] Can explain CRUD operations.
- [ ] Can write INSERT, SELECT, UPDATE, and DELETE queries from Python.
- [ ] Understand why `commit()` is required.
- [ ] Can explain SQL Injection with an example.
- [ ] Know why parameterized queries are safer than string concatenation.
- [ ] Can distinguish between `fetchone()` and `fetchall()`.
- [ ] Understand the purpose of a Database Helper class.
- [ ] Can explain the architecture of the Student Management application after introducing the helper layer.

---

# Tomorrow's Preview

- Repository Pattern
- Data Access Layer (DAL)
- Service Layer
- Clean Architecture Fundamentals
- Refactoring the Student Management project into a production-style backend structure
