# Day 007 — PostgreSQL & Python Integration

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 11 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand what PostgreSQL is.
- Install and configure PostgreSQL.
- Understand the role of pgAdmin.
- Create and connect to a PostgreSQL database.
- Execute SQL scripts in PostgreSQL.
- Connect Python applications to PostgreSQL using `psycopg`.
- Execute SQL queries from Python.
- Understand the architecture of a database-driven backend application.

---

# 1. What is PostgreSQL?

PostgreSQL (pronounced **Post-Gres-Q-L**) is an open-source **Relational Database Management System (RDBMS)**.

It stores, manages, secures, and retrieves structured data efficiently.

It is widely used in:

- Banking
- Healthcare
- E-commerce
- Government systems
- SaaS platforms
- AI platforms
- Enterprise software

---

# Why PostgreSQL?

Compared to simple text files:

- Faster querying
- Better performance
- Data integrity
- Relationships
- Security
- Transactions
- Scalability

This is why almost every backend application stores data in a database instead of files.

---

# SQL vs PostgreSQL

Many beginners confuse these two terms.

| SQL                   | PostgreSQL                                 |
| --------------------- | ------------------------------------------ |
| A language            | A database management system               |
| Used to write queries | Executes SQL queries                       |
| Standard language     | Software that stores and manages databases |

Think of it this way:

```text
SQL
↓

Language

↓

PostgreSQL

↓

Software that understands SQL
```

---

# PostgreSQL Architecture

```text
Python Application
        │
        ▼
   psycopg Driver
        │
        ▼
 PostgreSQL Server
        │
        ▼
 Database
        │
        ▼
 Tables
```

Python never talks directly to the database.

It communicates through a database driver.

---

# PostgreSQL Architecture Fundamentals

## Overview

PostgreSQL follows a classic client/server model. In this model, a client application connects to a PostgreSQL server, sends requests, and receives results.

A PostgreSQL session involves a set of cooperating processes that work together to manage database operations efficiently.

---

## 1. Client/Server Architecture

In PostgreSQL, the database server is the central component that:

- manages the database files,
- accepts incoming connections from client applications, and
- performs database actions on behalf of the clients.

The main server program is called `postgres`.

The client application is the frontend program that wants to interact with the database. It may be:

- a terminal-based tool,
- a graphical application,
- a web server,
- or a specialized database maintenance tool.

> The client and server may run on different machines, and they communicate over a TCP/IP network connection.

---

## 2. How PostgreSQL Handles Connections

PostgreSQL can manage multiple concurrent client connections at the same time.

To support this, the server:

1. starts a new process for each connection,
2. assigns that process to the connected client, and
3. allows the client and server process to communicate without involving the original supervisor process.

This means:

- the main PostgreSQL server process stays active and waits for new connections,
- while each client connection gets its own dedicated backend process.

---

## 3. PostgreSQL Client Applications

Client applications are software programs or scripts that connect to the PostgreSQL server to:

- execute SQL queries,
- run administrative commands, and
- retrieve data.

### Type A: Interactive Command-Line Tools

The most common example is `psql`.

**Key Use Case:**

- quick database management,
- running SQL scripts,
- viewing schemas with commands like `\d`, and
- performing system diagnostics from the terminal.

### Type B: Graphical User Interface Tools

Examples include:

- `pgAdmin`
- `DBeaver`
- VS Code PostgreSQL extensions

**Key Use Case:**

- visual database administration,
- interactive query tuning, and
- managing multiple server environments through a GUI.

### Type C: Programmatic Application Clients

These are drivers and ORMs used by applications written in different programming languages.

Common examples:

- Python: `psycopg` or `psycopg2`
- C# / .NET: `Npgsql`
- Node.js: `pg`
- Java: `JDBC`
- C: `libpq`

**Key Use Case:**

- enabling web applications, APIs, and other software systems to communicate with PostgreSQL.

---

## 4. How Client Communication Works

The communication flow between a client and PostgreSQL usually looks like this:

### Step 1: Connection Request

The client application connects to the PostgreSQL server using:

- the server host address (IP/domain), and
- the port number (default is `5432`).

### Step 2: Authentication

The client provides credentials such as:

- username and password, or
- identity tokens such as Azure AD / OAuth-based authentication.

### Step 3: Backend Process Spawning

Once the connection is accepted, PostgreSQL creates a dedicated backend process to handle requests for that client session.

### Step 4: Query Execution

The client sends SQL text to the server. PostgreSQL then:

- parses the query,
- optimizes it,
- executes it, and
- returns the result set to the client program.

---

## Summary

PostgreSQL uses a robust client/server architecture where:

- the server manages the database,
- clients connect and send SQL requests,
- each connection gets its own backend process, and
- communication happens through a structured request-response flow.

This architecture makes PostgreSQL suitable for both simple database tasks and large-scale multi-user applications.

---

# 2. Installing PostgreSQL

Install:

- PostgreSQL Server
- pgAdmin 4

During installation:

- Keep default port:

```text
5432
```

Create a password for:

```text
postgres
```

Remember this password because Python will use it later.

---

# 3. pgAdmin

pgAdmin is PostgreSQL's graphical management tool.

It allows you to:

- Create databases
- Create tables
- Execute SQL queries
- View data
- Manage schemas
- Backup and restore databases

Think of it as **Visual Studio Code for databases**.

---

# 4. Creating a Database

Example:

```sql
CREATE DATABASE student_db;
```

After creating the database:

- Connect to it using pgAdmin or `psql`.
- Create tables.
- Execute SQL scripts.

---

# 5. Running SQL Files

Instead of copying queries one by one:

Open:

```text
student_schema.sql
```

Execute the script.

The database automatically creates:

- Students
- Courses
- Enrollments

---

