# Day 031 — SQL Query Performance: EXPLAIN, EXPLAIN ANALYZE & JOIN Execution Plans

**Project ₹50L — Engineering Handbook**  
**Date:** 02 September 2026

---

## Learning Objectives

By the end of Day 31, the goal is to be able to:

1. Explain what PostgreSQL's query planner does and why execution plans exist.
2. Read a PostgreSQL `EXPLAIN` plan as a tree rather than as a wall of text.
3. Distinguish estimated planning information from actual execution information.
4. Understand `Seq Scan`, `Index Scan`, and other scan strategies at a practical level.
5. Recognize the three major join strategies: `Nested Loop`, `Hash Join`, and `Merge Join`.
6. Use `EXPLAIN ANALYZE` to compare planner estimates with what actually happened.
7. Use `EXPLAIN (ANALYZE, BUFFERS)` to investigate I/O behavior.
8. Understand why adding an index does **not** guarantee that PostgreSQL will use it.
9. Connect repository-layer SQL to database-level performance investigation.
10. Develop the production habit of **measure → understand → change → measure again**.

---

# 1. Big Picture — SQL Is a Request, Not an Execution Plan

When we write SQL such as:

```sql
SELECT
    s.name,
    c.name AS course_name
FROM students s
JOIN enrollments e
    ON e.student_id = s.id
JOIN courses c
    ON c.id = e.course_id
WHERE s.id = 42;
```

we describe **what** data we want.

We do not explicitly tell PostgreSQL:

- which table to access first,
- whether to scan every row or use an index,
- which join algorithm to use,
- which join should happen first,
- how much memory or I/O may be required,
- or the physical path through the tables.

PostgreSQL's planner/optimizer evaluates possible execution strategies and selects a plan it estimates to be efficient.

```text
                    SQL Query
                        |
                        v
                +----------------+
                | Query Planner  |
                | / Optimizer    |
                +----------------+
                        |
              chooses execution plan
                        |
                        v
              +---------------------+
              | Execution Plan      |
              | Scan + Join + Sort  |
              +---------------------+
                        |
                        v
                 Query Execution
                        |
                        v
                     Results
```

### The key shift in thinking

SQL development asks:

> “What data do I need?”

Database engineering also asks:

> “How will the database obtain that data, and what will it cost?”

That second question is the reason `EXPLAIN` matters.

---

# 2. Why Does `EXPLAIN` Exist?

A query can be logically correct and still be operationally poor.

For example:

```sql
SELECT *
FROM students
WHERE email = 'student42@example.com';
```

If PostgreSQL scans 2.5 million rows to find one student, the query may produce the correct answer while wasting significant work.

`EXPLAIN` lets us inspect the strategy PostgreSQL intends to use.

Conceptually:

```text
SQL
 |
 |  “Tell me how you would execute this.”
 v
EXPLAIN
 |
 v
Execution Plan
 |
 +--> Scan strategy
 +--> Join strategy
 +--> estimated rows
 +--> estimated costs
 +--> plan tree
```

This is a debugging and engineering tool, not something we add to normal application SQL in production.

---

# 3. The Day 31 Lab Schema

Day 31 builds directly on the isolated `day030_joins` practice schema from Day 30.

The logical model is:

```text
+----------------+
|    students    |
+----------------+
| id (PK)        |
| name           |
| email          |
+--------+-------+
         |
         | 1:N
         v
+----------------+
|  enrollments   |
+----------------+
| id (PK)        |
| student_id FK  |
| course_id FK   |
+--------+-------+
         |
         | N:1
         v
+----------------+
|    courses     |
+----------------+
| id (PK)        |
| name           |
+----------------+
```

The many-to-many relationship is represented through `enrollments`:

```text
Students  1 ----< Enrollments >---- 1  Courses
```

The same schema is useful for Day 31 because query performance becomes easier to understand when we can see scan and join choices over multiple tables.

---

# 4. Reading `EXPLAIN` as a Tree

A PostgreSQL execution plan is easiest to understand from the **bottom upward**.

Consider a conceptual plan:

```text
Hash Join
  Hash Cond: (...)
  |
  +---- Seq Scan on students
  |
  +---- Hash
          |
          +---- Seq Scan on enrollments
```

Think of it as:

