# Day 022 — Database Indexing & Query Performance

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 07 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand why database indexes exist.
- Explain how indexes improve query performance.
- Understand Sequential Scan vs Index Scan.
- Create indexes in PostgreSQL.
- Use `EXPLAIN` and `EXPLAIN ANALYZE`.
- Interpret PostgreSQL query execution plans.
- Understand when indexes help and when they hurt.
- Explain indexing confidently in interviews.

---

# Big Picture

Our backend has evolved steadily.

```text
Client

↓

FastAPI

↓

Router

↓

Service

↓

Repository

↓

Connection Pool

↓

PostgreSQL
```

Today we improve what happens **inside PostgreSQL**.

Instead of scanning the entire table every time, PostgreSQL can use an index to locate data much faster.

---

# 1. Why Do We Need Indexes?

Imagine a library containing one million books.

Without a catalog:

```text
Need Book

↓

Shelf 1

↓

Shelf 2

↓

Shelf 3

↓

...

↓

Found
```

Finding one book may take several minutes.

With a catalog:

```text
Need Book

↓

Search Catalog

↓

Shelf 482

↓

Found
```

The catalog does not contain the books.

It only tells you where they are.

A database index works exactly the same way.

---

# Database Without Index

Suppose we have:

```text
Students

1

2

3

4

5

...

100000
```

Query:

```sql
SELECT *
FROM students
WHERE email='mayank@gmail.com';
```

Without an index:

```text
Row 1

↓

Check

↓

Row 2

↓

Check

↓

Row 3

↓

Check

↓

...

↓

Row 100000
```

Every row must be examined.

This is called a **Sequential Scan**.

---

# Database With Index

```text
Index

↓

mayank@gmail.com

↓

Row 52381

↓

Students Table

↓

Return Row
```

Only the matching row is accessed.

---

# Visual Architecture

```text
                   Students Table

 ┌────────────────────────────────────────────┐

 │ id │ name │ email │ city │ age │

 └────────────────────────────────────────────┘

                ▲

                │

          B-Tree Index

                │

      mayank@gmail.com

                │

             Row 52381
```

---

# 2. What is an Index?

An index is a separate data structure maintained by the database.

It stores:

- Indexed column values
- References (pointers) to the corresponding rows

It does **not** duplicate the entire table.

Instead, it helps PostgreSQL find rows quickly.

---

# 3. How PostgreSQL Finds Data

Without Index:

```text
Request

↓

Sequential Scan

↓

Every Row

↓

Match Found
```

With Index:

```text
Request

↓

Index Lookup

↓

Row Pointer

↓

Retrieve Row
```

---

# 4. B-Tree Index

The default PostgreSQL index is a **B-Tree**.

Think of it as a sorted tree.

```text
                    M

             /              \

          F                  T

       /     \            /      \

     C         J        P          Z
```

Searching does **not** start from the beginning.

It repeatedly eliminates half of the remaining values.

This is much faster than checking every row.

---

# 5. Creating an Index

Example:

```sql
CREATE INDEX idx_students_email
ON students(email);
```

Now PostgreSQL can quickly search by email.

---

# Naming Convention

A common convention:

```text
idx_<table>_<column>
```

Examples:

```text
idx_students_email

idx_students_name

idx_orders_customer_id

idx_products_category
```

---

# 6. When Should We Create an Index?

Good candidates:

- Email
- Username
- Employee ID
- Order Number
- Foreign Keys
- Frequently searched columns

Example:

```sql
SELECT *

FROM students

WHERE email=...
```

Excellent candidate.

---

# Poor Candidates

Avoid indexing:

- Boolean columns

Example:

```text
is_active
```

Only two values exist.

The database gains little benefit.

---

Columns with very few distinct values.

Example:

```text
Gender

M

F
```

Again, not very selective.

---

Frequently updated columns may also be poor candidates because indexes must be updated whenever indexed values change.

---

# 7. Sequential Scan

Suppose:

```sql
SELECT *

FROM students

WHERE city='Ahmedabad';
```

No index.

Execution:

```text
Row 1

↓

Row 2

↓

Row 3

↓

...

↓

Row N
```

PostgreSQL examines every row.

---

# Index Scan

Now:

```sql
CREATE INDEX idx_city

ON students(city);
```

Execution:

```text
City Index

↓

Ahmedabad

↓

Matching Rows

↓

Done
```

