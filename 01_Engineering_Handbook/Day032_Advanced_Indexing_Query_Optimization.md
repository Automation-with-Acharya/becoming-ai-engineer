# Day 032 — Advanced PostgreSQL Indexing & Query Optimization

## Learning Objectives

By the end of Day 32, you should be able to:

- Explain how PostgreSQL B-tree multicolumn indexes work.
- Explain the importance of leading/leftmost columns in a composite index.
- Understand selectivity and how it affects index usefulness.
- Explain why column order in a composite index is workload-dependent.
- Design and test partial indexes for a subset of rows.
- Compare index designs using `EXPLAIN (ANALYZE, BUFFERS)`.
- Recognize that indexes improve reads but add storage and write/update/delete overhead.
- Apply evidence-driven query optimization rather than creating indexes blindly.
- Keep query/index concerns inside the Repository layer of the existing Student Management architecture.

---

# 1. Big Picture

Day 22 introduced indexes and the difference between sequential scans and index-assisted access.

Day 30 introduced advanced SQL JOINs and relational query design.

Day 31 introduced query-performance analysis using `EXPLAIN`, `EXPLAIN ANALYZE`, execution plans, estimated versus actual rows, loops, execution time, and buffers.

Day 32 builds directly on those concepts.

The key progression is:

```text
SQL Query
   │
   ▼
PostgreSQL Planner
   │
   ├── Table Statistics
   │
   ├── Available Indexes
   │
   ├── Query Predicates
   │
   └── Cost Model
   │
   ▼
Chosen Execution Plan
   │
   ├── Seq Scan
   ├── Index Scan
   ├── Bitmap Scan
   └── Join / Aggregate / Sort operations
   │
   ▼
Measured Execution
   │
   └── EXPLAIN (ANALYZE, BUFFERS)
```

The engineering loop is therefore:

```text
Observe
  ↓
Measure
  ↓
Understand the workload
  ↓
Choose an index design
  ↓
Measure again
  ↓
Keep / change / remove the index
```