```text
Leaf operations
      |
      v
Build/intermediate operations
      |
      v
Join/aggregation/sort
      |
      v
Final result
```

### Important mental model

The top node is generally the final operation producing the query's result.

The child nodes provide the inputs needed by the parent node.

So when reading a plan:

1. Start at the top to identify the overall operation.
2. Walk down through each child.
3. Reach the leaf scan nodes.
4. Then mentally reconstruct the execution from the leaves upward.

---

# 5. Estimated Cost vs Actual Work

A normal `EXPLAIN` gives the planner's estimates.

A simplified example:

```text
Index Scan using students_pkey on students
  (cost=0.29..8.30 rows=1 width=40)
```

The important concepts are:

- `cost=` — planner's estimated cost range.
- `rows=` — estimated number of rows produced by the node.
- `width=` — estimated average row width in bytes.

The cost is **not elapsed milliseconds**.

It is a planner cost unit used to compare candidate plans under PostgreSQL's cost model.

This distinction is critical in interviews and production debugging.

---

# 6. `EXPLAIN ANALYZE` — What Actually Happened?

`EXPLAIN ANALYZE` executes the query and adds actual runtime information.

Example shape:

```sql
EXPLAIN ANALYZE
SELECT *
FROM students
WHERE email = 'student42@example.com';
```

The output can include information such as:

```text
(actual time=0.020..0.021 rows=1 loops=1)
```

This lets us compare:

```text
Planner Estimate        Reality
----------------        -------
estimated rows  = 1     actual rows = 1
estimated rows  = 10    actual rows = 500
estimated cost  = ...   actual time = ...
```

### Why this matters

A large mismatch between estimated and actual rows can indicate that the planner's assumptions are poor.

For example:

```text
Estimated rows: 10
Actual rows:    500,000
```

That discrepancy can lead to an inefficient plan choice because the planner selected a strategy using incorrect expectations about the amount of data involved.

### Critical safety point

`EXPLAIN ANALYZE` actually runs the statement.

Therefore:

```sql
EXPLAIN ANALYZE SELECT ...;
```

is normally safe for a read-only query, but:

```sql
EXPLAIN ANALYZE DELETE ...;
```

can actually execute the `DELETE`.

For modifying statements, understand the risk before using `ANALYZE`.

---

# 7. Scan Strategies

The first major category to recognize is how PostgreSQL obtains rows from a table.

## 7.1 Sequential Scan

```text
Seq Scan on students
```

Conceptually:

```text
Table
 |
 +-- row 1 -> check predicate
 +-- row 2 -> check predicate
 +-- row 3 -> check predicate
 +-- ...
 +-- row N -> check predicate
```

A sequential scan reads the table sequentially and evaluates the filter.

A sequential scan is **not automatically bad**.

For a large portion of a table, reading the table sequentially may be cheaper than repeatedly navigating an index and then fetching many heap rows.

This is one of the most important lessons of the day:

> “Seq Scan” is not synonymous with “slow.”

---

## 7.2 Index Scan

Conceptually:

```text
Query predicate
      |
      v
   Index
      |
      v
matching row locations
      |
      v
   Table rows
```

Example shape:

```text
Index Scan using students_email_idx on students
```

An index is especially useful when the query is selective enough that PostgreSQL can avoid reading a large fraction of the table.

For example, finding one exact email in a large table is a natural indexing candidate.

---

## 7.3 Bitmap Scan — Awareness Level

PostgreSQL may also use bitmap access strategies, especially when a condition matches multiple rows.

The important Day 31 takeaway is not memorizing every detail, but recognizing that the planner has multiple access strategies and chooses among them based on estimated cost.

Think:

```text
Predicate
   |
   v
Index information
   |
   v
Bitmap of matching locations
   |
   v
Heap/table access
```

---

# 8. Join Strategies

Day 30 focused on writing JOIN queries.

Day 31 adds the next layer:

> PostgreSQL must decide **how** to physically perform the JOIN.

The main strategies are:

1. Nested Loop Join
2. Hash Join
3. Merge Join

---

# 9. Nested Loop Join

Conceptually:

```text
Outer input
  |
  +---- row A ----> search matching rows in inner input
  |
  +---- row B ----> search matching rows in inner input
  |
  +---- row C ----> search matching rows in inner input
```

Pseudocode:

```text
for each row in outer input:
    find matching rows in inner input
```

