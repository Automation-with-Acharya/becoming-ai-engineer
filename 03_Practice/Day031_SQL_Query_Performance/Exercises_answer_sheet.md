# Day 031: SQL Query Performance — Answer Sheet

**Date:** 2026-09-02  
**Schema:** `practice_schema` (renamed from `day030_joins`) inside `student_db`  
**Tools Used:** PostgreSQL 18 (locally installed), `psql` CLI  

---

## Pre-Exercise Setup

### Schema Rename

The schema `day030_joins` was renamed to `practice_schema` as requested:

```sql
ALTER SCHEMA day030_joins RENAME TO practice_schema;
```

### Original Data (before Exercise 5)

| Table       | Rows |
|-------------|------|
| students    | 4    |
| courses     | 3    |
| enrollments | 4    |

**Sample data:**
- **students:** Rahul (1), Priya (2), Mayank (3), Amit (4)
- **courses:** Python (101), Docker (102), PostgreSQL (103)
- **enrollments:** (1→101), (1→102), (2→101), (3→103)

### Table Structures

```
practice_schema.students
  student_id  INTEGER   PRIMARY KEY
  name        VARCHAR(100)

practice_schema.courses
  course_id   INTEGER   PRIMARY KEY
  name        VARCHAR(100)

practice_schema.enrollments
  student_id  INTEGER   NOT NULL  FK → students
  course_id   INTEGER   NOT NULL  FK → courses
  PRIMARY KEY (student_id, course_id)
```

---

## Exercise 1 — Baseline JOIN Plan

### Query Used

```sql
EXPLAIN
SELECT
  s.name AS student_name,
  c.name AS course_name
FROM practice_schema.students s
JOIN practice_schema.enrollments e
  ON s.student_id = e.student_id
JOIN practice_schema.courses c
  ON e.course_id = c.course_id;
```

### Output (small dataset — 4 students, 3 courses, 4 enrollments)

```
                                   QUERY PLAN
---------------------------------------------------------------------------------
 Hash Join  (cost=34.40..79.02 rows=2260 width=436)
   Hash Cond: (e.course_id = c.course_id)
   ->  Hash Join  (cost=17.20..55.81 rows=2260 width=222)
         Hash Cond: (e.student_id = s.student_id)
         ->  Seq Scan on enrollments e  (cost=0.00..32.60 rows=2260 width=8)
         ->  Hash  (cost=13.20..13.20 rows=320 width=222)
               ->  Seq Scan on students s  (cost=0.00..13.20 rows=320 width=222)
   ->  Hash  (cost=13.20..13.20 rows=320 width=222)
         ->  Seq Scan on courses c  (cost=0.00..13.20 rows=320 width=222)
(9 rows)
```

### What to Inspect

| Field    | Value                                             |
|----------|---------------------------------------------------|
| Scan     | Seq Scan on all three tables                      |
| Join     | Hash Join (two levels)                            |
| Cost     | Total: 34.40..79.02 (startup..total)              |
| Rows     | Estimated 2260 — very inaccurate (actual = 4)     |

> **NOTE:** The planner estimated 2260 rows but the table only had 4 rows because statistics
> hadn't been run on this small dataset yet. This is the estimation gap studied in Exercise 4.

---

## Exercise 2 — Read the Plan Tree

### Plan Tree Structure

```
Hash Join                            <- Top node
  |
  +-- Hash Join                      <- Join strategy (inner: student_id)
  |     |
  |     +-- Seq Scan on enrollments  <- Child scan (driving table)
  |     |
  |     +-- Hash
  |           |
  |           +-- Seq Scan on students   <- Child scan (inner: hashed)
  |
  +-- Hash
        |
        +-- Seq Scan on courses      <- Child scan (courses hashed)
```

### Answers

| #  | Question                              | Answer                                |
|----|---------------------------------------|---------------------------------------|
| 1  | Top-level operation                   | Hash Join (on course_id)              |
| 2  | Join strategy                         | Hash Join — used for both joins       |
| 3  | Scan strategy for students            | Seq Scan (Sequential Scan)            |
| 4  | Scan strategy for enrollments         | Seq Scan (Sequential Scan)            |
| 5  | Scan strategy for courses             | Seq Scan (Sequential Scan)            |

### Why Hash Join?

PostgreSQL chose Hash Join because:
- Tables are small — building an in-memory hash table is cheap
- No index on join keys (FK columns in enrollments)
- Hash Join is efficient when the smaller side fits in memory (Batches: 1)

