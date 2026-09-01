# Day 030 — Advanced SQL JOINs & Relational Query Design

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 26 August 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Explain why relational databases require JOINs.
- Understand `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, and `FULL OUTER JOIN`.
- Write JOIN conditions using `ON`.
- Understand table aliases and why they make multi-table queries readable.
- Understand the difference between filtering in `ON` and `WHERE` for outer joins.
- Combine JOINs with `GROUP BY`, `COUNT`, and `HAVING`.
- Traverse a relational model such as `students → enrollments → courses`.
- Understand how JOIN queries belong in the Repository layer.
- Connect JOIN design with indexing and query performance.

PostgreSQL defines a joined table as a table derived from two source tables according to the selected join type, with the join condition determining which rows match. `FROM`, `WHERE`, `GROUP BY`, and `HAVING` form successive transformations of the table expression. citeturn927110view0

---

# Big Picture

Our backend has now reached the point where database queries need to reflect the **relationships between entities**, not just retrieve rows from one table.

```text
Day 06
Relational Database Design
        ↓
Day 07
PostgreSQL + Python
        ↓
Day 08
CRUD + Database Helper
        ↓
Day 09
Repository Pattern
        ↓
Day 20
Transactions
        ↓
Day 22
Indexes + Query Performance
        ↓
Day 25–29
Dockerized Database + Backend
        ↓
⭐ Day 30
Advanced SQL JOINs
```

The key shift today is:

```text
"Give me rows from this table."

        ↓

"Give me information that exists across related tables."
```

---

# 1. Why JOINs Exist

Relational databases intentionally separate different entities into different tables.

For example:

```text
students
---------
student_id
name
email
```

```text
courses
--------
course_id
name
```

```text
enrollments
-----------
student_id
course_id
```

This avoids storing the same student or course information repeatedly.

But eventually we need questions like:

> Which courses is Rahul enrolled in?

That information is not stored in one table.

We need to combine:

```text
students
    ↓
enrollments
    ↓
courses
```

This is exactly what JOINs are for.

---

# 2. Our Relational Model

Visualize the relationships first:

```text
                 students
              ┌─────────────┐
              │ student_id  │
              │ name        │
              │ email       │
              └──────┬──────┘
                     │
                     │ 1
                     │
                     │ many
                     ▼
              ┌─────────────┐
              │ enrollments │
              │ student_id  │
              │ course_id   │
              └──────┬──────┘
                     │
                     │ many
                     │
                     │ 1
                     ▼
                 courses
              ┌─────────────┐
              │ course_id   │
              │ name        │
              └─────────────┘
```

The relationship is:

```text
Student
   ↓
Enrollment
   ↓
Course
```

---

# 3. What Is a JOIN?

A JOIN combines rows from two tables according to a join condition.

General structure:

```sql
SELECT ...
FROM table_a a
JOIN table_b b
    ON a.some_id = b.some_id;
```

PostgreSQL documents JOINs as joined table expressions derived from two source tables according to the selected join type. JOINs can also be chained or nested. citeturn927110view0

Think:

```text
Table A
   +
Table B
   ↓
Matching condition
   ↓
Combined result
```

---

# 4. INNER JOIN

`INNER JOIN` returns rows where the join condition matches.

Example:

```sql
SELECT
    s.student_id,
    s.name,
    e.course_id
FROM students s
INNER JOIN enrollments e
    ON s.student_id = e.student_id;
```

Conceptually:

```text
students
   │
   ├── Rahul  ─────── enrollment
   ├── Priya  ─────── enrollment
   └── Amit   ─────── no enrollment

INNER JOIN

Result:
Rahul
Priya
```

A student with no matching enrollment is not included. citeturn927110view0

---

# 5. LEFT JOIN

A `LEFT JOIN` keeps every row from the left table and adds matching data from the right table.

```sql
SELECT
    s.student_id,
    s.name,
    e.course_id
FROM students s
LEFT JOIN enrollments e
    ON s.student_id = e.student_id;