Nested loops can be excellent when the outer relation is small and the inner side can be searched efficiently, often with an index.

For example:

```text
Small number of students
          |
          v
Nested Loop
          |
          +--> Index lookup into enrollments
```

But a nested loop can become expensive when both inputs are large and the inner operation is repeated many times.

### Engineering intuition

```text
Small outer set + cheap indexed lookup
                = potentially excellent

Large outer set + expensive repeated lookup
                = potentially disastrous
```

---

# 10. Hash Join

Hash joins are designed for equality-style joins and often make sense for larger inputs.

Conceptually:

```text
Build side
   |
   v
+--------+
| Hash   |
| Table  |
+--------+
     |
     | probe
     v
Other input
     |
     v
Matching rows
```

Simplified execution model:

```text
1. Read one input.
2. Build an in-memory hash structure from the join key.
3. Read the other input.
4. Probe the hash table for matches.
```

Typical shape:

```text
Hash Join
  Hash Cond: (e.student_id = s.id)
```

Again, the planner makes this choice based on estimated costs and statistics.

---

# 11. Merge Join

A merge join works effectively when both inputs can be presented in matching sort order.

Conceptually:

```text
Input A:  1  3  5  7  9
          |
          | scan together
          v
Input B:  1  2  5  8  9

Matches:  1     5        9
```

The important high-level idea is:

> Walk two ordered inputs together and match equal join keys.

It can be attractive when appropriate ordering already exists or can be obtained efficiently.

---

# 12. Why PostgreSQL May Choose Different JOINs

Suppose the query is:

```sql
SELECT
    s.name,
    c.name
FROM students s
JOIN enrollments e
    ON e.student_id = s.id
JOIN courses c
    ON c.id = e.course_id;
```

PostgreSQL has more than one possible physical strategy.

Conceptually:

```text
                    JOIN
                     |
        +------------+------------+
        |            |            |
   Nested Loop    Hash Join   Merge Join
        |            |            |
      cost         cost         cost
        |            |            |
        +------------+------------+
                     |
              lowest estimated
                   cost
                     |
                     v
             selected plan
```

The query remains logically the same.

The execution strategy can change based on:

- table size,
- available indexes,
- estimated selectivity,
- statistics,
- row-count estimates,
- data distribution,
- configuration and planner cost assumptions.

---

# 13. The Most Important Indexing Lesson of Day 31

Adding an index does **not** mean PostgreSQL must use it.

Suppose we create:

```sql
CREATE INDEX idx_enrollments_student_id
ON enrollments(student_id);
```

We might expect:

```text
Index exists
    |
    v
Index Scan
```

But PostgreSQL may still choose:

```text
Seq Scan
```

That is perfectly valid if the planner estimates that reading the table directly is cheaper.

For example, if a query needs 80% of the table's rows, using the index may mean:

```text
Index lookup
      |
      v
Many row locations
      |
      v
Many table page accesses
```

A sequential pass may be cheaper:

```text
Table
 |
 +-- page 1
 +-- page 2
 +-- page 3
 +-- ...
```

So the correct mindset is:

> Indexes provide options to the planner. They do not command the planner.

---

# 14. Day 31 Experiment — Baseline JOIN Plan

Start with the Day 30 schema and inspect a representative three-table query.

Example:

```sql
EXPLAIN
SELECT
    s.name AS student_name,
    c.name AS course_name
FROM students s
JOIN enrollments e
    ON e.student_id = s.id
JOIN courses c
    ON c.id = e.course_id;
```

### What to inspect

Do not try to understand every field immediately.

First answer these questions:

```text
1. What is the top-level operation?
2. How many joins are present?
3. Which scan is used for students?
4. Which scan is used for enrollments?
5. Which scan is used for courses?
6. Which join strategy is being used?
7. What rows does PostgreSQL estimate at each major node?
```

The purpose of the experiment is to learn to **read the plan tree**.

---

# 15. Day 31 Experiment — `EXPLAIN ANALYZE`

Next:

```sql
EXPLAIN ANALYZE
SELECT
    s.name AS student_name,
    c.name AS course_name
FROM students s
JOIN enrollments e
    ON e.student_id = s.id
JOIN courses c
    ON c.id = e.course_id;
```

Compare the estimates with the actual values.

Build the habit of asking:

