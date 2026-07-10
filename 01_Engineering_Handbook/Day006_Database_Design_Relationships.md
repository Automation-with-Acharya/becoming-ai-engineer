# Day 006 — Database Design & Relationships

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 10 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand what a relational database is.
- Design normalized database tables.
- Understand Primary Keys and Foreign Keys.
- Identify different table relationships.
- Design a simple database schema.
- Understand why good database design matters in real-world applications.

---

# 1. What is a Relational Database?

A **Relational Database** stores data in multiple related tables instead of keeping everything in a single large table.

Each table represents one type of information.

Example:

```text
Student Database

├── Students
├── Courses
├── Enrollments
├── Teachers
└── Departments
```

The tables are connected using relationships.

---

# Why Relational Databases?

Without relationships:

- Duplicate data
- Difficult maintenance
- Inconsistent information
- Poor scalability

With relationships:

- Organized data
- Less duplication
- Faster searching
- Better consistency
- Easier maintenance

---

# 2. Table

A **table** stores related information.

Example:

## Students

| student_id | name   | age | city        |
| ---------- | ------ | --- | ----------- |
| 1          | Mayank | 27  | Gandhinagar |
| 2          | Rahul  | 25  | Ahmedabad   |
| 3          | Priya  | 24  | Surat       |

Each table focuses on a single entity.

---

# 3. Row (Record)

A **row** represents one complete record.

Example:

```text
1 | Mayank | 27 | Gandhinagar
```

Each student is one row.

---

# 4. Column (Field)

A **column** represents one attribute.

Examples:

- student_id
- name
- age
- city

Every row contains values for these columns.

---

# 5. Primary Key

## Definition

A **Primary Key (PK)** uniquely identifies each record in a table.

Example:

```sql
student_id
```

Properties:

- Unique
- Cannot be NULL
- One Primary Key per table
- Used to identify records efficiently

Example:

| student_id | name   |
| ---------- | ------ |
| 1          | Mayank |
| 2          | Rahul  |

The `student_id` distinguishes one student from another.

---

# 6. Foreign Key

## Definition

A **Foreign Key (FK)** creates a relationship between two tables.

Example:

## Students

| student_id | name   |
| ---------- | ------ |
| 1          | Mayank |
| 2          | Rahul  |

## Enrollments

| enrollment_id | student_id | course_id |
| ------------- | ---------- | --------- |
| 1             | 1          | 101       |
| 2             | 2          | 102       |

Here,

```text
Enrollments.student_id
```

references

```text
Students.student_id
```

This relationship ensures that every enrollment belongs to a valid student.

---

# Why Foreign Keys?

They:

- Maintain data integrity.
- Prevent invalid references.
- Connect related tables.
- Reduce data duplication.

---

# 7. Relationships

Relational databases connect tables using relationships.

---

## One-to-One (1:1)

One record is related to exactly one record.

Example:

```text
Employee

↓

Employee ID Card
```

One employee has one ID card.

One ID card belongs to one employee.

---

## One-to-Many (1:N)

One record relates to many records.

Example:

```text
Teacher

↓

Many Students
```

One teacher teaches many students.

Each student belongs to one teacher (in this simplified model).

---

## Many-to-Many (N:N)

Many records relate to many other records.

Example:

```text
Students

↓

Enrollments

↓

Courses
```

A student can enroll in many courses.

A course can have many students.

This is implemented using a **junction table**.

---

# 8. Junction Table

Many-to-Many relationships require a third table.

Example:

## Students

| student_id | name |
| ---------- | ---- |

---

## Courses

| course_id | course_name |
| --------- | ----------- |

---

## Enrollments

| enrollment_id | student_id | course_id |
| ------------- | ---------- | --------- |

The `Enrollments` table links students and courses.

---

# 9. Database Normalization

## Definition

Normalization is the process of organizing data to reduce redundancy and improve consistency.

---

## Why Normalize?

Without normalization:

```text
Student Table

Mayank

Python

SQL

Docker

Git
```

Course information gets repeated for every student.

This leads to:

- Duplicate data
- Update issues
- Storage waste

---

## First Normal Form (1NF)

Rules:

- One value per cell.
- No repeating groups.
- Each row should be unique.

