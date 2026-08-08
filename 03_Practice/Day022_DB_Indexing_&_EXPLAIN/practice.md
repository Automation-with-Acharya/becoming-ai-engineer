# Day 022 — DB Indexing & EXPLAIN

## Exercise 1

1. Create a table with several thousand rows (or generate sample data).
2. Search by:
   - `id`
   - `email`
   - `name`
3. Measure response time.

## Exercise 2

1. Create an index.
2. Run the same query again.
3. Observe the difference.

## Exercise 3

1. Run:
   ```sql
   EXPLAIN SELECT ...
   ```
2. Interpret whether PostgreSQL uses:
   - Sequential Scan
   - Index Scan

## Exercise 4

1. Run:
   ```sql
   EXPLAIN ANALYZE
   ```
2. Record:
   - Planning Time
   - Execution Time

## Exercise 5

1. Add an index to a column in your Student Management project that is commonly searched (for example, `email`).
2. Discuss why that column benefits from indexing.