```text
Planner thought:
    “I expect about N rows.”

Reality:
    “I actually processed M rows.”

Question:
    Is N reasonably close to M?
```

That is far more valuable than simply seeing “the query took X ms.”

---

# 16. Day 31 Experiment — Add Data, Then Measure Again

Use a moderate dataset for learning rather than spending the entire session generating millions of rows.

A useful practice scale is approximately:

```text
students      ~1,000
courses       ~100
enrollments   ~5,000
```

Then repeat:

```text
EXPLAIN
   |
   v
EXPLAIN ANALYZE
   |
   v
Compare estimated rows vs actual rows
```

The goal is to see how plan decisions depend on the shape of the data.

---

# 17. Day 31 Experiment — Add JOIN Indexes

Create indexes aligned with the foreign-key join columns used in the experiment:

```sql
CREATE INDEX idx_enrollments_student_id
ON enrollments(student_id);

CREATE INDEX idx_enrollments_course_id
ON enrollments(course_id);
```

Then run the same query again:

```sql
EXPLAIN ANALYZE
SELECT
    s.name AS student_name,
    c.name AS course_name
FROM students s
JOIN enrollments e
    ON e.student_id = s.id
JOIN courses c
    ON c.id = e.course_id;
```

### The important experiment question

Do **not** ask:

> “Did PostgreSQL use my new indexes?”

Ask:

> “Why did PostgreSQL choose this plan given the available options?”

If it still chooses sequential scans, that becomes part of the lesson rather than a failed experiment.

---

# 18. `EXPLAIN (ANALYZE, BUFFERS)`

For deeper investigation:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    s.name AS student_name,
    c.name AS course_name
FROM students s
JOIN enrollments e
    ON e.student_id = s.id
JOIN courses c
    ON c.id = e.course_id;
```

`BUFFERS` adds information about buffer activity during execution.

At a practical level, this helps answer questions such as:

```text
Is this query doing substantial shared buffer reads?
Is the operation mostly served from shared buffers?
Which node appears to be responsible for the work?
```

For production troubleshooting, this moves us from a simple “plan shape” view toward a more concrete view of database work.

---

# 19. Deliberately Remove an Index and Compare

A useful engineering experiment is to compare the plan before and after an index change.

For example:

```sql
DROP INDEX IF EXISTS idx_enrollments_student_id;
```

Then run the same `EXPLAIN ANALYZE` query again.

Record:

```text
Plan before change
Plan after change
Estimated rows
Actual rows
Join strategy
Scan strategy
Execution time
Buffer information
```

The key lesson is not that “indexes are always faster.”

The lesson is:

> A performance change should be demonstrated by measurements before and after the change.

---

# 20. SQL Performance Debugging Loop

This is the Day 31 production habit to carry forward.

```text
             Slow / suspicious query
                       |
                       v
                 Reproduce safely
                       |
                       v
                    EXPLAIN
                       |
                       v
               Read plan structure
                       |
                       v
                 EXPLAIN ANALYZE
                       |
                       v
          Compare estimates vs actuals
                       |
                       v
              Identify likely cause
                       |
               +-------+-------+
               |               |
          Query design      Missing / poor
          issue?             access path?
               |               |
               +-------+-------+
                       |
                       v
                 Make one change
                       |
                       v
                    Measure
                       |
                       v
                  Improvement?
                  /         \
                Yes          No
                 |             |
                 v             v
              Keep it      Reconsider
```

Never jump straight from:

> “This query feels slow.”

to:

> “Add an index.”

The database should be measured first.

---

# 21. Enterprise Connection — Repository Layer to PostgreSQL

From the Clean Architecture work on Day 9, the repository layer hides SQL from higher layers.

The conceptual request path remains:

```text
HTTP Request
     |
     v
API / Router
     |
     v
Service Layer
     |
     v
Repository
     |
     v
SQL Query
     |
     v
PostgreSQL
     |
     v
Execution Plan
     |
     v
Rows / Result
```

Suppose we later add a repository operation:

```python
class StudentRepository:
    def get_students_with_courses(self):
        ...
```

The repository might issue a JOIN similar to:

```sql
SELECT
    s.id,
    s.name,
    c.name AS course_name
FROM students s
JOIN enrollments e
    ON e.student_id = s.id