---

## Exercise 3 — EXPLAIN ANALYZE

### Query

```sql
EXPLAIN ANALYZE
SELECT
  s.name AS student_name,
  c.name AS course_name
FROM practice_schema.students s
JOIN practice_schema.enrollments e
  ON s.student_id = e.student_id
JOIN practice_schema.courses c
  ON e.course_id = c.course_id;
```

### Output (small dataset — before adding bulk data)

```
                                                          QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------
 Hash Join  (cost=34.40..79.02 rows=2260 width=436) (actual time=0.041..0.043 rows=4.00 loops=1)
   Hash Cond: (e.course_id = c.course_id)
   Buffers: shared hit=3
   ->  Hash Join  (cost=17.20..55.81 rows=2260 width=222) (actual time=0.023..0.025 rows=4.00 loops=1)
         Hash Cond: (e.student_id = s.student_id)
         Buffers: shared hit=2
         ->  Seq Scan on enrollments e  (cost=0.00..32.60 rows=2260 width=8) (actual time=0.009..0.009 rows=4.00 loops=1)
               Buffers: shared hit=1
         ->  Hash  (cost=13.20..13.20 rows=320 width=222) (actual time=0.009..0.009 rows=4.00 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 9kB
               Buffers: shared hit=1
               ->  Seq Scan on students s  (cost=0.00..13.20 rows=320 width=222) (actual time=0.006..0.006 rows=4.00 loops=1)
                     Buffers: shared hit=1
   ->  Hash  (cost=13.20..13.20 rows=320 width=222) (actual time=0.013..0.013 rows=3.00 loops=1)
         Buckets: 1024  Batches: 1  Memory Usage: 9kB
         Buffers: shared hit=1
         ->  Seq Scan on courses c  (cost=0.00..13.20 rows=320 width=222) (actual time=0.011..0.011 rows=3.00 loops=1)
               Buffers: shared hit=1
 Planning:
   Buffers: shared hit=196
 Planning Time: 0.529 ms
 Execution Time: 0.062 ms
(22 rows)
```

### Key Fields

| Field          | What it tells you                                         |
|----------------|-----------------------------------------------------------|
| cost=          | Planner's estimated cost (startup..total)                 |
| rows=          | Planner's estimated row count                             |
| actual time=   | Measured wall-clock time in ms (start..end)               |
| loops=         | How many times this node was executed                     |

> **IMPORTANT:** EXPLAIN shows what the planner THINKS will happen.
> EXPLAIN ANALYZE shows what ACTUALLY happened — it runs the query for real.

---

## Exercise 4 — Estimated vs Actual Rows

### Comparison (small dataset)

| Node                    | Estimated (rows=) | Actual (actual rows=) | Delta      |
|-------------------------|-------------------|-----------------------|------------|
| Seq Scan on enrollments | 2260              | 4                     | 565x off   |
| Seq Scan on students    | 320               | 4                     | 80x off    |
| Seq Scan on courses     | 320               | 3                     | 106x off   |
| Hash Join (outer)       | 2260              | 4                     | 565x off   |

### Why Were Estimates So Wrong?

The planner uses table statistics stored in pg_statistic. For this tiny table (only 4 rows),
statistics were stale. The default stats assumed much larger tables. Running ANALYZE fixes this.

### Engineering Implication

> If estimates are dramatically wrong, the planner may make poor join strategy choices.
> Running ANALYZE on tables after large data changes keeps statistics accurate.

---

## Exercise 5 — Add Data

### Synthetic Data Inserted

```sql
-- 97 new courses (course_id 104-200)
INSERT INTO practice_schema.courses (course_id, name)
SELECT gs, 'Course_' || gs
FROM generate_series(104, 200) AS gs;

-- 996 new students (student_id 5-1000)
INSERT INTO practice_schema.students (student_id, name)
SELECT gs, 'Student_' || gs
FROM generate_series(5, 1000) AS gs;

-- ~13,948 enrollments
INSERT INTO practice_schema.enrollments (student_id, course_id)
SELECT
  (floor(random() * 1000) + 1)::int,
  (floor(random() * 100) + 101)::int
FROM generate_series(1, 15000)
ON CONFLICT DO NOTHING;

-- Update planner statistics
ANALYZE practice_schema.students;
ANALYZE practice_schema.enrollments;
ANALYZE practice_schema.courses;
```

### Final Row Counts

| Table       | Rows   |
|-------------|--------|
| students    | 1,000  |
| courses     | 100    |
| enrollments | 13,948 |