```

Suppose:

```text
students
---------
Rahul
Priya
Mayank
Amit
```

and:

```text
enrollments
-----------
Rahul
Priya
Mayank
```

Result:

```text
Rahul
Priya
Mayank
Amit → NULL
```

PostgreSQL defines a left outer join as preserving at least one result row for every row from the left table, using nulls for unmatched right-side columns. citeturn927110view0

---

# 6. INNER JOIN vs LEFT JOIN

| INNER JOIN                             | LEFT JOIN                           |
| -------------------------------------- | ----------------------------------- |
| Keeps matching rows                    | Keeps all left-side rows            |
| Unmatched left rows disappear          | Unmatched left rows remain          |
| Useful for only-related-record queries | Useful for all-left-record queries  |
| Missing relationships are excluded     | Missing relationships become `NULL` |

Mental model:

```text
INNER JOIN
    ↓
Only matches

LEFT JOIN
    ↓
Everything on the left
+
matches on the right
```

---

# 7. RIGHT JOIN

A `RIGHT JOIN` is the mirror image of `LEFT JOIN`.

```sql
SELECT
    s.name,
    e.course_id
FROM students s
RIGHT JOIN enrollments e
    ON s.student_id = e.student_id;
```

It preserves every row from the right table. PostgreSQL documents it as the converse of a left join. citeturn927110view0

In practice, many teams rewrite a `RIGHT JOIN` as a `LEFT JOIN` by swapping table order because the resulting query can be easier to read.

---

# 8. FULL OUTER JOIN

A `FULL OUTER JOIN` keeps unmatched rows from both sides.

```sql
SELECT
    s.name,
    e.course_id
FROM students s
FULL OUTER JOIN enrollments e
    ON s.student_id = e.student_id;
```

Conceptually:

```text
Left-only rows
+
Matching rows
+
Right-only rows
```

PostgreSQL describes a full outer join as preserving unmatched rows from both source tables and filling the opposite side with nulls. citeturn927110view0

---

# 9. The JOIN Condition — `ON`

The most important part of a normal JOIN is:

```sql
ON s.student_id = e.student_id
```

This answers:

> **When should these two rows be considered related?**

So always ask:

```text
What is the relationship?
        ↓
Which keys connect these tables?
        ↓
What belongs in ON?
```

Without an intentional join condition, you can accidentally create a Cartesian product.

---

# 10. Table Aliases

Queries become much easier to read with aliases.

Instead of:

```text
students.student_id
enrollments.student_id
courses.course_id
```

we can write:

```text
s.student_id
e.student_id
c.course_id
```

Example:

```sql
SELECT
    s.name,
    c.name
FROM students AS s
JOIN enrollments AS e
    ON s.student_id = e.student_id
JOIN courses AS c
    ON e.course_id = c.course_id;
```

PostgreSQL documents table aliases as temporary names usable throughout the current query and notes that they are especially useful for readable joins. citeturn927110view0

---

# 11. Three-Table JOIN

Now we reach the query that matters for the project.

```sql
SELECT
    s.name AS student_name,
    c.name AS course_name
FROM students s
JOIN enrollments e
    ON s.student_id = e.student_id
JOIN courses c
    ON e.course_id = c.course_id;
```

Flow:

```text
students
   |
   | student_id
   v
enrollments
   |
   | course_id
   v
courses
```

Result:

```text
student_name | course_name
-------------+-------------
Rahul        | Python
Rahul        | Docker
Priya        | Python
Mayank       | PostgreSQL
```

---

# 12. LEFT JOIN With Three Tables

Suppose we want every student, even students with no course.

```sql
SELECT
    s.name AS student_name,
    c.name AS course_name
FROM students s
LEFT JOIN enrollments e
    ON s.student_id = e.student_id
LEFT JOIN courses c
    ON e.course_id = c.course_id;
```

Result conceptually:

```text
Rahul   Python
Rahul   Docker
Priya   Python
Mayank  PostgreSQL
Amit    NULL
```

This is a common business-reporting pattern.

---

# 13. `ON` vs `WHERE` With LEFT JOIN

Consider:

```sql
SELECT *
FROM students s
LEFT JOIN enrollments e
    ON s.student_id = e.student_id
       AND e.course_id = 101;
```

Compare:

```sql
SELECT *
FROM students s
LEFT JOIN enrollments e
    ON s.student_id = e.student_id
WHERE e.course_id = 101;
```

These are not equivalent for an outer join.

The first keeps the left-side rows while limiting which right-side rows qualify as matches.

The second filters the joined result afterward and can remove rows whose right-side values are `NULL`.

PostgreSQL explicitly documents that restrictions in `ON` are processed during the join while restrictions in `WHERE` are applied after the join, which matters significantly for outer joins. citeturn927110view0

Mental model:

```text
ON
↓
Controls matching