Bad:

| Student | Courses             |
| ------- | ------------------- |
| Mayank  | Python, SQL, Docker |

Good:

| Student | Course |
| ------- | ------ |
| Mayank  | Python |
| Mayank  | SQL    |
| Mayank  | Docker |

---

# 10. Database Schema

Example:

```text
Students
---------
student_id (PK)
name
age
city

Courses
--------
course_id (PK)
course_name
duration

Enrollments
-----------
enrollment_id (PK)
student_id (FK)
course_id (FK)
```

This schema avoids duplication and supports future growth.

---

# SQL Example

## Students Table

```sql
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    city VARCHAR(100)
);
```

---

## Courses Table

```sql
CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100),
    duration INT
);
```

---

## Enrollments Table

```sql
CREATE TABLE enrollments (
    enrollment_id INT PRIMARY KEY,
    student_id INT,
    course_id INT,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
);
```

---

# Real-World Example

Imagine building an online learning platform.

Instead of storing everything in one table:

```text
Student

↓

Course

↓

Instructor

↓

Assignments

↓

Certificates
```

Each concept gets its own table.

Relationships connect them.

This is how enterprise applications scale.

---

# Best Practices

✅ One table = One responsibility.

✅ Use meaningful table names.

✅ Always define a Primary Key.

✅ Use Foreign Keys to maintain relationships.

✅ Avoid duplicate data.

✅ Normalize data before writing queries.

---

# Common Mistakes

❌ Storing multiple values in one column.

❌ Repeating the same information across many rows.

❌ Not defining a Primary Key.

❌ Ignoring relationships.

❌ Creating one massive table for everything.

---

# Interview Questions

### Q1. What is a relational database?

A database that stores data in multiple related tables connected using keys.

---

### Q2. Difference between Primary Key and Foreign Key?

Primary Key:

- Uniquely identifies a row.
- Exists in its own table.

Foreign Key:

- References the Primary Key of another table.
- Creates relationships between tables.

---

### Q3. Why do we normalize databases?

To reduce redundancy, improve consistency, and simplify maintenance.

---

### Q4. What is a One-to-Many relationship?

One record in one table relates to many records in another table.

Example:

One customer → Many orders.

---

### Q5. Why do Many-to-Many relationships require a junction table?

Because relational databases cannot directly store many-to-many relationships. A third table maps the relationship between the two entities.

---

# Backend Evolution

Our Student Management project has evolved like this:

```text
Day 003
students.txt

↓

Day 005
SQL Queries

↓

Day 006
Relational Database Design

↓

Day 007+
PostgreSQL

↓

Python + PostgreSQL

↓

REST API

↓

React Frontend

↓

Production Application
```

Every day's learning builds directly on the previous day's work.

---

# Cheat Sheet

```text
Primary Key (PK)
→ Uniquely identifies a row.

Foreign Key (FK)
→ Connects two tables.

1 : 1
→ One record ↔ One record.

1 : N
→ One record ↔ Many records.

N : N
→ Many records ↔ Many records
(using a junction table).

Normalization
→ Reduce duplication.
→ Improve consistency.
```

---

# Key Takeaways

- Relational databases organize information into related tables.
- Primary Keys uniquely identify records.
- Foreign Keys connect related tables.
- One-to-One, One-to-Many, and Many-to-Many relationships model real-world systems.
- Junction tables implement Many-to-Many relationships.
- Normalization reduces redundancy and improves data integrity.
- Good database design makes applications easier to scale, maintain, and extend.

---

# Revision Checklist

- [ ] Can explain what a relational database is.
- [ ] Understand tables, rows, and columns.
- [ ] Know the purpose of Primary Keys.
- [ ] Know the purpose of Foreign Keys.
- [ ] Can identify relationship types.
- [ ] Understand why junction tables are needed.
- [ ] Can explain First Normal Form (1NF).
- [ ] Can design a simple relational database schema.

---

# Tomorrow's Preview

- Installing PostgreSQL
- Creating databases in PostgreSQL
- Executing SQL queries in PostgreSQL
- Connecting Python to PostgreSQL using `psycopg`
- Migrating the Student Management project from text files to a real relational database