Far fewer rows are examined.

---

# Scan Comparison

Sequential Scan

```text
Entire Table

↓

Every Row

↓

Slow for Large Tables
```

Index Scan

```text
Index

↓

Matching Pointer

↓

Row

↓

Fast
```

---

# 8. EXPLAIN

Sometimes we don't want to execute a query.

We only want to know how PostgreSQL **plans** to execute it.

```sql
EXPLAIN

SELECT *

FROM students

WHERE email='abc@example.com';
```

Possible output:

```text
Index Scan

Cost=0.15..8.17

Rows=1
```

---

# What EXPLAIN Shows

Execution strategy.

Examples:

- Sequential Scan
- Index Scan
- Bitmap Scan
- Join methods

Estimated:

- Cost
- Rows
- Width

---

# 9. EXPLAIN ANALYZE

Unlike `EXPLAIN`,

this actually runs the query.

```sql
EXPLAIN ANALYZE

SELECT *

FROM students

WHERE email='abc@example.com';
```

Output includes:

- Planning Time
- Execution Time
- Actual Rows
- Actual Scan Type

---

# Example Output

```text
Index Scan

Planning Time:

0.210 ms

Execution Time:

0.058 ms
```

Without index:

```text
Seq Scan

Planning Time:

0.220 ms

Execution Time:

45.128 ms
```

Notice the dramatic reduction in execution time.

---

# 10. Why Indexes Improve Performance

Without Index

```text
Need Row

↓

Read Entire Table

↓

Find Match
```

With Index

```text
Need Row

↓

Read Small Index

↓

Jump to Row
```

Much less data is read from disk.

---

# 11. The Cost of Indexes

Indexes are not free.

Whenever data changes:

```sql
INSERT

UPDATE

DELETE
```

PostgreSQL must also update the index.

Therefore:

Indexes improve **read performance** but slightly slow **write operations**.

---

# Read vs Write Trade-off

Without Index

```text
Reads

Slow

Writes

Fast
```

With Index

```text
Reads

Fast

Writes

Slightly Slower
```

Engineering is always about balancing trade-offs.

---

# 12. Multiple Indexes

One table may contain many indexes.

Example:

```text
Students

↓

Email Index

↓

Name Index

↓

City Index
```

PostgreSQL chooses the most suitable one automatically.

---

# 13. Composite Index

Sometimes queries search using multiple columns.

Example:

```sql
WHERE city='Ahmedabad'

AND age=27
```

Instead of two separate indexes:

```sql
CREATE INDEX idx_city_age

ON students(city, age);
```

This is called a **Composite Index**.

---

# 14. Primary Key Index

When creating:

```sql
PRIMARY KEY
```

PostgreSQL automatically creates an index.

Example:

```sql
student_id
```

No need to create another index on the same column.

---

# 15. Unique Index

When a column must remain unique:

```sql
CREATE UNIQUE INDEX
```

Example:

```text
Email

Username
```

Duplicates are not allowed.

---

# Real-World Architecture

Today's backend:

```text
Client

↓

FastAPI

↓

Router

↓

Service

↓

Repository

↓

Connection Pool

↓

PostgreSQL

↓

Indexes

↓

Data Pages
```

The application doesn't know whether PostgreSQL uses an index.

The database optimizer decides automatically.

---

# Query Optimization Workflow

Whenever a query feels slow:

```text
Query

↓

EXPLAIN

↓

Sequential Scan?

↓

Yes

↓

Should Index Exist?

↓

Create Index

↓

EXPLAIN ANALYZE

↓

Compare Performance
```

---

# Best Practices

✅ Create indexes on frequently searched columns.

✅ Index foreign keys.

✅ Use `EXPLAIN ANALYZE` before optimizing.

✅ Remove unused indexes.

✅ Monitor query performance in production.

---

# Common Beginner Mistakes

❌ Indexing every column.

❌ Creating duplicate indexes.

❌ Forgetting that indexes slow writes.

❌ Assuming PostgreSQL always uses an index.

❌ Optimizing without measuring.

---

# Real-World Examples

Indexes are commonly created on:

Banking

- Account Number
- Customer ID
- Transaction ID

E-commerce

- Product ID
- Category
- SKU

Healthcare

- Patient ID
- Doctor ID

Authentication

- Email
- Username

---