WHERE
↓
Filters resulting rows
```

---

# 14. GROUP BY After JOIN

JOINs become much more powerful when combined with aggregation.

Suppose we want:

> How many courses is each student enrolled in?

```sql
SELECT
    s.student_id,
    s.name,
    COUNT(e.course_id) AS course_count
FROM students s
LEFT JOIN enrollments e
    ON s.student_id = e.student_id
GROUP BY
    s.student_id,
    s.name;
```

Conceptually:

```text
Rahul   2
Priya   1
Mayank  1
Amit    0
```

PostgreSQL describes `GROUP BY` and `HAVING` as successive transformations of the intermediate table produced from `FROM`/JOIN. citeturn927110view0

---

# 15. Why `COUNT(e.course_id)`?

With a `LEFT JOIN`, an unmatched student produces:

```text
e.course_id = NULL
```

Therefore:

```sql
COUNT(e.course_id)
```

returns `0` for that student.

This differs from:

```sql
COUNT(*)
```

which counts the preserved left-side row too.

That distinction is useful whenever a `LEFT JOIN` is being used to report zero related records.

---

# 16. HAVING

Now answer:

> Which students are enrolled in more than one course?

```sql
SELECT
    s.student_id,
    s.name,
    COUNT(e.course_id) AS course_count
FROM students s
LEFT JOIN enrollments e
    ON s.student_id = e.student_id
GROUP BY
    s.student_id,
    s.name
HAVING COUNT(e.course_id) > 1;
```

Logical structure:

```text
JOIN
 ↓
GROUP BY
 ↓
COUNT
 ↓
HAVING
```

`HAVING` filters groups after aggregation, whereas `WHERE` filters rows before grouping. citeturn927110view0

---

# 17. Real-World Questions JOINs Answer

Examples:

```text
Which customers have orders?

Which customers have never placed an order?

Which products belong to each category?

Which employees belong to each department?

Which users have active subscriptions?

Which students have multiple courses?

Which courses have no enrolled students?
```

The SQL changes.

The relational reasoning stays the same.

---

# 18. JOINs and the Repository Layer

Our application architecture is:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
Database Helper
   ↓
PostgreSQL
```

The Service should not contain raw JOIN SQL.

Instead:

```python
students = repository.get_students_with_courses()
```

while the Repository handles the query:

```sql
SELECT
    ...
FROM students s
JOIN enrollments e
    ...
JOIN courses c
    ...
```

The Repository Pattern exists to hide persistence details from the application layers. fileciteturn0file1L262-L280

---

# 19. Why This Separation Matters

Without Repository:

```text
Router
   ↓
SQL JOIN
   ↓
Database
```

With Repository:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
JOIN query
   ↓
Database
```

The Service asks for:

```text
students with courses
```

rather than knowing which SQL tables must be joined.

---

# 20. JOINs and Indexes

Today's topic connects directly to Day 22.

Consider:

```sql
ON s.student_id = e.student_id
```

and:

```sql
ON e.course_id = c.course_id
```

If these relationships are queried frequently on large tables, indexes on the relevant columns may be important.

For example:

```sql
CREATE INDEX idx_enrollments_student_id
ON enrollments(student_id);
```

and:

```sql
CREATE INDEX idx_enrollments_course_id
ON enrollments(course_id);
```

But:

> **Do not create indexes blindly.**

The right design depends on query frequency, selectivity, table size, write volume, existing indexes, and actual execution plans.

Your Day 22 `EXPLAIN` / `EXPLAIN ANALYZE` knowledge is the tool we will use to measure these queries. fileciteturn0file6L13-L19

---

# 21. JOIN Does Not Automatically Mean Slow

A common misconception is:

> "JOINs are expensive, so avoid them."

That is not a useful engineering rule.

Relational databases are designed to work with related tables.

Instead ask:

```text
Is the query logically correct?
        ↓
Are the join predicates correct?
        ↓
Are the relevant indexes appropriate?
        ↓
