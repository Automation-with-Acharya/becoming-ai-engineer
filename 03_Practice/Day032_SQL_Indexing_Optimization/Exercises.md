# SQL Indexing and Optimization Exercises

## Exercise 1: Create a Multi-Condition Query

Use a large student dataset and construct a query such as:

```sql
SELECT *
FROM students
WHERE city = 'Ahmedabad'
	AND age = 30;
```

First run:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

Record:

- Scan type
- Rows
- Actual rows
- Execution time
- Buffers

This is your baseline.

## Exercise 2: Single-Column Index Experiment

Create:

```sql
CREATE INDEX idx_students_city
ON students(city);
```

Then re-run:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM students
WHERE city = 'Ahmedabad'
	AND age = 30;
```

Observe what changed.

Do not assume the index must win.

## Exercise 3: Add the Second Index

Now create:

```sql
CREATE INDEX idx_students_age
ON students(age);
```

Run the same query again.

Compare:

1. No index
2. City index
3. City and age indexes

Record:

- Plan
- Execution time
- Actual rows
- Buffers

## Exercise 4: Replace with a Composite Index

Now create:

```sql
CREATE INDEX idx_students_city_age
ON students(city, age);
```

Run:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM students
WHERE city = 'Ahmedabad'
	AND age = 30;
```

Compare:

- Single-column strategy
- Composite index strategy

This is the core experiment of Day 32.

## Exercise 5: Reverse the Column Order

Now experiment with:

```sql
CREATE INDEX idx_students_age_city
ON students(age, city);
```

Then compare it against:

```sql
CREATE INDEX idx_students_city_age
ON students(city, age);
```

Use the same query.

**Question:** Why might the planner prefer one ordering over the other?

This is where selectivity enters the discussion.

### Selectivity

Very roughly, selectivity tells us how strongly a condition narrows down the candidate rows.

Imagine 2.5 million students.

Suppose:

- `city = 'Ahmedabad'` returns 600,000 rows.
- `age = 73` returns 7,000 rows.

Then `age` is much more selective in this example.

But index design is not simply:

> "Always put the most selective column first."

The real answer depends on the actual query workload, predicates, ordering, and planner behavior.

Today you are learning the concept, not memorizing a universal rule.

## Exercise 6: Query Pattern Experiment

Run these three queries:

### Query A

```sql
SELECT *
FROM students
WHERE city = 'Ahmedabad';
```

### Query B

```sql
SELECT *
FROM students
WHERE city = 'Ahmedabad'
	AND age = 30;
```

### Query C

```sql
SELECT *
FROM students
WHERE age = 30;
```

Then compare their plans against:

```sql
INDEX(city, age)
```

This will make the leading-column concept much more concrete.

## Exercise 7: Partial Index

Now suppose only active students are frequently queried.

Create a partial index:

```sql
CREATE INDEX idx_students_active_email
ON students(email)
WHERE is_active = true;
```

Then test:

```sql
SELECT *
FROM students
WHERE is_active = true
	AND email = 'student@example.com';
```

Run:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

Then compare it with a query that does not satisfy the predicate.

For example:

```sql
SELECT *
FROM students
WHERE is_active = false
	AND email = 'student@example.com';
```

The point is to understand:

1. Partial index
2. Covers only a subset
3. Query must match the index predicate

## Exercise 8: Don't Leave Six Indexes Behind

After your experiments, clean up the practice indexes that are no longer needed.

This is intentional.

We do not want the lesson to become:

> "Performance = keep adding indexes."

Instead:

1. Experiment
2. Measure
3. Understand
4. Keep the justified index
5. Remove unnecessary indexes

Indexes improve some reads but also consume storage and add write and maintenance work.

## Exercise 9: Revisit Day 31

Take the best-performing query from today's experiments and inspect:

```sql
EXPLAIN (ANALYZE, BUFFERS)
```

Now answer:

1. Which scan is used?
2. Is an index used?
3. Which index?
4. Estimated rows?
5. Actual rows?
6. Execution time?
7. Significant buffer activity?
8. Why do you think the planner chose this plan?

This is where Day 31 and Day 32 become one continuous skill.

## Exercise 10: Repository Thinking

Suppose tomorrow we add:

```text
repository.search_students(city, age)
```

The architecture should remain:

1. Router
2. Service
3. Repository
4. Parameterized SQL
5. PostgreSQL

Performance work happens around the Repository's query:

1. Repository query
2. `EXPLAIN ANALYZE`
3. Planner behavior
4. Index design
5. Measured improvement

The Service layer should not need to know that a city and age index exists.

That is an implementation detail of persistence.