# 6. Basic SQL Execution

Retrieve all students.

```sql
SELECT *
FROM students;
```

Retrieve all courses.

```sql
SELECT *
FROM courses;
```

Retrieve all enrollments.

```sql
SELECT *
FROM enrollments;
```

You should see the records inserted from your SQL scripts.

---

# 7. Installing psycopg

Python communicates with PostgreSQL using the `psycopg` library.

Install:

```bash
pip install psycopg[binary]
```

Verify installation:

```bash
python -c "import psycopg; print(psycopg.__version__)"
```

---

# 8. Connecting Python to PostgreSQL

Basic connection:

```python
import psycopg

connection = psycopg.connect(
    dbname="student_db",
    user="postgres",
    password="YOUR_PASSWORD",
    host="localhost",
    port="5432"
)

print("Connected Successfully!")

connection.close()
```

---

# Connection Parameters

| Parameter | Description         |
| --------- | ------------------- |
| dbname    | Database name       |
| user      | PostgreSQL username |
| password  | PostgreSQL password |
| host      | Database server     |
| port      | PostgreSQL port     |

---

# 9. Creating a Cursor

A connection opens communication.

A cursor executes SQL.

```python
cursor = connection.cursor()
```

Think of it as a keyboard that types SQL into PostgreSQL.

---

# 10. Executing SQL from Python

Example:

```python
cursor.execute(
    "SELECT * FROM students;"
)
```

---

# Reading Results

```python
students = cursor.fetchall()

for student in students:
    print(student)
```

Expected output:

```text
(1, 'Mayank', 27, 'Gandhinagar')
(2, 'Rahul', 25, 'Ahmedabad')
(3, 'Priya', 24, 'Surat')
```

---

# Closing Resources

Always close resources.

```python
cursor.close()
connection.close()
```

This prevents resource leaks.

---

# Complete Example

```python
import psycopg

connection = psycopg.connect(
    dbname="student_db",
    user="postgres",
    password="YOUR_PASSWORD",
    host="localhost",
    port="5432"
)

cursor = connection.cursor()

cursor.execute(
    "SELECT * FROM students;"
)

students = cursor.fetchall()

for student in students:
    print(student)

cursor.close()
connection.close()
```

---

# Best Practices

✅ Close database connections.

✅ Close cursors.

✅ Store credentials securely (never hardcode passwords in production).

✅ Keep SQL queries readable.

✅ Use meaningful table names.

✅ Handle database exceptions using `try-except`.

---

# Common Mistakes

❌ Forgetting to close the connection.

❌ Wrong username or password.

❌ Wrong port number.

❌ Connecting to the wrong database.

❌ Forgetting to commit changes after `INSERT`, `UPDATE`, or `DELETE`.

Example:

```python
connection.commit()
```

---

# CRUD from Python

## Create

```python
cursor.execute(
    "INSERT INTO students VALUES (4,'Anjali',23,'Vadodara');"
)

connection.commit()
```

---

## Read

```python
cursor.execute(
    "SELECT * FROM students;"
)
```

---

## Update

```python
cursor.execute(
    "UPDATE students SET city='Ahmedabad' WHERE student_id=4;"
)

connection.commit()
```

---

## Delete

```python
cursor.execute(
    "DELETE FROM students WHERE student_id=4;"
)

connection.commit()
```

---

# Real-World Architecture

Our project has evolved like this:

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

psycopg

↓

PostgreSQL

↓

student_db

↓

students table
```

Next evolution:

```text
React Frontend

↓

FastAPI

↓

Python

↓

PostgreSQL
```

This is the same layered architecture used by many production backend systems.

---

# Interview Questions

### Q1. What is PostgreSQL?

An open-source relational database management system used to store and manage structured data.

---

### Q2. Difference between SQL and PostgreSQL?

SQL is the language.

PostgreSQL is the software that executes SQL and manages databases.

---

### Q3. Why do we need `psycopg`?

It acts as a bridge between Python and PostgreSQL.

---

### Q4. What is a cursor?

A cursor executes SQL commands and retrieves results from the database.

---

### Q5. Why is `commit()` required?

Changes made by `INSERT`, `UPDATE`, and `DELETE` remain pending until committed.

`commit()` permanently saves them.

---

### Q6. Why should database connections be closed?

Closing connections releases resources, prevents leaks, and allows other applications to use the database efficiently.

---

# Cheat Sheet

```text
PostgreSQL
↓

Database Server

↓

Database

↓

Tables

↓

Rows
```

```python
connection = psycopg.connect(...)

cursor = connection.cursor()

cursor.execute(...)

results = cursor.fetchall()

connection.commit()

cursor.close()

connection.close()
```

---

# Key Takeaways

- PostgreSQL is an enterprise-grade relational database management system.
- SQL is the language used to communicate with PostgreSQL.
- `psycopg` enables Python applications to connect to PostgreSQL.
- A connection establishes communication, while a cursor executes SQL.
- Always close cursors and connections after use.
- `commit()` is required to permanently save data changes.
- Database-driven applications are more scalable and maintainable than file-based applications.

---

# Revision Checklist

- [ ] Can explain the difference between SQL and PostgreSQL.
- [ ] Understand the role of pgAdmin.
- [ ] Can create and connect to a PostgreSQL database.
- [ ] Can execute SQL scripts.
- [ ] Can install and use `psycopg`.
- [ ] Can connect Python to PostgreSQL.
- [ ] Can execute SQL queries from Python.
- [ ] Know when to use `commit()`.
- [ ] Can confidently explain the database architecture in an interview.

---

# Tomorrow's Preview

- Parameterized SQL queries
- Preventing SQL Injection
- Building a reusable Database Helper class
- Migrating the Student Management application from file storage to PostgreSQL
- Writing production-quality database code in Python
