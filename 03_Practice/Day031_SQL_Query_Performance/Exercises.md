# Day 031: SQL Query Performance - Exercises

## Exercise 1 — Baseline JOIN Plan

Start with your Day 30 three-table query:

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

Run:

```sql
EXPLAIN
SELECT ...
```

Do not change anything yet.

Your job is simply to inspect:

- `Scan`
- `Join`
- `Cost`
- `Rows`

## Exercise 2 — Read the Plan Tree

Take your EXPLAIN output and identify:

```
Top node
  ↓
Join
  ↓
Child scan
  ↓
Child scan
```

### Remember:

- The indentation represents the hierarchy of the plan tree.
- PostgreSQL's documentation explicitly uses this tree structure to show how parent nodes consume the results of their child nodes.

### Write down:

1. Top-level operation:
2. Join strategy:
3. Scan strategy for students:
4. Scan strategy for enrollments:
5. Scan strategy for courses:

## Exercise 3 — EXPLAIN ANALYZE

Now run:

```sql
EXPLAIN ANALYZE
SELECT ...
```

This is where you move from:

- **Estimated**

to:

- **Actual**

Look specifically for:

- `cost=`
- `rows=`
- `actual time=`
- `loops=`

PostgreSQL explains that `EXPLAIN` shows planner estimates while `EXPLAIN ANALYZE` actually executes the query and reports measured execution information alongside the plan.

## Exercise 4 — Estimated vs Actual Rows

Look for:

- `rows=`
- `actual rows=`

Compare them.

### Example mental model:

```
Planner estimate
  ↓
rows=100

Actual execution
  ↓
actual rows=950
```

That's an important signal.

If estimates are dramatically wrong, the planner may make poor choices.

You don't need to fix statistics today.

Just understand:

- The planner is making decisions using estimates.

## Exercise 5 — Add Data

Your Day 30 schema is small.

That means PostgreSQL may reasonably choose sequential scans.

This is where I want you to experiment.

Insert more data into the practice schema.

You do not need millions of rows today.

Even the following is enough to start observing different planning behavior:

- 1,000 students
- 5,000 enrollments
- 100 courses

If you want to reuse the larger synthetic-data mindset from Day 22, you can scale higher—but do not spend today's entire session generating millions of rows.

The important part is observing the plans.

## Exercise 6 — Add Indexes

Create appropriate indexes for your JOIN keys.

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

Then run:

```sql
EXPLAIN ANALYZE
SELECT ...
```

again.

Now compare:

```
Before index
  ↓
EXPLAIN ANALYZE

After index
  ↓
EXPLAIN ANALYZE
```

This connects:

- Day 22: Indexes
- Day 30: JOINs
- Day 31: Execution Plans

## Exercise 7 — Don't Expect the Index to Always Win

This is extremely important.

You may discover that PostgreSQL still chooses:

```
Seq Scan
```

even after you add an index.

That is **not necessarily a problem**.

### Why?

If the table is small or the query returns a large percentage of rows, a sequential scan can be cheaper.

PostgreSQL's documentation explicitly shows cases where sequential scanning can be preferred and explains that planner decisions depend on estimated costs and expected row counts.

### The correct engineering mindset is:

> "I created an index."
>
> **Not:** "It MUST use the index."
>
> **Instead:** "Let's see what the planner chooses."

This is a very important shift in thinking.

## Exercise 8 — EXPLAIN (ANALYZE, BUFFERS)

Now run:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...
```

Look for:

```
Buffers:
```

You don't need to master every buffer field today.

Just understand the broad idea:

```
EXPLAIN
  ↓
Plan

ANALYZE
  ↓
Actual execution

BUFFERS
  ↓
I/O / buffer usage information
```

This is the beginning of real database-performance investigation.

## Exercise 9 — Remove the Index Experiment

Drop one of your practice indexes:

```sql
DROP INDEX idx_enrollments_student_id;
```

Run:

```sql
EXPLAIN ANALYZE
SELECT ...
```

Then recreate it:

```sql
CREATE INDEX ...
```

Run the plan again.

Compare.

This gives you:

```
No index
  ↓
Plan

Index
  ↓
Plan
```

Don't only compare execution time.

Compare:

- Join strategy
- Scan strategy
- Estimated rows
- Actual rows
- Cost
- Buffers

## Exercise 10 — Repository Connection

Today we do not need to modify the production Repository.

Instead, write a short note answering:

> If tomorrow I add a `get_students_with_courses()` method to the Repository, where should performance investigation happen?

### Correct engineering flow:

```
Service
  ↓
Repository method
  ↓
SQL JOIN
  ↓
PostgreSQL
  ↓
EXPLAIN ANALYZE
  ↓
Optimization
```

**The Service should NOT contain:**

```sql
EXPLAIN ANALYZE ...
```

**The performance investigation belongs to the database/query engineering workflow.**

---

**And ideally your practice notes should contain before/after evidence, not just conclusions.**

### For example:

```
Query
  ↓
Plan before index
  ↓
Index created
  ↓
Plan after index
  ↓
Observation
```