### EXPLAIN After Adding Data (no indexes yet)

```
                                   QUERY PLAN
---------------------------------------------------------------------------------
 Hash Join  (cost=37.75..356.16 rows=13948 width=21)
   Hash Cond: (e.course_id = c.course_id)
   ->  Hash Join  (cost=33.50..313.75 rows=13948 width=15)
         Hash Cond: (e.student_id = s.student_id)
         ->  Seq Scan on enrollments e  (cost=0.00..243.48 rows=13948 width=8)
         ->  Hash  (cost=21.00..21.00 rows=1000 width=15)
               ->  Seq Scan on students s  (cost=0.00..21.00 rows=1000 width=15)
   ->  Hash  (cost=3.00..3.00 rows=100 width=14)
         ->  Seq Scan on courses c  (cost=0.00..3.00 rows=100 width=14)
(9 rows)
```

### Observation

After running ANALYZE, the estimates are now accurate — the planner correctly estimates
rows=13948 for enrollments, matching the actual row count. Fresh statistics are critical
to good planning decisions.

---

## Exercise 6 — Add Indexes

### Indexes Created

```sql
CREATE INDEX idx_enrollments_student_id
ON practice_schema.enrollments(student_id);

CREATE INDEX idx_enrollments_course_id
ON practice_schema.enrollments(course_id);
```

### EXPLAIN ANALYZE — Before Indexes

```
 Hash Join  (cost=37.75..356.16 rows=13948 width=21) (actual time=0.174..3.234 rows=13948.00 loops=1)
   Hash Cond: (e.course_id = c.course_id)
   Buffers: shared hit=117
   ->  Hash Join  (cost=33.50..313.75 rows=13948 width=15) (actual time=0.143..2.021 rows=13948.00 loops=1)
         Hash Cond: (e.student_id = s.student_id)
         Buffers: shared hit=115
         ->  Seq Scan on enrollments e  (cost=0.00..243.48 rows=13948 width=8) (actual time=0.005..0.450 rows=13948.00 loops=1)
               Buffers: shared hit=104
         ->  Hash  (cost=21.00..21.00 rows=1000 width=15) (actual time=0.128..0.128 rows=1000.00 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 55kB
               Buffers: shared hit=11
               ->  Seq Scan on students s  (cost=0.00..21.00 rows=1000 width=15) (actual time=0.006..0.068 rows=1000.00 loops=1)
                     Buffers: shared hit=11
   ->  Hash  (cost=3.00..3.00 rows=100 width=14) (actual time=0.027..0.027 rows=100.00 loops=1)
         Buckets: 1024  Batches: 1  Memory Usage: 13kB
         Buffers: shared hit=2
         ->  Seq Scan on courses c  (cost=0.00..3.00 rows=100 width=14) (actual time=0.009..0.016 rows=100.00 loops=1)
               Buffers: shared hit=2
 Planning:
   Buffers: shared hit=228
 Planning Time: 0.730 ms
 Execution Time: 3.534 ms
```

### EXPLAIN ANALYZE — After Indexes

```
 Hash Join  (cost=37.75..356.16 rows=13948 width=21) (actual time=0.179..3.596 rows=13948.00 loops=1)
   Hash Cond: (e.course_id = c.course_id)
   Buffers: shared hit=117
   ->  Hash Join  (cost=33.50..313.75 rows=13948 width=15) (actual time=0.151..2.205 rows=13948.00 loops=1)
         Hash Cond: (e.student_id = s.student_id)
         Buffers: shared hit=115
         ->  Seq Scan on enrollments e  (cost=0.00..243.48 rows=13948 width=8) (actual time=0.008..0.478 rows=13948.00 loops=1)
               Buffers: shared hit=104
         ->  Hash  (cost=21.00..21.00 rows=1000 width=15) (actual time=0.133..0.134 rows=1000.00 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 55kB
               Buffers: shared hit=11
               ->  Seq Scan on students s  (cost=0.00..21.00 rows=1000 width=15) (actual time=0.006..0.069 rows=1000.00 loops=1)
                     Buffers: shared hit=11
   ->  Hash  (cost=3.00..3.00 rows=100 width=14) (actual time=0.025..0.025 rows=100.00 loops=1)
         Buckets: 1024  Batches: 1  Memory Usage: 13kB
         Buffers: shared hit=2
         ->  Seq Scan on courses c  (cost=0.00..3.00 rows=100 width=14) (actual time=0.009..0.016 rows=100.00 loops=1)
               Buffers: shared hit=2
 Planning:
   Buffers: shared hit=248 read=5
 Planning Time: 0.852 ms
 Execution Time: 3.928 ms
```

