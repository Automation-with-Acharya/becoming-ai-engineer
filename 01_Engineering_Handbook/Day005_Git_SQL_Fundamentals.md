# Day 005 — Git & SQL Fundamentals

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 09 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand the purpose of Git and Version Control.
- Understand the Git workflow.
- Use the most common Git commands confidently.
- Understand what a database is.
- Understand tables, rows, columns, and primary keys.
- Write basic SQL queries.
- Perform CRUD (Create, Read, Update, Delete) operations.
- Understand why databases replace text files in real-world applications.

---

# Part 1 — Git Fundamentals

# What is Git?

Git is a **Distributed Version Control System (DVCS)** used to track changes in source code.

It allows developers to:

- Track every change.
- Collaborate with teams.
- Restore previous versions.
- Work on multiple features independently.
- Maintain a complete project history.

---

# Why Git?

Without Git:

- No history of changes.
- Difficult collaboration.
- Easy to lose work.
- No rollback mechanism.

With Git:

- Safe version tracking.
- Team collaboration.
- Easy rollback.
- Professional development workflow.

---

# Git Workflow

```text
Working Directory
        │
    git add
        │
Staging Area
        │
   git commit
        │
 Local Repository
        │
    git push
        │
GitHub Repository
```

---

# Common Git Commands

## Check Repository Status

```bash
git status
```

Displays:

- Modified files
- New files
- Deleted files
- Staged files

---

## Stage All Files

```bash
git add .
```

Stages every modified file.

---

## Stage a Single File

```bash
git add filename.py
```

Example:

```bash
git add day05.sql
```

---

## Commit Changes

```bash
git commit -m "Meaningful commit message"
```

Creates a permanent snapshot of staged changes.

---

## View Commit History

```bash
git log
```

Short version:

```bash
git log --oneline
```

---

## Compare Changes

```bash
git diff
```

Shows changes before staging.

---

## Restore Changes

```bash
git restore filename.py
```

Discards local changes that haven't been committed.

---

## View Branches

```bash
git branch
```

Lists all local branches.

---

## Push to GitHub

```bash
git push
```

Uploads commits to the remote repository.

---

## Pull Latest Changes

```bash
git pull
```

Downloads and merges changes from the remote repository.

---

# Git Best Practices

✅ Commit frequently.

✅ Write meaningful commit messages.

✅ Commit only working code.

✅ Pull before starting work (when collaborating).

✅ Push regularly to keep GitHub updated.

---

# Part 2 — SQL Fundamentals

# What is SQL?

SQL (**Structured Query Language**) is the standard language used to communicate with relational databases.

It allows us to:

- Store data.
- Retrieve data.
- Update data.
- Delete data.

---

# What is a Database?

A **database** is an organized collection of related data.

Example:

```
Student Database
│
├── Students
├── Courses
├── Teachers
└── Attendance
```

---

# What is a Table?

A table stores related information using rows and columns.

Example:

| id  | name   | age | city        |
| --- | ------ | --- | ----------- |
| 1   | Mayank | 27  | Gandhinagar |
| 2   | Rahul  | 25  | Ahmedabad   |

---

# Row vs Column

### Row

Represents one complete record.

Example:

```
1 | Mayank | 27 | Gandhinagar
```

---

### Column

Represents one attribute.

Examples:

- id
- name
- age
- city

---

# Primary Key

A **Primary Key** uniquely identifies every row.

Properties:

- Unique
- Cannot be NULL
- One primary key per table

Example:

```
id
```

---

# CRUD Operations

| Operation | SQL Command |
| --------- | ----------- |
| Create    | INSERT      |
| Read      | SELECT      |
| Update    | UPDATE      |
| Delete    | DELETE      |

---

# Create Database

```sql
CREATE DATABASE student_db;
```

---

# Use Database

```sql
USE student_db;
```

---

# Create Table

```sql
CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    city VARCHAR(100)
);
```

---

# Insert Data

```sql
INSERT INTO students
VALUES
(1,'Mayank',27,'Gandhinagar'),
(2,'Rahul',25,'Ahmedabad'),
(3,'Priya',24,'Surat');
```

---

# Retrieve Data

Retrieve everything.