JOIN courses c
    ON c.id = e.course_id;
```

If this becomes slow at scale, the repository is where the SQL is represented in the application, but the **database execution plan** is where we investigate the physical work.

### Architectural rule

Do not put database optimizer logic such as `EXPLAIN` into the service layer just because the query is slow.

Instead:

```text
Application behavior
        |
        v
Repository owns SQL
        |
        v
Database owns execution
        |
        v
EXPLAIN helps engineers inspect execution
```

---

# 22. Enterprise Comparison — PostgreSQL ↔ ASP.NET Core / SQL Server Mindset

The exact syntax and plan output differ between database engines, but the engineering concept transfers.

| Concept | PostgreSQL | Typical Enterprise .NET / SQL Server Context |
|---|---|---|
| Query planner | PostgreSQL planner | SQL Server optimizer |
| Inspect plan | `EXPLAIN` | Estimated/Actual Execution Plan |
| Execute + inspect | `EXPLAIN ANALYZE` | Actual execution plan / runtime stats |
| Sequential access | `Seq Scan` | Table/heap scan equivalent |
| Indexed access | `Index Scan` | Index Seek / Index Scan concepts |
| Nested join | `Nested Loop` | Nested Loops |
| Hash join | `Hash Join` | Hash Match |
| Merge join | `Merge Join` | Merge Join |
| Buffer visibility | `BUFFERS` | SQL Server I/O/statistics tooling |

The exact operator names should not be memorized across databases as if they are interchangeable.

The transferable engineering idea is:

```text
SQL
 -> optimizer
 -> candidate physical plans
 -> cost-based choice
 -> execution
 -> measurements
```

That is the deeper database-engineering skill.

---

# 23. Common Mistakes

## Mistake 1 — Assuming Seq Scan = Bad

Wrong:

> “I saw Seq Scan, therefore the query is slow.”

Correct:

> “I need to know how many rows are scanned, how selective the predicate is, and whether sequential access is cheaper.”

---

## Mistake 2 — Assuming Index = Guaranteed Performance

Wrong:

> “There is an index, so the query should use it.”

Correct:

> “The index is an available access path. PostgreSQL will use it when its cost model predicts that it is beneficial.”

---

## Mistake 3 — Treating Cost as Milliseconds

Wrong:

```text
cost=0.29..8.30
```

means 8.30 ms.

Correct:

It is a planner cost estimate, not wall-clock execution time.

---

## Mistake 4 — Looking Only at Total Query Time

A query may be slow, but total time alone does not explain why.

You also want to inspect:

```text
Plan shape
Estimated rows
Actual rows
Scans
Joins
Loops
Buffers
```

---

## Mistake 5 — Optimizing Blindly

Adding multiple indexes simultaneously makes cause-and-effect harder to understand.

Prefer:

```text
Baseline
  |
One change
  |
Measure
  |
Compare
```

---

## Mistake 6 — Forgetting That `EXPLAIN ANALYZE` Executes the Query

Especially dangerous for `INSERT`, `UPDATE`, and `DELETE` statements.

Always understand the statement before using `ANALYZE`.

---

# 24. Production Best Practices

### 1. Measure before optimizing

Do not optimize from intuition alone.

### 2. Inspect actual plans for important slow queries

Estimated plans are useful. Actual runtime data is often necessary to explain reality.

### 3. Compare estimates with actuals

Large row-estimate errors deserve investigation.

### 4. Change one major variable at a time

This preserves causal clarity.

### 5. Index for query patterns, not for fashion

An index should support a meaningful access pattern.

### 6. Re-run the query after every meaningful change

Optimization is empirical.

### 7. Avoid over-indexing

Indexes also have storage and write-maintenance costs.

### 8. Validate production-like data distributions

A plan that works well on tiny sample data may not remain optimal at scale.

---

# 25. Engineering Sprinkle — The Senior Engineer Habit

A junior-oriented approach to a slow query often sounds like:

> “Let's add an index.”

A stronger engineering approach is:

```text
What is slow?
     |
     v
Can I reproduce it?
     |
     v
What plan is chosen?
     |
     v
What did the planner estimate?
     |
     v
What actually happened?
     |
     v
Where is the expensive work?
     |
     v
What single change should address it?
     |
     v