# Interview Questions

### Q1. What is a database index?

A database index is a separate data structure that stores indexed column values along with references to table rows, allowing PostgreSQL to locate data efficiently without scanning the entire table.

---

### Q2. Why are indexes faster?

Because PostgreSQL searches a much smaller sorted structure instead of reading every row in the table.

---

### Q3. What is a Sequential Scan?

A Sequential Scan examines every row in a table until it finds matching records.

---

### Q4. What is an Index Scan?

An Index Scan uses an index to locate matching rows directly, reducing the amount of data that must be read.

---

### Q5. What is `EXPLAIN`?

`EXPLAIN` shows PostgreSQL's execution plan without executing the query.

---

### Q6. What is `EXPLAIN ANALYZE`?

It executes the query and reports actual execution statistics such as planning time, execution time, and scan type.

---

### Q7. Should every column be indexed?

No.

Indexes consume storage, slow write operations, and are only beneficial for columns frequently used in search, filtering, joins, or sorting.

---

# Cheat Sheet

```text
Need Data

↓

Index Exists?

↓

YES

↓

Index Scan

↓

Fast

────────────

NO

↓

Sequential Scan

↓

Slow
```

---

```sql
CREATE INDEX idx_students_email

ON students(email);
```

---

```sql
EXPLAIN

SELECT ...
```

---

```sql
EXPLAIN ANALYZE

SELECT ...
```

---

# 🏗 Why does this exist?

## What problem does it solve?

Without indexes:

- Queries become slower as tables grow.
- PostgreSQL performs Sequential Scans.
- APIs experience increased response times.

Indexes solve this by allowing PostgreSQL to locate matching rows efficiently.

---

## Who depends on it?

```text
FastAPI

↓

Repository

↓

SQL Query

↓

PostgreSQL Optimizer

↓

Indexes

↓

Database
```

The application issues SQL queries.

PostgreSQL decides whether to use available indexes.

---

## Who should NOT depend on it?

Business logic.

Neither the Service layer nor the Router should assume an index exists.

Performance optimization belongs entirely to the database layer.

---

## SQL Server Equivalent

```text
Clustered Index

↓

Non-Clustered Index

↓

Execution Plan
```

---

## PostgreSQL Equivalent

```text
B-Tree Index

↓

EXPLAIN

↓

EXPLAIN ANALYZE
```

Different terminology.

Same engineering principles.

---

# Key Takeaways

- Indexes improve query performance by reducing the amount of data PostgreSQL must scan.
- A Sequential Scan checks every row, while an Index Scan navigates directly to matching rows.
- `EXPLAIN` shows the execution plan without running the query.
- `EXPLAIN ANALYZE` executes the query and reports actual performance statistics.
- Indexes speed up reads but introduce additional work during inserts, updates, and deletes.
- Effective indexing is based on workload analysis rather than indexing every column.

---

# Revision Checklist

- [ ] Understand why indexes exist.
- [ ] Can explain Sequential Scan vs Index Scan.
- [ ] Can create indexes in PostgreSQL.
- [ ] Know when indexes improve performance.
- [ ] Understand the cost of maintaining indexes.
- [ ] Can use `EXPLAIN`.
- [ ] Can use `EXPLAIN ANALYZE`.
- [ ] Can explain indexing confidently in an interview.

---

# Engineering Evolution

Our Student Management backend has continued its progression toward production readiness.

```text
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
        │
        ▼
Day 021
Connection Pooling
        │
        ▼
Day 022
Database Indexing & Query Performance
```

Notice how our focus has shifted.

Initially we concentrated on writing correct code.

Now we're learning how to build **fast**, **efficient**, and **scalable** systems.

Understanding indexes is one of the most valuable backend engineering skills because almost every production application eventually encounters performance problems as data grows.

---

# Mental Model

Imagine a city's telephone directory.

Without a directory:

```text
Need Person

↓

Visit Every House

↓

Find Person
```

With a directory:

```text
Need Person

↓

Search Directory

↓

Exact Address

↓

Reach House
```

An index is the database's telephone directory.

It doesn't contain the actual records.

It simply tells PostgreSQL where those records are located.

---

# Tomorrow's Preview

- Pagination
- LIMIT & OFFSET
- Sorting & Filtering
- Efficient API Responses
- Searching Large Datasets
- Designing Scalable List Endpoints