```sql
SELECT * FROM students;
```

Retrieve selected columns.

```sql
SELECT name, city
FROM students;
```

---

# Filter Data

```sql
SELECT *
FROM students
WHERE age > 25;
```

---

# Update Data

```sql
UPDATE students
SET city='Ahmedabad'
WHERE id=1;
```

---

# Delete Data

```sql
DELETE FROM students
WHERE id=3;
```

---

# Sort Data

Ascending

```sql
SELECT *
FROM students
ORDER BY age;
```

Descending

```sql
SELECT *
FROM students
ORDER BY age DESC;
```

---

# Aggregate Functions

Count

```sql
SELECT COUNT(*)
FROM students;
```

Maximum

```sql
SELECT MAX(age)
FROM students;
```

Minimum

```sql
SELECT MIN(age)
FROM students;
```

Average

```sql
SELECT AVG(age)
FROM students;
```

Distinct

```sql
SELECT DISTINCT city
FROM students;
```

---

# Why Databases Instead of Text Files?

Text Files

- No relationships
- Slow searching
- No constraints
- Manual management

Databases

- Fast querying
- Data integrity
- Relationships
- Security
- Scalability

---

# Git + SQL in Real Projects

Imagine the Student Management CLI you've built.

Current Version:

```
Student Manager

↓

students.txt
```

Future Version:

```
Student Manager

↓

PostgreSQL Database

↓

REST API

↓

React Frontend
```

This is exactly how we'll evolve the project over the coming weeks.

---

# Interview Questions

### Q1. What is Git?

A distributed version control system used to track changes in source code.

---

### Q2. Difference between Git and GitHub?

- **Git** → Version control tool installed locally.
- **GitHub** → Cloud platform that hosts Git repositories.

---

### Q3. What is SQL?

A language used to create, manage, retrieve, update, and delete data in relational databases.

---

### Q4. Difference between a Database and a Table?

- Database → Collection of related tables.
- Table → Collection of rows and columns.

---

### Q5. What is a Primary Key?

A unique identifier for each row in a table. It cannot contain duplicate or `NULL` values.

---

### Q6. Difference between `DELETE` and `DROP`?

- `DELETE` removes rows but keeps the table structure.
- `DROP` removes the entire table, including its structure and data.

---

### Q7. Difference between `WHERE` and `ORDER BY`?

- `WHERE` filters records.
- `ORDER BY` sorts records.

---

# Best Practices

### Git

- Commit frequently.
- Use meaningful commit messages.
- Keep commits focused on a single change.
- Push regularly.

### SQL

- Always use a Primary Key.
- Use `WHERE` with `UPDATE` and `DELETE`.
- Keep table names meaningful.
- Write readable queries with proper formatting.

---

# Cheat Sheet

## Git

```bash
git status
git add .
git commit -m "message"
git log
git diff
git restore file.py
git branch
git push
git pull
```

---

## SQL

```sql
CREATE DATABASE

CREATE TABLE

INSERT INTO

SELECT

UPDATE

DELETE

WHERE

ORDER BY

COUNT()

MAX()

MIN()

AVG()
```

---

# Key Takeaways

- Git tracks project history and enables safe collaboration.
- The Git workflow consists of Working Directory → Staging Area → Repository → Remote Repository.
- SQL is the standard language for interacting with relational databases.
- Tables organize data into rows and columns.
- Primary Keys uniquely identify records.
- CRUD operations form the foundation of database interactions.
- Databases provide scalability, integrity, and performance beyond simple text files.
- Git and SQL are essential skills for every backend and AI engineer.

---

# Revision Checklist

- [ ] Can explain Git and Version Control.
- [ ] Understand the Git workflow.
- [ ] Can use the 10 essential Git commands.
- [ ] Know what a database and table are.
- [ ] Understand rows, columns, and primary keys.
- [ ] Can write basic CRUD queries.
- [ ] Can explain why databases are preferred over text files.
- [ ] Confidently answer Git and SQL interview questions.

---

# Tomorrow's Preview

- Installing PostgreSQL
- Connecting Python to PostgreSQL
- Executing SQL from Python
- Refactoring the Student Management project to use a real database
- Introduction to REST APIs and Backend Architecture