Did the measurement improve?
```

This mindset scales well beyond PostgreSQL.

It is the same debugging philosophy used for:

- API latency,
- distributed systems,
- cache behavior,
- message processing,
- memory usage,
- cloud infrastructure,
- and performance engineering generally.

The tool changes.

The reasoning process remains.

---

# 26. Project Integration

Day 31 strengthens the Student Backend from a database-engineering perspective.

Previous progression:

```text
Day 7   PostgreSQL + Python
   |
Day 8   CRUD + Database Helper
   |
Day 9   Repository Pattern / DAL / Clean Architecture
   |
Day 20  Transactions
   |
Day 21  Connection Pooling
   |
Day 22  Indexing & Query Performance
   |
Day 30  Advanced JOINs
   |
Day 31  Execution Plans & Query Optimization
```

The architecture now has a much stronger database layer:

```text
                    +-----------------------+
                    |       FastAPI         |
                    | Router / API Layer    |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |    Service Layer      |
                    | Business Rules        |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |   Repository Layer    |
                    | SQL / Data Access     |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |    PostgreSQL         |
                    | Planner + Optimizer   |
                    +-----------+-----------+
                                |
                 +--------------+--------------+
                 |              |              |
                 v              v              v
              Seq Scan      Index Scan     Bitmap Scan
                 \\             |             /
                  \\            |            /
                   +------------+------------+
                                |
                        Join / Aggregate
                                |
                                v
                             Result
```

This is the transition from simply **using a database** to beginning to **engineer around a database**.

---

# 27. Interview Questions

## Q1. What is `EXPLAIN` in PostgreSQL?

`EXPLAIN` displays the execution plan PostgreSQL's planner chooses for a query, including scan strategies, joins, estimated costs, and estimated row counts.

---

## Q2. What is the difference between `EXPLAIN` and `EXPLAIN ANALYZE`?

`EXPLAIN` shows the planner's estimated plan.

`EXPLAIN ANALYZE` actually executes the query and adds runtime measurements and actual row counts.

---

## Q3. Is a sequential scan always bad?

No. PostgreSQL may correctly choose a sequential scan when a large portion of a table is needed or when the estimated cost of using an index is higher.

---

## Q4. Why might PostgreSQL ignore an index?

Because the planner's cost model estimates that another execution path, such as a sequential scan, is cheaper for the specific query and data distribution.

---

## Q5. Name three PostgreSQL join strategies.

`Nested Loop`, `Hash Join`, and `Merge Join`.

---

## Q6. When can a Nested Loop be effective?

When the outer input is relatively small and the inner side can be searched efficiently, often through an index.

---

## Q7. What is a Hash Join?

A join strategy that typically builds a hash structure for one input and probes it with rows from the other input, making it useful for many equality joins.

---

## Q8. What is the difference between estimated rows and actual rows?

Estimated rows are the planner's prediction. Actual rows are the number observed during execution when using `EXPLAIN ANALYZE`.

Large mismatches can indicate poor cardinality estimates and potentially lead to poor plan choices.

---

## Q9. Does `EXPLAIN ANALYZE` execute a query?

Yes.

That is why it must be used carefully with statements that modify data.

---

## Q10. What does `BUFFERS` add?

It provides buffer-usage information during execution, helping engineers understand database I/O and cache-related behavior at the plan-node level.

---

## Q11. Why not create indexes on every column?

Indexes consume storage and add write/maintenance overhead. They should support meaningful query patterns rather than being added indiscriminately.

---

## Q12. How would you investigate a slow repository method?

A good answer is:

```text
Reproduce query
   -> EXPLAIN
   -> EXPLAIN ANALYZE
   -> inspect scans / joins / row estimates
   -> inspect buffers where useful
   -> identify bottleneck
   -> make one targeted change
   -> measure again
```

---

# 28. Cheat Sheet

| Item | Meaning |
|---|---|
| `EXPLAIN` | Show planner's execution plan |
| `EXPLAIN ANALYZE` | Execute query + show actual runtime data |
| `BUFFERS` | Show buffer activity during execution |
| `Seq Scan` | Sequential table access |
| `Index Scan` | Access using an index |
| `Bitmap Scan` | Bitmap-oriented index/table access strategy |
| `Nested Loop` | Repeated lookup through inner side |
| `Hash Join` | Hash-based equality join |
| `Merge Join` | Merge ordered inputs |
| `cost` | Planner cost units |
| `rows` | Estimated row count |
| `actual rows` | Observed row count under `ANALYZE` |
| `loops` | Number of times a plan node executed |
| `width` | Estimated average row width |
| `BUFFERS` | Additional buffer/I/O visibility |

### Core commands

```sql
EXPLAIN
SELECT ...;
```

```sql
EXPLAIN ANALYZE
SELECT ...;
```

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

### Performance mantra

```text
Measure
  -> Explain
  -> Understand
  -> Change
  -> Measure again
