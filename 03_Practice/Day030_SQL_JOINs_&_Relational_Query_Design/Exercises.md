# Day 030: SQL JOINs & Relational Query Design — Exercises

## Exercise 1 — Inspect the Current Database Schema

First, inspect the current tables in your project.

You already have a **Student Management PostgreSQL database**.

### Tasks:

- Identify the `students` table
- Identify any relationship-bearing tables you currently have

### Important Note

If the current application schema doesn't yet contain a suitable relationship table, create a small practice schema for today's exercises rather than forcing unrelated application changes.

### Recommended Conceptual Model

```
students
  |
  | 1
  |
  | many
  v
enrollments
  |
  | many
  |
  | 1
  v
courses
```

---

## Exercise 2 — Build a JOIN Dataset

Create a small dataset as follows:

### Students Table

| ID  | Name   |
| --- | ------ |
| 1   | Rahul  |
| 2   | Priya  |
| 3   | Mayank |
| 4   | Amit   |

### Courses Table

| ID  | Name       |
| --- | ---------- |
| 101 | Python     |
| 102 | Docker     |
| 103 | PostgreSQL |

### Enrollments Table

| Student ID | Course ID |
| ---------- | --------- |
| 1          | 101       |
| 1          | 102       |
| 2          | 101       |
| 3          | 103       |

### Data Structure

```
Rahul
├── Python
└── Docker

Priya
└── Python

Mayank
└── PostgreSQL

Amit
└── (no courses)
```

This is the perfect JOIN playground.

---

## Exercise 3 — INNER JOIN

Write a query that returns:

- Student Name
- Course Name

### Expected Output

```
Rahul     Python
Rahul     Docker
Priya     Python
Mayank    PostgreSQL
```

---

## Exercise 4 — LEFT JOIN

Now modify the previous query to use a **LEFT JOIN** instead of INNER JOIN.

### Expected Output

```
Rahul     Python
Rahul     Docker
Priya     Python
Mayank    PostgreSQL
Amit      NULL
```

### Important Question

**Why did Amit appear this time?**

Because `LEFT JOIN` preserves every row from the left table, even if there are no matching rows in the right table.

---

## Exercise 5 — Find Students With No Courses

Now combine these SQL concepts:

- `LEFT JOIN`
- `IS NULL` condition

### Conceptual Query

```sql
WHERE e.student_id IS NULL
```

### Expected Result

```
Amit
```

### Real-World Use Cases

This is a **very common real-world SQL pattern**. Examples:

- Customers with no orders
- Employees with no manager assignment
- Users with no subscriptions
- Products with no sales

---

## Exercise 6 — Count Enrollments Per Student

Now combine these SQL concepts:

- `JOIN`
- `GROUP BY`
- `COUNT(*)`

### Query Goal

Find: **Student Name | Course Count**

### Expected Output

```
Rahul     2
Priya     1
Mayank    1
Amit      0
```

### Why This Matters

This exercise is especially important because **you're no longer simply retrieving rows**. You're **deriving information from relationships**.

---

## Exercise 7 — HAVING Clause

Now answer this question:

**Which students are enrolled in more than one course?**

### SQL Concepts to Use

- `GROUP BY`
- `COUNT(*)`
- `HAVING` clause

### Conceptual Query

```sql
HAVING COUNT(*) > 1
```

### Expected Result

```
Rahul
```

---

## Exercise 8 — Multi-Table JOIN

Now join **all three tables together**:

```
students
  ↓
enrollments
  ↓
courses
```

### Query Goal

Produce:

- Student Name
- Course Name

### Query Structure

```sql
SELECT
  s.name,
  c.name
FROM students s
JOIN enrollments e
  ON s.student_id = e.student_id
JOIN courses c
  ON e.course_id = c.course_id;
```

### Understanding Over Memorization

**Don't memorize this exact query.** Instead, understand the chain:

```
students
  ↓
enrollments
  ↓
courses
```

Each JOIN connects one table to the next through a foreign key relationship.

---

## Exercise 9 — Repository Connection

This is where today's SQL learning **reconnects to the architecture** we've spent so much time building.

### Current Architecture

```
Router
  ↓
Service
  ↓
Repository
  ↓
Database
```

### Today's Goal

Your **Repository should conceptually be able to expose something like:**

```python
get_students_with_courses()
```

Instead of exposing SQL directly to the Service layer.

### Desired Architecture

```
Service
  ↓
student_repository.get_students_with_courses()
  ↓
JOIN query (hidden in repository)
  ↓
PostgreSQL
```

### Why This Matters

This is **exactly why the Repository Pattern exists**.

- It **hides database-query mechanics** from the business layer
- Your Day 9 handbook explicitly established the Repository as the layer that **hides SQL from the application**
- The Service doesn't need to know about JOINs, GROUP BY, or other SQL details
- The Repository handles all that complexity internally