### Before vs After Index Comparison

| Metric              | Before Index     | After Index       |
|---------------------|------------------|-------------------|
| Join strategy       | Hash Join        | Hash Join         |
| Scan — enrollments  | Seq Scan         | Seq Scan          |
| Scan — students     | Seq Scan         | Seq Scan          |
| Scan — courses      | Seq Scan         | Seq Scan          |
| Execution Time      | 3.534 ms         | 3.928 ms          |
| Buffers (planning)  | hit=228          | hit=248 read=5    |
| Total cost estimate | 356.16           | 356.16            |

> The planner chose the SAME plan (Hash Join + Seq Scan) with or without indexes.
> See Exercise 7 for why this is expected and correct behaviour.

---

## Exercise 7 — Don't Expect the Index to Always Win

### Observation

Despite creating idx_enrollments_student_id and idx_enrollments_course_id, PostgreSQL
still chose Seq Scan for all tables. This is NOT a bug — it is the correct decision.

### Why PostgreSQL Chose Seq Scan

1. **Full table output**: The query returns ALL 13,948 enrollments. Reading the index first
   (BTree lookup then heap fetch per row) costs MORE than a straight sequential scan.

2. **Cost math**: Index scans shine for selective queries (e.g., WHERE student_id = 42).
   For full-table joins, the overhead of following index pointers per row is greater.

3. **Hash Join is already optimal here**: PostgreSQL builds hash tables of smaller relations
   (students, courses) in memory, then scans enrollments once. Already lowest-cost plan.

### Correct Engineering Mindset

```
WRONG:  "I created an index — it MUST use it."

RIGHT:  "I created an index. Let's read the plan and understand the planner's choice."
```

The indexes WOULD be valuable in a selective query:

```sql
-- This query WOULD use the index:
EXPLAIN ANALYZE
SELECT s.name, c.name
FROM practice_schema.students s
JOIN practice_schema.enrollments e ON s.student_id = e.student_id
JOIN practice_schema.courses c ON e.course_id = c.course_id
WHERE s.student_id = 42;   -- selective filter
```

For this filtered query, PostgreSQL would likely switch to Index Scan + Nested Loop.

---

## Exercise 8 — EXPLAIN (ANALYZE, BUFFERS)

### Query

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT
  s.name AS student_name,
  c.name AS course_name
FROM practice_schema.students s
JOIN practice_schema.enrollments e
  ON s.student_id = e.student_id
JOIN practice_schema.courses c
  ON e.course_id = c.course_id;