What does EXPLAIN say?
```

Performance should be measured, not guessed.

---

# 22. JOIN Result Cardinality

A JOIN can produce more rows than either source table.

Example:

```text
Rahul → Python
Rahul → Docker
Rahul → PostgreSQL
```

Rahul appears three times because there are three matching enrollment rows.

That is not necessarily duplicate data.

It is the expected result of a one-to-many relationship:

```text
1 Student
   ↓
Many Enrollments
   ↓
Many result rows
```

This is important when debugging apparently duplicated API results.

---

# 23. Common JOIN Mistakes

## Mistake 1 — Missing JOIN condition

A JOIN without an intentional relationship can produce an unintended Cartesian product.

## Mistake 2 — Joining on the wrong columns

A query can execute successfully while returning logically incorrect data.

SQL correctness is not only syntax; it is relationship correctness.

## Mistake 3 — Using INNER JOIN when you need all left-side rows

Requirement:

> Show every student, including those with no enrollment.

Correct choice:

```text
LEFT JOIN
```

## Mistake 4 — Filtering an outer join incorrectly

This pattern can remove the `NULL` rows you intended to preserve:

```sql
LEFT JOIN ...
WHERE right_table.some_column = ...
```

## Mistake 5 — Using `SELECT *` in production queries

Prefer explicit columns:

```sql
SELECT
    s.name,
    c.name
```

rather than:

```sql
SELECT *
```

This makes the result contract clearer and reduces accidental coupling to schema changes.

---

# 24. Production-Oriented JOIN Practices

✅ Use meaningful table aliases.

✅ Make JOIN conditions explicit.

✅ Select only required columns.

✅ Understand result cardinality.

✅ Use `LEFT JOIN` intentionally.

✅ Be careful with `ON` vs `WHERE`.

✅ Index relationship columns when justified.

✅ Validate performance with `EXPLAIN ANALYZE`.

✅ Keep SQL inside the Repository/data-access layer.

---

# 25. Interview Questions

### Q1. What is an INNER JOIN?

It returns rows for matching pairs satisfying the join condition.

### Q2. What is a LEFT JOIN?

It preserves every row from the left table and adds matching rows from the right, using `NULL` when no match exists. citeturn927110view0

### Q3. Why use LEFT JOIN instead of INNER JOIN?

When you need all rows from the left table, including those without a related row on the right.

### Q4. Why can a JOIN appear to duplicate rows?

Because one row on the left may have multiple matching rows on the right.

### Q5. What is the difference between `ON` and `WHERE` with a LEFT JOIN?

`ON` controls which rows match during the join; `WHERE` filters the result afterward. Moving a condition from `ON` to `WHERE` can remove unmatched left-side rows. citeturn927110view0

### Q6. What does `GROUP BY` do?

It groups rows so aggregate functions such as `COUNT`, `SUM`, or `AVG` can be applied per group.

### Q7. What does `HAVING` do?

It filters groups after aggregation.

### Q8. Where should JOIN SQL live in Clean Architecture?

In the Repository/data-access layer, rather than in the Router or business Service layer.

### Q9. How can JOIN performance be improved?

Use correct schema design, correct join predicates, relevant indexes, and execution-plan analysis such as `EXPLAIN ANALYZE`.

---

# 26. FastAPI ↔ ASP.NET Core Mapping

The principle is framework-independent.

```text
ASP.NET Core Controller
        ↓
Service
        ↓
Repository
        ↓
SQL / EF Core query
        ↓
PostgreSQL / SQL Server
```

The framework changes.

The relational reasoning does not.

---

# 27. Cheat Sheet

```text
INNER JOIN
→ Matching rows only

LEFT JOIN
→ All left rows + matching right rows

RIGHT JOIN
→ All right rows + matching left rows

FULL OUTER JOIN
→ All rows from both sides

ON
→ Defines the matching relationship

WHERE
→ Filters rows after the table expression

GROUP BY
→ Groups rows for aggregation

HAVING
→ Filters grouped results

COUNT
→ Counts rows/values

Alias
→ Short readable table name
```

Example:

```sql
SELECT
    s.name AS student_name,
    c.name AS course_name
FROM students s
JOIN enrollments e
    ON s.student_id = e.student_id
JOIN courses c
    ON e.course_id = c.course_id;
```

Mental translation:

```text
students
   ↓
match enrollments
   ↓
match courses
   ↓