```

---

# 29. Final Mental Model

A useful mental model for Day 31 is:

```text
                SQL expresses WHAT
                         |
                         v
              PostgreSQL planner asks
                         |
       +-----------------+-----------------+
       |                                   |
   How to scan?                        How to join?
       |                                   |
       +----------+-----------+------------+
                  |           |
              Seq Scan    Index Scan
                  |
                  +----------------------+
                                         |
                             Nested Loop / Hash / Merge
                                         |
                                         v
                                Execution Plan
                                         |
                                         v
                                  Query executes
                                         |
                                         v
                             EXPLAIN ANALYZE tells
                             us what actually happened
                                         |
                                         v
                                 Engineer compares
                                  estimate vs reality
                                         |
                                         v
                                   Optimize safely
```

The key conceptual progression is:

```text
SQL syntax
   ↓
Relational design
   ↓
Indexes
   ↓
Query plans
   ↓
Execution behavior
   ↓
Measurement
   ↓
Performance engineering
```

Day 31 is the bridge between **writing SQL** and **reasoning about how a database executes SQL**.

---

# 30. Revision Checklist

Before considering Day 31 fully internalized, you should be able to answer “yes” to all of these:

- [ ] I can explain why PostgreSQL creates an execution plan.
- [ ] I can explain what `EXPLAIN` provides.
- [ ] I can explain the difference between `EXPLAIN` and `EXPLAIN ANALYZE`.
- [ ] I know that `EXPLAIN ANALYZE` actually executes the query.
- [ ] I can read a plan as a tree from top-level operation through child nodes.
- [ ] I understand `Seq Scan`.
- [ ] I understand `Index Scan`.
- [ ] I know why a sequential scan can be the correct choice.
- [ ] I understand the high-level purpose of `Nested Loop`.
- [ ] I understand the high-level purpose of `Hash Join`.
- [ ] I understand the high-level purpose of `Merge Join`.
- [ ] I can explain estimated rows vs actual rows.
- [ ] I understand why large row-estimate errors matter.
- [ ] I know why adding an index does not guarantee index usage.
- [ ] I can use `EXPLAIN (ANALYZE, BUFFERS)` for deeper investigation.
- [ ] I can describe a safe SQL performance-debugging loop.
- [ ] I can connect repository SQL to PostgreSQL execution plans.
- [ ] I can explain the PostgreSQL concepts in language transferable to other enterprise databases.

---

# 31. Exact Resources Used

These are the primary PostgreSQL references for Day 31.

### PostgreSQL Documentation — Using EXPLAIN

**URL:**  
https://www.postgresql.org/docs/current/using-explain.html

**Relevant sections:**

- `14.1.1 EXPLAIN Basics`
- `14.1.2 EXPLAIN ANALYZE`
- `14.1.3 Caveats`
- Examples covering `Nested Loop`, `Hash Join`, and `Merge Join`

### PostgreSQL Documentation — EXPLAIN Command

**URL:**  
https://www.postgresql.org/docs/current/sql-explain.html

**Focus:**

- `ANALYZE`
- `BUFFERS`
- `VERBOSE`

### PostgreSQL Documentation — Indexes

**URL:**  
https://www.postgresql.org/docs/current/indexes.html

**Relevant sections:**

- `11.1 Introduction`
- `11.2.1 B-Tree Indexes`

---

# 32. Closing Note

Day 30 taught the relational side of JOINs:

> “How do these tables relate, and how do I express that relationship in SQL?”

Day 31 adds the systems side:

> “How will PostgreSQL physically execute that SQL, and how do I prove whether that execution is efficient?”

That distinction is exactly what starts moving database knowledge from application-level usage toward backend engineering and production systems thinking.

**Status:** Day 031 Engineering Handbook Complete ✅