PostgreSQL explicitly treats indexes as a performance tool that also adds system overhead, so they should be used sensibly. [PostgreSQL 11.1](https://www.postgresql.org/docs/current/indexes.html) 

---

# 2. Composite / Multicolumn Indexes

A multicolumn index stores more than one key column in one index definition.

Example:

```sql
CREATE INDEX idx_students_city_age
ON students(city, age);
```

This is not equivalent to simply saying “there are two indexes.” It is one ordered index whose keys are built from the column sequence:

```text
(city, age)
```

PostgreSQL currently supports multicolumn indexes for B-tree, GiST, GIN, and BRIN index types, with behavior depending on the index type. [PostgreSQL 11.3](https://www.postgresql.org/docs/current/indexes-multicolumn.html)

For this day's experiments, the important case is the default B-tree index.

## 2.1 B-tree and the leftmost columns

For a B-tree multicolumn index, the leading columns matter most for determining which portion of the index can be efficiently scanned.

Consider:

```sql
CREATE INDEX idx_students_city_age
ON students(city, age);
```

The logical ordering is approximately:

```text
city
  ├── Ahmedabad
  │      ├── age 18
  │      ├── age 19
  │      ├── age 20
  │      └── ...
  ├── Mumbai
  │      ├── age 18
  │      ├── age 19
  │      └── ...
  └── Pune
         └── ...
```

A query constraining `city` can therefore narrow the index efficiently.

A query constraining both `city` and `age` can narrow it further.

PostgreSQL's current documentation states that a multicolumn B-tree index is most efficient when constraints exist on its leading columns. Equality conditions on leading columns, followed by an inequality on the first column without an equality constraint, determine the portion of the index that must be scanned; later-column conditions can still be checked while scanning. [PostgreSQL 11.3](https://www.postgresql.org/docs/current/indexes-multicolumn.html)

### Example

```sql
CREATE INDEX idx_students_city_age
ON students(city, age);
```

Good workload match:

```sql
SELECT *
FROM students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

Also potentially useful:

```sql
SELECT *
FROM students
WHERE city = 'Ahmedabad';
```

The planner has the leading `city` column available as an efficient restriction.

A query such as:

```sql
SELECT *
FROM students
WHERE age = 30;
```

does not have the conventional leading-column equality condition. PostgreSQL can sometimes use B-tree skip scan when its cost model predicts that repeated searches through distinct leading-column values are worthwhile, but this is workload- and data-dependent rather than something to assume automatically. [PostgreSQL 11.3](https://www.postgresql.org/docs/current/indexes-multicolumn.html)

---

# 3. Column Order Is a Workload Decision

A common misconception is:

> “Always put the most selective column first.”

That is too simplistic.

For a B-tree composite index, the best order depends on the actual query workload, predicates, cardinality, ordering needs, and how the planner can exploit the index.

Compare:

```sql
CREATE INDEX idx_students_city_age
ON students(city, age);
```

with:

```sql
CREATE INDEX idx_students_age_city
ON students(age, city);
```

The indexes represent different orderings and can produce different plans for different queries.

For a workload dominated by:

```sql
WHERE city = ? AND age = ?
```

both columns participate.

For a workload dominated by:

```sql
WHERE city = ?
```

`(city, age)` has the advantage of putting `city` in the leading position.

For a workload dominated by:

```sql
WHERE age = ?
```

`(age, city)` is naturally aligned with the leading predicate.

The correct engineering question is therefore not:

```text
Which column is “better”?
```

It is:

```text
Which index ordering best serves the actual workload?
```

---

# 4. Selectivity

## 4.1 Definition

Selectivity describes how narrowly a predicate identifies rows.

Conceptually:

```text
High selectivity
    ↓
Small fraction of rows match
    ↓
Index can potentially eliminate a lot of work
```

Whereas:

```text
Low selectivity
    ↓
Large fraction of rows match
    ↓
Index may provide little benefit
```

Example with one million rows:

```text
city = 'Ahmedabad'
→ 400,000 matching rows
→ relatively weak filtering
```

versus:

```text
email = 'some.unique@email.com'
→ 1 matching row
→ highly selective
```

Selectivity is not a static label that automatically tells PostgreSQL what to do. The planner uses statistics and its cost model to estimate the usefulness of candidate plans.

This is why a query can legitimately use a sequential scan even when an index exists.

---

# 5. Sequential Scan Is Not Automatically Bad

The goal is not:

```text
Make PostgreSQL use an index
```

The goal is:

```text
Make PostgreSQL choose an efficient plan for the workload
```

Suppose a query returns a very large fraction of a table:

```sql
SELECT *
FROM students
WHERE city IS NOT NULL;
```

Walking an index and then visiting a huge number of table rows may be more expensive than reading the table sequentially.

Therefore:

```text
Index exists
      ≠
Index must be used
```

This principle is central to query optimization.

PostgreSQL's planner evaluates candidate plans using estimated costs; `EXPLAIN` exposes the chosen plan and its estimated cost values. [PostgreSQL 14.1](https://www.postgresql.org/docs/current/using-explain.html)

---

# 6. Partial Indexes

A partial index is an index over only a subset of a table.

The subset is defined using a predicate.

Example:

```sql
CREATE INDEX idx_students_active_email
ON students(email)
WHERE is_active = true;
```

Conceptually:

```text
students table
│
├── active rows      → included in index
│
└── inactive rows    → not included in index
```

This can make the index smaller than a full-table index when the predicate matches a useful subset of the workload.

PostgreSQL documents partial indexes as a specialized feature that can be useful when common rows do not benefit from being indexed, reducing index size and potentially reducing index maintenance work. [PostgreSQL 11.8](https://www.postgresql.org/docs/current/indexes-partial.html)

## 6.1 Matching predicates matter

Given:

```sql
CREATE INDEX idx_students_active_email
ON students(email)
WHERE is_active = true;
```

A query such as:

```sql
SELECT *
FROM students
WHERE is_active = true
  AND email = 'student@example.com';
```

matches the partial-index predicate directly.

The intended idea is:

```text
The query needs active students
          ↓
The index contains only active students
          ↓
The index can avoid entries for irrelevant rows
```

A query that does not establish the predicate may not be able to safely use the partial index for the same purpose.

---

# 7. Index Design Trade-offs

Indexes are not free.

## Read benefit

```text
Query
  ↓
Index
  ↓
Fewer candidate rows/pages
  ↓
Potentially lower execution cost
```

## Write/maintenance cost

```text
INSERT / UPDATE / DELETE
        ↓
Table changes
        ↓
Relevant index entries may also change
        ↓
Additional work + storage
```

Therefore, excessive indexing can create its own performance problem.

A useful engineering rule is:

> Index based on actual workload evidence, not because an indexed column “looks important.”

The PostgreSQL documentation explicitly notes that indexes add overhead to the overall database system. [PostgreSQL 11.1](https://www.postgresql.org/docs/current/indexes.html)

---

# 8. Day 32 Practical Experiment

The practical exercise uses the large Student Management dataset created during the earlier query-performance work.

The intended query is:

```sql
SELECT *
FROM students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

The experiment should be performed with:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

The objective is to observe how the plan changes as index options are introduced.

---

# 9. Experiment 1 — Baseline

Start with no experimental indexes covering the target predicates.

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

Record at minimum:

```text
Plan node(s)
Estimated rows
Actual rows
Execution time
Buffers
```

Possible outcome:

```text
Seq Scan on students
```

That is not a failure. It is the baseline against which the index experiments are compared.

---

# 10. Experiment 2 — Single-Column City Index

Create:

```sql
CREATE INDEX idx_students_city
ON students(city);
```

Then rerun:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

Questions to answer:

```text
Did the planner use the index?
Did execution time change?
Did buffer activity change?
How many rows were estimated?
How many rows actually matched?
```

---

# 11. Experiment 3 — Add an Age Index

Create:

```sql
CREATE INDEX idx_students_age
ON students(age);
```

Run the same query again.

Now the planner has more choices.

Depending on data distribution and cost estimates, PostgreSQL may choose one index, combine access paths, or continue with a sequential scan.

The important lesson is:

```text
Creating another index does not force a particular plan.
```

The planner still chooses what it estimates to be cheapest.

---

# 12. Experiment 4 — Composite Index `(city, age)`

Create:

```sql
CREATE INDEX idx_students_city_age
ON students(city, age);
```

Then measure:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

This index directly represents the conjunction of the two equality predicates.

Conceptually:

```text
WHERE city = X AND age = Y
          ↓
(city, age) B-tree index
          ↓
Narrower relevant index region
```

Compare this result to the single-column experiments.

---

# 13. Experiment 5 — Reverse Composite Order

Create:

```sql
CREATE INDEX idx_students_age_city
ON students(age, city);
```

Rerun the same query:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

For this exact equality/equality query, both column orders can potentially serve the predicate set. The more interesting question is what happens for additional workload shapes.

For example:

```sql
SELECT *
FROM students
WHERE city = 'Ahmedabad';
```

versus:

```sql
SELECT *
FROM students
WHERE age = 30;
```

The leading-column behavior becomes important.

---

# 14. Experiment 6 — Partial Index

Create:

```sql
CREATE INDEX idx_students_active_email
ON students(email)
WHERE is_active = true;
```

Then test the matching workload:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM students
WHERE is_active = true
  AND email = 'student@example.com';
```

Then compare it with a query that does not constrain `is_active`:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM students
WHERE email = 'student@example.com';
```

The purpose is to reason about when PostgreSQL can prove that the partial index's predicate is relevant to the query.

---

# 15. Comparing Results Scientifically

Do not judge an index only by whether the output changed from:

```text
Seq Scan
```

to:

```text
Index Scan
```

Record evidence instead.

Suggested comparison table:

| Experiment | Index | Plan | Estimated Rows | Actual Rows | Execution Time | Buffers | Observation |
|---|---|---|---:|---:|---:|---:|---|
| Baseline | None | ... | ... | ... | ... | ... | ... |
| City | `(city)` | ... | ... | ... | ... | ... | ... |
| City + Age | `(city, age)` | ... | ... | ... | ... | ... | ... |
| Age + City | `(age, city)` | ... | ... | ... | ... | ... | ... |
| Partial | `(email) WHERE is_active` | ... | ... | ... | ... | ... | ... |

This is the core habit of performance engineering:

```text
Hypothesis
   ↓
Controlled change
   ↓
Measure
   ↓
Compare
   ↓
Decide
```

---

# 16. Understanding EXPLAIN Again

Day 31 established the execution-plan mindset. Day 32 uses the same measurement framework for index design.

The basic form:

```sql
EXPLAIN
SELECT ...;
```

shows the planner's chosen execution plan without actually executing the statement.

The more useful experiment form:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

actually executes the statement and shows measured runtime/row information together with buffer information. PostgreSQL's documentation describes `ANALYZE` as executing the query and comparing actual row counts and runtime with planner estimates. `BUFFERS` exposes I/O-related buffer activity. [PostgreSQL 14.1](https://www.postgresql.org/docs/current/using-explain.html)

### Key fields to inspect

```text
cost=START..TOTAL
rows=ESTIMATE
actual time=START..END
actual rows=MEASURED
loops=N
Buffers: shared hit/read/...
```

The most valuable comparison is often:

```text
Estimated rows
      vs
Actual rows
```

Large discrepancies can signal that planner statistics or data distribution assumptions are not matching reality.

---

# 17. Statistics and `ANALYZE`

The PostgreSQL planner depends on statistics about the data.

After substantial changes to a test dataset, refreshing statistics is useful:

```sql
ANALYZE students;
```

Then rerun:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

The objective is not to memorize `ANALYZE` as a magic optimization command.

The engineering model is:

```text
Data distribution changes
        ↓
Planner statistics may need refreshing
        ↓
Planner estimates become more representative
        ↓
Plan selection can improve
```

---

# 18. Repository-Layer Mapping

The existing Student Management architecture is:

```text
Client
   ↓
FastAPI Router
   ↓
Service
   ↓
Repository
   ↓
Database Helper
   ↓
Connection Pool
   ↓
PostgreSQL
```

A performance-oriented repository method might look conceptually like:

```python
def search_students(city: str, age: int):
    ...
```

The SQL and index assumptions remain inside the data-access boundary.

For example, the Repository can own a query such as:

```sql
SELECT id, name, email, city, age
FROM students
WHERE city = %s
  AND age = %s;
```

The Service layer should not know whether PostgreSQL answers the query using:

```text
Seq Scan
Index Scan
Bitmap Heap Scan
Composite index
Partial index
```

That is an implementation concern of the persistence layer.

This preserves the existing architecture:

```text
Business intent
      ↓
Service
      ↓
Repository abstraction
      ↓
SQL + Index strategy
      ↓
PostgreSQL
```

---

# 19. Production Best Practices

## 19.1 Index workload, not every column

Avoid creating indexes just because a column appears in a table.

Start from real queries and access patterns.

## 19.2 Use `EXPLAIN` before guessing

The planner may already be making a better choice than expected.

## 19.3 Use `EXPLAIN (ANALYZE, BUFFERS)` for measured experiments

This provides evidence about actual execution rather than relying only on intuition.

## 19.4 Reconsider column order

Composite index order should follow actual query patterns.

## 19.5 Keep indexes maintainable

Every additional index can add storage and write/update/delete maintenance cost.

## 19.6 Consider partial indexes for real subsets

A partial index is most useful when a meaningful subset of rows repeatedly appears in the workload.

## 19.7 Measure after every important index change

Never assume an index is beneficial just because it sounds theoretically appropriate.

---

# 20. Common Mistakes

### Mistake 1 — “More indexes always means faster queries”

Wrong.

Indexes improve some reads while increasing storage and maintenance overhead.

### Mistake 2 — “Every query should use an index”

Wrong.

Sequential scans can be the best plan when a large fraction of the table is needed.

### Mistake 3 — “Most selective column must always come first”

Too simplistic.

Composite index order is a workload and access-pattern decision.

### Mistake 4 — Creating `(city, age)` and assuming it behaves like two independent indexes

It does not.

It is one ordered multicolumn index with important leading-column behavior.

### Mistake 5 — Looking only at execution time

One timing sample is not enough to understand the plan.

Inspect:

```text
Plan
Estimated rows
Actual rows
Loops
Buffers
Execution time
```

### Mistake 6 — Optimizing without a baseline

Without a baseline, you cannot establish whether the change helped.

### Mistake 7 — Mixing experiments into production indexes

Performance experiments should be isolated where practical so that learning does not alter the production application's intended schema.

---

# 21. Troubleshooting Checklist

When an expected index is not used:

```text
1. Inspect the exact query predicate.
2. Check the index definition.
3. Check column order.
4. Check data distribution/selectivity.
5. Check estimated vs actual rows.
6. Run ANALYZE when appropriate.
7. Inspect the full execution plan.
8. Compare the planner's chosen cost against alternatives.
```

Remember:

```text
“No Index Scan”
        ≠
“PostgreSQL is broken”
```

It may simply mean that the planner estimates another path to be cheaper.

---

# 22. Enterprise Mapping

These concepts become important as systems grow because query patterns and data distributions evolve.

### Application architecture

```text
API Endpoint
    ↓
Service
    ↓
Repository
    ↓
Parameterized SQL
    ↓
PostgreSQL Planner
    ↓
Index Strategy
    ↓
Storage / Buffer / CPU Work
```

### Example production scenario

Suppose an enterprise Student/Customer table grows from:

```text
10,000 rows
```

to:

```text
10,000,000 rows
```

A query that was previously fast with a sequential scan may become a candidate for a carefully designed index.

But the correct process remains:

```text
Real workload
   ↓
Measure
   ↓
EXPLAIN
   ↓
Index hypothesis
   ↓
Controlled change
   ↓
Benchmark
   ↓
Production decision
```

This is the bridge from “knowing SQL” to “engineering database performance.”

---

# 23. Interview Questions

### Q1. What is a composite index?

An index whose key consists of multiple columns, for example:

```sql
CREATE INDEX idx_students_city_age
ON students(city, age);
```

### Q2. Why does column order matter in a B-tree composite index?

Because the index has an ordered key structure. Leading columns are especially important for narrowing the portion of the index scanned.

### Q3. Can PostgreSQL use a `(city, age)` index for `WHERE age = 30`?

Do not assume a conventional leftmost-column lookup. PostgreSQL can sometimes use B-tree skip scan when the planner expects it to be worthwhile, but this is conditional and data-dependent.

### Q4. What is selectivity?

The degree to which a predicate narrows the set of matching rows. More selective predicates generally eliminate more candidate rows.

### Q5. Why might PostgreSQL choose a sequential scan even when an index exists?

Because the planner may estimate that reading a large portion of the table through the index is more expensive than scanning the table sequentially.

### Q6. What is a partial index?

An index that covers only rows satisfying a predicate:

```sql
CREATE INDEX idx_students_active_email
ON students(email)
WHERE is_active = true;
```

### Q7. Why are indexes not free?

They consume storage and can add work during insert/update/delete operations.

### Q8. What is the difference between `EXPLAIN` and `EXPLAIN ANALYZE`?

`EXPLAIN` shows the planner's chosen execution plan. `EXPLAIN ANALYZE` executes the statement and reports actual execution measurements alongside estimates.

### Q9. What does `BUFFERS` tell you?

It provides additional information about buffer activity during execution, helping investigate I/O behavior.

### Q10. How would you decide whether a new index is worthwhile in production?

Use a real workload query, establish a baseline, inspect the plan, create the candidate index in a controlled environment, rerun measurements, compare execution behavior and maintenance/storage trade-offs, then make a workload-backed decision.

---

# 24. Cheat Sheet

```text
COMPOSITE INDEX
CREATE INDEX ... ON table(col1, col2);

LEFTMOST / LEADING COLUMN
Important for efficient B-tree index restriction.

SELECTIVITY
How strongly a predicate narrows matching rows.

PARTIAL INDEX
CREATE INDEX ... ON table(col) WHERE predicate;

BASELINE
EXPLAIN (ANALYZE, BUFFERS) ...;

STATISTICS
ANALYZE table;

KEY METRICS
cost
estimated rows
actual rows
loops
execution time
buffers

CORE RULE
Do not optimize from intuition alone.
Measure → change → measure again.

ARCHITECTURE RULE
Keep SQL/index strategy inside the Repository/persistence boundary.
```

---

# 25. Final Mental Model

Think of PostgreSQL optimization as a planner making an evidence-based decision.

```text
                   ┌──────────────────────┐
                   │      SQL Query       │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   PostgreSQL Planner │
                   └──────────┬───────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
      Statistics           Indexes            Query Shape
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                       Chosen Plan
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
            Seq Scan      Index Scan   Bitmap / Join...
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                   EXPLAIN ANALYZE + BUFFERS
                              │
                              ▼
                         Evidence
                              │
                              ▼
                       Better Decision
```

The mature database engineer does not think:

```text
“I need an index.”
```

The mature database engineer thinks:

```text
“What workload is slow?”
        ↓
“What does the plan do?”
        ↓
“Why is PostgreSQL choosing that plan?”
        ↓
“What index/query/statistics change could improve it?”
        ↓
“Can I prove the change helped?”
```

That mindset is the real objective of Day 32.

---

# 26. Revision Checklist

Before marking Day 32 fully understood, verify that you can explain each without notes:

- [ ] What a composite/multicolumn index is.
- [ ] Why `(city, age)` and `(age, city)` are different index designs.
- [ ] What “leading/leftmost column” means for a B-tree index.
- [ ] What selectivity means.
- [ ] Why a sequential scan can be the correct plan.
- [ ] What a partial index is.
- [ ] Why partial-index predicates matter to query planning.
- [ ] Why indexes have write and storage costs.
- [ ] How to compare an index experiment using `EXPLAIN (ANALYZE, BUFFERS)`.
- [ ] Why estimated versus actual rows matter.
- [ ] Why `ANALYZE` can matter after significant data changes.
- [ ] Why SQL and index strategy belong inside the Repository layer rather than the Service layer.

---

# 27. Exact Resources Used

## Official PostgreSQL Documentation

### PostgreSQL 11.1 — Introduction to Indexes
https://www.postgresql.org/docs/current/indexes.html

Focus:
- Section `11.1 Introduction`
- General index benefits and overhead

### PostgreSQL 11.3 — Multicolumn Indexes
https://www.postgresql.org/docs/current/indexes-multicolumn.html

Focus:
- Section `11.3 Multicolumn Indexes`
- B-tree leading/leftmost columns
- Equality and inequality behavior
- Skip scan behavior
- Multicolumn index design guidance

### PostgreSQL 11.8 — Partial Indexes
https://www.postgresql.org/docs/current/indexes-partial.html

Focus:
- Section `11.8 Partial Indexes`
- Partial-index predicates
- Reduced index size
- Workload-specific use cases

### PostgreSQL 14.1 — Using EXPLAIN
https://www.postgresql.org/docs/current/using-explain.html

Focus:
- `14.1.1 EXPLAIN Basics`
- `14.1.2 EXPLAIN ANALYZE`
- Plan nodes
- Estimated versus actual rows
- Costs
- Buffers

### PostgreSQL EXPLAIN Command Reference
https://www.postgresql.org/docs/current/sql-explain.html

Focus:
- `ANALYZE`
- `BUFFERS`
- Cost and plan output

---

# 28. Day 32 Completion Criteria

Day 32 is complete when you can demonstrate all of the following:

```text
✓ Explain composite indexes
✓ Explain leftmost-column behavior
✓ Explain selectivity
✓ Explain column-order trade-offs
✓ Explain partial indexes
✓ Compare index strategies with EXPLAIN ANALYZE
✓ Interpret estimated vs actual rows
✓ Interpret buffer information
✓ Explain index read benefits vs write/storage costs
✓ Keep performance logic within the Repository/persistence layer
```

## Core Takeaway

```text
Indexing is not about creating more indexes.

Indexing is about designing the right access paths
for real query workloads,
then proving their value with measurements.
```