return student + course
```

---

# 28. Final Mental Model

```text
                         Relational Model

                    ┌───────────────┐
                    │   STUDENTS    │
                    │               │
                    │ student_id    │
                    │ name          │
                    └───────┬───────┘
                            │
                            │ 1
                            │
                            │ many
                            ▼
                    ┌───────────────┐
                    │ ENROLLMENTS   │
                    │               │
                    │ student_id    │
                    │ course_id     │
                    └───────┬───────┘
                            │
                            │ many
                            │
                            │ 1
                            ▼
                    ┌───────────────┐
                    │    COURSES    │
                    │               │
                    │ course_id     │
                    │ name          │
                    └───────────────┘
```

Query:

```text
students
    ↓
    JOIN
    ↓
enrollments
    ↓
    JOIN
    ↓
courses
```

Application:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
JOIN Query
   ↓
PostgreSQL
```

Performance:

```text
JOIN
  +
Correct predicates
  +
Appropriate indexes
  +
EXPLAIN ANALYZE
  =
Measured query performance
```

---

# Key Takeaways

- JOINs allow a relational database to answer questions that span multiple related tables.
- `INNER JOIN` returns matching rows; `LEFT JOIN` preserves all rows from the left side and adds matching right-side data. citeturn927110view0
- `ON` defines the relationship between tables, while `WHERE` filters the resulting rows.
- For outer joins, moving a condition between `ON` and `WHERE` can materially change the result. citeturn927110view0
- JOINs can legitimately produce multiple result rows for one entity when the relationship is one-to-many.
- `GROUP BY`, `COUNT`, and `HAVING` turn relational data into useful business summaries.
- JOIN SQL belongs in the Repository/data-access layer, keeping the Service layer focused on business behavior. fileciteturn0file1L262-L280
- JOIN performance should be measured using indexes and execution plans rather than avoided through blanket rules.
- Today marks the beginning of the advanced SQL/database-engineering part of Project ₹50L.

---

# Project ₹50L — Architecture Evolution

```text
Day 22
Indexes + Query Performance
        │
        ▼
Day 23–29
Docker + Compose + Deployment
        │
        ▼
⭐ Day 30
Advanced SQL JOINs
        │
        ├── INNER JOIN
        ├── LEFT JOIN
        ├── Multi-table JOIN
        ├── GROUP BY
        ├── HAVING
        └── Repository Integration
        │
        ▼
Next
JOIN Performance
+
Query Optimization
+
Advanced Repository Queries
```

The broader progression is:

```text
Relational Schema
      ↓
Relationships
      ↓
JOINs
      ↓
Aggregation
      ↓
Indexing
      ↓
Execution Plans
      ↓
Query Optimization
```

We are now teaching the database to answer **real business questions**, not merely performing CRUD.

---

# Revision Checklist

- [ ] Can explain why JOINs exist.
- [ ] Can explain INNER JOIN.
- [ ] Can explain LEFT JOIN.
- [ ] Understand RIGHT and FULL OUTER JOIN.
- [ ] Can write JOIN conditions with `ON`.
- [ ] Can use table aliases.
- [ ] Understand `ON` vs `WHERE` for outer joins.
- [ ] Can chain multiple JOINs.
- [ ] Can combine JOIN + GROUP BY + COUNT.
- [ ] Can use HAVING after aggregation.
- [ ] Understand one-to-many JOIN cardinality.
- [ ] Know why JOIN SQL belongs in the Repository.
- [ ] Understand how indexes can support JOIN performance.
- [ ] Know that query performance should be measured with execution plans.

---

# Exact Resources Used

- PostgreSQL — Table Expressions / JOINs: https://www.postgresql.org/docs/current/queries-table-expressions.html
  - `7.2.1.1 Joined Tables`
  - INNER / LEFT / RIGHT / FULL JOIN
  - `ON` / `USING`
  - table aliases
  - `ON` vs `WHERE` behavior for outer joins
- PostgreSQL — SELECT: https://www.postgresql.org/docs/current/sql-select.html
- PostgreSQL — Aggregate Functions: https://www.postgresql.org/docs/current/functions-aggregate.html

The PostgreSQL documentation confirms the JOIN semantics, table-expression pipeline, join conditions, aliases, and outer-join filtering behavior used throughout this chapter. citeturn927110view0turn927110view1turn927110view2