```

### Output

```
 Hash Join  (cost=37.75..356.16 rows=13948 width=21) (actual time=0.182..3.488 rows=13948.00 loops=1)
   Hash Cond: (e.course_id = c.course_id)
   Buffers: shared hit=117
   ->  Hash Join  (cost=33.50..313.75 rows=13948 width=15) (actual time=0.154..2.143 rows=13948.00 loops=1)
         Hash Cond: (e.student_id = s.student_id)
         Buffers: shared hit=115
         ->  Seq Scan on enrollments e  (cost=0.00..243.48 rows=13948 width=8) (actual time=0.009..0.471 rows=13948.00 loops=1)
               Buffers: shared hit=104
         ->  Hash  (cost=21.00..21.00 rows=1000 width=15) (actual time=0.133..0.133 rows=1000.00 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 55kB
               Buffers: shared hit=11
               ->  Seq Scan on students s  (cost=0.00..21.00 rows=1000 width=15) (actual time=0.006..0.069 rows=1000.00 loops=1)
                     Buffers: shared hit=11
   ->  Hash  (cost=3.00..3.00 rows=100 width=14) (actual time=0.025..0.025 rows=100.00 loops=1)
         Buckets: 1024  Batches: 1  Memory Usage: 13kB
         Buffers: shared hit=2
         ->  Seq Scan on courses c  (cost=0.00..3.00 rows=100 width=14) (actual time=0.010..0.015 rows=100.00 loops=1)
               Buffers: shared hit=2
 Planning:
   Buffers: shared hit=253
 Planning Time: 0.881 ms
 Execution Time: 3.816 ms
(22 rows)
```

### Understanding the Three Layers

| Keyword | What it adds                                     |
|---------|--------------------------------------------------|
| EXPLAIN | The plan — what the planner decided to do        |
| ANALYZE | Actual execution — real time and row counts      |
| BUFFERS | I/O information — buffer cache usage             |

### Buffer Breakdown

| Node                  | shared hit | Meaning                                 |
|-----------------------|------------|-----------------------------------------|
| Seq Scan enrollments  | 104        | 104 pages read from shared buffer cache |
| Seq Scan students     | 11         | 11 pages from shared buffer cache       |
| Seq Scan courses      | 2          | 2 pages from shared buffer cache        |
| Total query           | 117        | No disk I/O — all data was cached       |
| Planning              | 253        | Catalog pages during plan construction  |

> shared hit = data was already in PostgreSQL's shared buffer pool (RAM). No disk I/O.
> shared read = pages had to be read from disk (cold cache or insufficient shared_buffers).

---

## Exercise 9 — Remove the Index Experiment

### Step 1: Drop idx_enrollments_student_id

```sql
DROP INDEX practice_schema.idx_enrollments_student_id;
```

### EXPLAIN ANALYZE — Without idx_enrollments_student_id

```
 Hash Join  (cost=37.75..356.16 rows=13948 width=21) (actual time=0.177..3.850 rows=13948.00 loops=1)
   Hash Cond: (e.course_id = c.course_id)
   Buffers: shared hit=117
   ->  Hash Join  (cost=33.50..313.75 rows=13948 width=15) (actual time=0.147..2.374 rows=13948.00 loops=1)
         Hash Cond: (e.student_id = s.student_id)
         Buffers: shared hit=115
         ->  Seq Scan on enrollments e  (cost=0.00..243.48 rows=13948 width=8) (actual time=0.005..0.505 rows=13948.00 loops=1)
               Buffers: shared hit=104
         ->  Hash  (cost=21.00..21.00 rows=1000 width=15) (actual time=0.132..0.132 rows=1000.00 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 55kB
               Buffers: shared hit=11
               ->  Seq Scan on students s  (cost=0.00..21.00 rows=1000 width=15) (actual time=0.005..0.066 rows=1000.00 loops=1)
                     Buffers: shared hit=11
   ->  Hash  (cost=3.00..3.00 rows=100 width=14) (actual time=0.027..0.028 rows=100.00 loops=1)
         Buckets: 1024  Batches: 1  Memory Usage: 13kB
         Buffers: shared hit=2
         ->  Seq Scan on courses c  (cost=0.00..3.00 rows=100 width=14) (actual time=0.009..0.016 rows=100.00 loops=1)
               Buffers: shared hit=2
 Planning:
   Buffers: shared hit=242 dirtied=2
 Planning Time: 0.755 ms
 Execution Time: 4.210 ms
```

### Step 2: Recreate idx_enrollments_student_id

```sql
CREATE INDEX idx_enrollments_student_id
ON practice_schema.enrollments(student_id);
```

### EXPLAIN ANALYZE — After Recreating Index

```
 Hash Join  (cost=37.75..356.16 rows=13948 width=21) (actual time=0.166..3.356 rows=13948.00 loops=1)
   Hash Cond: (e.course_id = c.course_id)
   Buffers: shared hit=117
   ->  Hash Join  (cost=33.50..313.75 rows=13948 width=15) (actual time=0.139..2.027 rows=13948.00 loops=1)
         Hash Cond: (e.student_id = s.student_id)
         Buffers: shared hit=115
         ->  Seq Scan on enrollments e  (cost=0.00..243.48 rows=13948 width=8) (actual time=0.004..0.371 rows=13948.00 loops=1)
               Buffers: shared hit=104
         ->  Hash  (cost=21.00..21.00 rows=1000 width=15) (actual time=0.130..0.130 rows=1000.00 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 55kB
               Buffers: shared hit=11
               ->  Seq Scan on students s  (cost=0.00..21.00 rows=1000 width=15) (actual time=0.006..0.067 rows=1000.00 loops=1)
                     Buffers: shared hit=11
   ->  Hash  (cost=3.00..3.00 rows=100 width=14) (actual time=0.023..0.023 rows=100.00 loops=1)
         Buckets: 1024  Batches: 1  Memory Usage: 13kB
         Buffers: shared hit=2
         ->  Seq Scan on courses c  (cost=0.00..3.00 rows=100 width=14) (actual time=0.008..0.015 rows=100.00 loops=1)
               Buffers: shared hit=2
 Planning:
   Buffers: shared hit=181 read=4
 Planning Time: 0.746 ms
 Execution Time: 3.673 ms
```

### Full Comparison Table

| Metric                    | No index (dropped)  | Index recreated    |
|---------------------------|---------------------|--------------------|
| Join strategy             | Hash Join           | Hash Join          |
| Scan — enrollments        | Seq Scan            | Seq Scan           |
| Scan — students           | Seq Scan            | Seq Scan           |
| Scan — courses            | Seq Scan            | Seq Scan           |
| Estimated rows            | 13,948              | 13,948             |
| Actual rows               | 13,948              | 13,948             |
| Total cost estimate       | 356.16              | 356.16             |
| Execution Time            | 4.210 ms            | 3.673 ms           |
| Buffers hit (query)       | 117                 | 117                |
| Planning dirtied          | 2 pages             | 0                  |

### Key Observation

The plan structure is identical in both cases (Hash Join + Seq Scan). However, there is a
minor execution time difference: 3.673 ms (with index) vs 4.210 ms (without). The improvement
is small here, but the indexes would significantly benefit selective, filtered queries.

---

## Exercise 10 — Repository Connection

### Question

> If tomorrow I add a get_students_with_courses() method to the Repository,
> where should performance investigation happen?

### Answer

Performance investigation belongs entirely in the database/query engineering workflow,
NOT inside application code.

### Correct Engineering Flow

```
Service layer
    |
    | calls
    v
Repository method: get_students_with_courses()
    |
    | executes
    v
SQL JOIN query
    |
    | runs on
    v
PostgreSQL
    |
    | investigated with
    v
EXPLAIN ANALYZE
    |
    | leads to
    v
Optimization (indexes, query rewrite, stats update)
```

### What Goes Where

| Location         | Responsibility                                                |
|------------------|---------------------------------------------------------------|
| Service layer    | Business logic only — call repository, handle result          |
| Repository method| SQL query definition — the JOIN/WHERE/ORDER BY logic          |
| DBA/Dev workflow | EXPLAIN ANALYZE investigation, index creation, tuning         |

### What the Service Should NOT Contain

```python
# WRONG — performance investigation does not belong here
class StudentService:
    async def get_students_with_courses(self):
        await db.execute("EXPLAIN ANALYZE SELECT ...")   # NO
```

```python
# CORRECT — service only calls repository
class StudentService:
    async def get_students_with_courses(self):
        return await self.student_repo.get_students_with_courses()
```

```python
# CORRECT — repository owns the SQL
class StudentRepository:
    async def get_students_with_courses(self):
        query = """
            SELECT s.name AS student_name, c.name AS course_name
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            JOIN courses c ON e.course_id = c.course_id
        """
        return await self.db.fetch_all(query)
```

The performance investigation is a separate engineering activity — run EXPLAIN ANALYZE
directly in psql or pgAdmin during development/tuning, not inside application code.

---

## Final State — Database Schema

### Indexes in practice_schema (after all exercises)

```
practice_schema.courses_pkey                -> courses(course_id)             [PK]
practice_schema.students_pkey               -> students(student_id)           [PK]
practice_schema.enrollments_pkey            -> enrollments(student_id, course_id) [PK]
practice_schema.idx_enrollments_student_id  -> enrollments(student_id)        [created Ex.6]
practice_schema.idx_enrollments_course_id   -> enrollments(course_id)         [created Ex.6]
```

### Row Counts (final)

| Table       | Rows   |
|-------------|--------|
| students    | 1,000  |
| courses     | 100    |
| enrollments | 13,948 |

---

## Summary of Key Learnings

| Concept                       | Takeaway                                                               |
|-------------------------------|------------------------------------------------------------------------|
| EXPLAIN                       | Shows the planner's estimated plan — no query execution                |
| EXPLAIN ANALYZE               | Runs the query and shows actual vs estimated metrics                   |
| EXPLAIN (ANALYZE, BUFFERS)    | Adds buffer/I/O stats — starting point for real perf investigation     |
| Seq Scan                      | Not inherently bad — optimal when returning many/all rows              |
| Hash Join                     | Preferred for large tables where both sides can be hashed into memory  |
| Index utility                 | Indexes help for selective queries, not full-table scans               |
| Estimation accuracy           | Run ANALYZE after bulk inserts to keep statistics fresh                |
| Planner trust                 | PostgreSQL makes cost-based decisions — trust them, then investigate   |
| Perf investigation layer      | Belongs at the SQL/DB level, not inside Service or Repository code     |
