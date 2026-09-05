# Day 032: SQL Indexing and Optimization — Answer Sheet

**Date:** 2026-09-05  
**Database:** `student_db` (locally installed PostgreSQL 18)  
**Schema used:** `public` — table `students` (2,500,000 rows)  
**Existing indexes at start:** `students_pkey` (id), `students_email_key` (email UNIQUE)

---

## Dataset Overview

| Attribute          | Value          |
|--------------------|----------------|
| Total rows         | 2,500,000      |
| Distinct cities    | 71             |
| Distinct ages      | 18             |
| `Ahmedabad` count  | 35,268 rows    |
| `age = 30` count   | 139,328 rows   |
| `city+age` count   | 1,900 rows     |

```sql
-- Table columns
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema='public' AND table_name='students'
ORDER BY ordinal_position;
-- id | integer | name | varchar | age | integer | city | varchar | email | varchar
```

---

## Exercise 1: Baseline Multi-Condition Query

### Setup
No indexes exist on `city` or `age` at this point. Only PK and unique email index exist.

### Query

```sql
-- Baseline query: city + age filter, no relevant indexes
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

### Output

```
 Gather  (cost=1000.00..45664.40 rows=1994 width=60) (actual time=0.536..142.314 rows=1900.00 loops=1)
   Workers Planned: 2
   Workers Launched: 2
   Buffers: shared hit=13941 read=14899
   ->  Parallel Seq Scan on students  (cost=0.00..44465.00 rows=831 width=60) (actual time=0.301..43.167 rows=633.33 loops=3)
         Filter: (((city)::text = 'Ahmedabad'::text) AND (age = 30))
         Rows Removed by Filter: 832700
         Buffers: shared hit=13941 read=14899
 Planning:
   Buffers: shared hit=120
 Planning Time: 0.309 ms
 Execution Time: 142.418 ms
```

### Baseline Metrics

| Metric              | Value                     |
|---------------------|---------------------------|
| Scan type           | Parallel Sequential Scan  |
| Workers             | 2 parallel workers        |
| Estimated rows      | 1,994                     |
| Actual rows         | 1,900                     |
| Execution time      | **142.418 ms**            |
| Buffers shared hit  | 13,941                    |
| Buffers shared read | 14,899 (disk reads)       |
| Rows scanned total  | ~2,498,100 (3 × 832,700)  |

### Observation
PostgreSQL used a **Parallel Sequential Scan** — it read the entire 2.5M row table across
3 parallel workers (1 leader + 2 workers). This is expensive: 14,899 pages read from disk.
This is the worst case for a multi-condition filter with no relevant indexes.

---

## Exercise 2: Single-Column Index on `city`

### Index Created

```sql
-- Single-column index on the city column
CREATE INDEX idx_students_city ON public.students(city);
```

### Query After City Index

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

### Output

```
 Bitmap Heap Scan on students  (cost=392.43..31285.62 rows=1994 width=60) (actual time=3.951..44.753 rows=1900.00 loops=1)
   Recheck Cond: ((city)::text = 'Ahmedabad'::text)
   Filter: (age = 30)
   Rows Removed by Filter: 33368
   Heap Blocks: exact=20522
   Buffers: shared hit=745 read=19810 written=3
   ->  Bitmap Index Scan on idx_students_city  (cost=0.00..391.93 rows=35667 width=0) (actual time=1.943..1.943 rows=35268.00 loops=1)
         Index Cond: ((city)::text = 'Ahmedabad'::text)
         Index Searches: 1
         Buffers: shared read=33
 Planning:
   Buffers: shared hit=135 read=1
 Planning Time: 0.452 ms
 Execution Time: 44.916 ms
```

### City Index Metrics

| Metric              | Value                         |
|---------------------|-------------------------------|
| Scan type           | Bitmap Heap Scan              |
| Index used          | `idx_students_city`           |
| Index scan rows     | 35,268 (all Ahmedabad)        |
| After age filter    | 33,368 rows removed           |
| Actual rows         | 1,900                         |
| Execution time      | **44.916 ms** (3.2x faster)   |
| Buffers read (disk) | 19,810 (heap) + 33 (index)    |

### Observation
The city index changed the plan from **Parallel Seq Scan** to **Bitmap Heap Scan**:
1. The Bitmap Index Scan on `idx_students_city` finds all 35,268 Ahmedabad rows using the index.
2. The Bitmap Heap Scan then fetches those rows and applies the `age = 30` filter.
3. Still removed 33,368 rows during the heap scan (the age filter was not index-covered).
4. Execution time dropped from 142 ms to 44 ms — significant improvement, but still costly
   because 35,268 heap pages were read just to filter by age.

---

## Exercise 3: Add Single-Column Index on `age`

### Index Created

```sql
-- Single-column index on the age column
CREATE INDEX idx_students_age ON public.students(age);
```

### Query With Both Single-Column Indexes

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

### Output

```
 Bitmap Heap Scan on students  (cost=1917.73..8164.15 rows=1994 width=60) (actual time=7.527..11.788 rows=1900.00 loops=1)
   Recheck Cond: (((city)::text = 'Ahmedabad'::text) AND (age = 30))
   Heap Blocks: exact=1833
   Buffers: shared hit=1371 read=616
   ->  BitmapAnd  (cost=1917.73..1917.73 rows=1994 width=0) (actual time=7.303..7.303 rows=0.00 loops=1)
         Buffers: shared read=154
         ->  Bitmap Index Scan on idx_students_city  (cost=0.00..391.93 rows=35667 width=0) (actual time=1.912..1.913 rows=35268.00 loops=1)
               Index Cond: ((city)::text = 'Ahmedabad'::text)
               Index Searches: 1
               Buffers: shared read=33
         ->  Bitmap Index Scan on idx_students_age  (cost=0.00..1524.56 rows=139750 width=0) (actual time=4.884..4.884 rows=139328.00 loops=1)
               Index Cond: (age = 30)
               Index Searches: 1
               Buffers: shared read=121
 Planning:
   Buffers: shared hit=149 read=2
 Planning Time: 0.445 ms
 Execution Time: 11.992 ms
```

### Two Single-Column Index Metrics

| Metric              | Value                           |
|---------------------|---------------------------------|
| Scan type           | Bitmap Heap Scan + BitmapAnd    |
| Indexes used        | `idx_students_city` + `idx_students_age` |
| City bitmap rows    | 35,268                          |
| Age bitmap rows     | 139,328                         |
| AND-merged rows     | 1,900                           |
| Actual rows         | 1,900                           |
| Execution time      | **11.992 ms** (11.9x faster than baseline) |
| Buffers read (disk) | 616 (heap) + 154 (indexes)      |
| Heap Blocks         | 1,833                           |

### Comparison So Far

| Strategy            | Execution Time | Buffers Read  |
|---------------------|---------------|---------------|
| No index (baseline) | 142.418 ms    | 14,899        |
| City index only     | 44.916 ms     | 19,843        |
| City + Age indexes  | 11.992 ms     | 770           |

### Observation
With both single-column indexes, PostgreSQL used a **BitmapAnd** strategy:
1. Scanned `idx_students_city` bitmap → 35,268 matching IDs
2. Scanned `idx_students_age` bitmap → 139,328 matching IDs
3. AND-merged both bitmaps in memory → 1,900 matching IDs
4. Fetched only those 1,900 rows from the heap

This is much more efficient because only 1,833 heap blocks were touched (down from 20,522).

---

## Exercise 4: Composite Index `(city, age)`

### Index Created

```sql
-- Composite index: city as leading column, age as second column
CREATE INDEX idx_students_city_age ON public.students(city, age);
```

### Query With Composite Index

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

### Output

```
 Bitmap Heap Scan on students  (cost=28.87..6275.29 rows=1994 width=60) (actual time=0.364..3.903 rows=1900.00 loops=1)
   Recheck Cond: (((city)::text = 'Ahmedabad'::text) AND (age = 30))
   Heap Blocks: exact=1833
   Buffers: shared hit=1833 read=5
   ->  Bitmap Index Scan on idx_students_city_age  (cost=0.00..28.37 rows=1994 width=0) (actual time=0.233..0.233 rows=1900.00 loops=1)
         Index Cond: (((city)::text = 'Ahmedabad'::text) AND (age = 30))
         Index Searches: 1
         Buffers: shared read=5
 Planning:
   Buffers: shared hit=165 read=1
 Planning Time: 0.572 ms
 Execution Time: 3.991 ms
```

### Composite Index Metrics

| Metric              | Value                               |
|---------------------|-------------------------------------|
| Scan type           | Bitmap Heap Scan                    |
| Index used          | `idx_students_city_age`             |
| Index scan rows     | 1,900 (exactly matching both conditions) |
| Actual rows         | 1,900                               |
| Execution time      | **3.991 ms** (35.7x faster than baseline!) |
| Index buffers read  | **5** (down from 154 with two indexes) |
| Heap buffers hit    | 1,833                               |

### Full Progression Comparison

| Strategy                    | Execution Time | Index Pages | Plan               |
|-----------------------------|---------------|-------------|---------------------|
| No index (baseline)         | 142.418 ms    | 0           | Parallel Seq Scan  |
| `idx_students_city` only    | 44.916 ms     | 33          | Bitmap Heap Scan   |
| `idx_city` + `idx_age`      | 11.992 ms     | 154         | BitmapAnd          |
| `idx_students_city_age` (composite) | **3.991 ms** | **5** | Bitmap Heap Scan   |

### Why Composite Wins

The composite index `(city, age)` stores both columns together in a single B-tree.
A single index scan finds **exactly the 1,900 matching rows** using both conditions simultaneously.
There is no need to build two bitmaps and AND them — the work is done entirely inside the index.
Only 5 index pages were read (vs 154 for BitmapAnd with two separate indexes).

---

## Exercise 5: Reverse the Column Order `(age, city)`

### Index Created

```sql
-- Reverse composite: age as leading column, city as second column
CREATE INDEX idx_students_age_city ON public.students(age, city);
```

### Planner Choice With Both Composites Present

```sql
-- With both idx_students_city_age AND idx_students_age_city available
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

### Natural Plan (enable_bitmapscan = on)

```
 Bitmap Heap Scan on students  (cost=28.87..6275.29 rows=1994 width=60) (actual time=0.300..4.260 rows=1900.00 loops=1)
   Recheck Cond: ((age = 30) AND ((city)::text = 'Ahmedabad'::text))
   Heap Blocks: exact=1833
   Buffers: shared hit=1837
   ->  Bitmap Index Scan on idx_students_age_city  (cost=0.00..28.37 rows=1994 width=0) (actual time=0.168..0.168 rows=1900.00 loops=1)
         Index Cond: ((age = 30) AND ((city)::text = 'Ahmedabad'::text))
         Index Searches: 1
         Buffers: shared hit=4
 Planning:
   Buffers: shared hit=181
 Planning Time: 0.480 ms
 Execution Time: 4.350 ms
```

### Forced Index Scan (enable_bitmapscan = off — to see the age,city index directly)

```
 Index Scan using idx_students_age_city on students  (cost=0.43..7747.68 rows=1994 width=60) (actual time=0.072..3.862 rows=1900.00 loops=1)
   Index Cond: ((age = 30) AND ((city)::text = 'Ahmedabad'::text))
   Index Searches: 1
   Buffers: shared hit=1833 read=4
 Planning:
   Buffers: shared hit=180 read=1
 Planning Time: 0.860 ms
 Execution Time: 3.926 ms
```

### Comparison: `(city, age)` vs `(age, city)`

| Index                      | Est Cost   | Actual Time | Index Reads | Notes                    |
|----------------------------|-----------|-------------|-------------|--------------------------|
| `idx_students_city_age`    | 28.87..6275 | 3.991 ms  | 5 pages     | City=leading, city more selective |
| `idx_students_age_city`    | 28.87..6275 | 4.350 ms  | 4 pages     | Age=leading, age less selective |

### The Selectivity Discussion

In this dataset:
- `city = 'Ahmedabad'` → 35,268 rows out of 2,500,000 = **1.4%** of table
- `age = 30` → 139,328 rows out of 2,500,000 = **5.6%** of table

**City is more selective** (1.4% vs 5.6%), meaning `(city, age)` is typically preferred:
- The leading column narrows the candidate set more aggressively first
- With `(city, age)`, the B-tree navigates to the Ahmedabad section (1.4%) then filters by age

**Important nuance:** For this specific `city + age` query, both composite index orderings
perform nearly identically (~4ms) because both conditions are provided. The leading-column
matters most when only ONE condition is used (see Exercise 6).

**The rule is NOT simply:** "Put the most selective column first."  
The real answer depends on: query workload, which predicates appear alone, range scans, and sort needs.

---

## Exercise 6: Leading-Column Query Pattern Experiment

All three queries run with `idx_students_city_age (city, age)` available.

### Query A — Only `city` Filter

```sql
-- Query A: Uses leading column of idx_students_city_age
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE city = 'Ahmedabad';
```

```
 Bitmap Heap Scan on students  (cost=400.85..31204.87 rows=35667 width=60) (actual time=3.563..47.558 rows=35268.00 loops=1)
   Recheck Cond: ((city)::text = 'Ahmedabad'::text)
   Heap Blocks: exact=20522
   Buffers: shared hit=1866 read=18689 written=2
   ->  Bitmap Index Scan on idx_students_city  (cost=0.00..391.93 rows=35667 width=0) (actual time=1.853..1.854 rows=35268.00 loops=1)
         Index Cond: ((city)::text = 'Ahmedabad'::text)
         Index Searches: 1
         Buffers: shared hit=33
 Planning:
   Buffers: shared hit=176
 Planning Time: 0.448 ms
 Execution Time: 48.535 ms
```

**Index used:** `idx_students_city` (single-column, still available)  
**Rows returned:** 35,268  
**Time:** 48.535 ms  
**Note:** The composite `idx_students_city_age` COULD serve this query (leading column = city),
but the planner chose the single-column `idx_students_city` (fewer pages to scan since it only
stores city values, not city+age pairs).

---

### Query B — `city AND age` Filter

```sql
-- Query B: Full composite index usage
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

```
 Bitmap Heap Scan on students  (cost=28.87..6275.29 rows=1994 width=60) (actual time=0.390..3.910 rows=1900.00 loops=1)
   Recheck Cond: ((age = 30) AND ((city)::text = 'Ahmedabad'::text))
   Heap Blocks: exact=1833
   Buffers: shared hit=1833 read=4
   ->  Bitmap Index Scan on idx_students_age_city  (cost=0.00..28.37 rows=1994 width=0) (actual time=0.258..0.258 rows=1900.00 loops=1)
         Index Cond: ((age = 30) AND ((city)::text = 'Ahmedabad'::text))
         Index Searches: 1
         Buffers: shared read=4
 Planning:
   Buffers: shared hit=181
 Planning Time: 0.624 ms
 Execution Time: 3.999 ms
```

**Index used:** `idx_students_age_city` (planner chose age-leading when both available)  
**Rows returned:** 1,900  
**Time:** 3.999 ms

---

### Query C — Only `age` Filter

```sql
-- Query C: Age-only filter — does NOT use leading column of idx_students_city_age
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE age = 30;
```

```
 Bitmap Heap Scan on students  (cost=1559.49..32146.37 rows=139750 width=60) (actual time=7.600..60.978 rows=139328.00 loops=1)
   Recheck Cond: (age = 30)
   Heap Blocks: exact=28636
   Buffers: shared hit=1278 read=27479
   ->  Bitmap Index Scan on idx_students_age  (cost=0.00..1524.56 rows=139750 width=0) (actual time=4.873..4.873 rows=139328.00 loops=1)
         Index Cond: (age = 30)
         Index Searches: 1
         Buffers: shared read=121
 Planning:
   Buffers: shared hit=176
 Planning Time: 0.453 ms
 Execution Time: 64.157 ms
```

**Index used:** `idx_students_age` (single-column age index)  
**Rows returned:** 139,328  
**Time:** 64.157 ms  
**Note:** The composite `idx_students_city_age (city, age)` CANNOT be used for `age`-only queries
because `age` is the NON-LEADING column. B-tree indexes require the leading column to be present.

---

### Leading-Column Rule Demonstrated

| Query           | Filter Used           | Index Used               | Uses Composite? | Time       |
|-----------------|-----------------------|--------------------------|-----------------|------------|
| A (city only)   | `city = 'Ahmedabad'`  | `idx_students_city`      | Indirectly (leading col) | 48.5 ms |
| B (city + age)  | `city AND age`        | `idx_students_age_city`  | YES             | 4.0 ms     |
| C (age only)    | `age = 30`            | `idx_students_age`       | **NO** (non-leading col) | 64.2 ms |

**Key learning:** An index `(city, age)` can serve:
- Queries filtering on `city` alone (uses leading column)
- Queries filtering on `city AND age` (uses both columns)
- **Cannot serve** queries filtering on `age` alone (non-leading column is skipped in B-tree)

---

## Exercise 7: Partial Index

### Setup — Add `is_active` Column

The `public.students` table did not originally have an `is_active` column.
It was added for this exercise:

```sql
-- Add is_active boolean column
ALTER TABLE public.students ADD COLUMN is_active BOOLEAN DEFAULT true;

-- Set 80% active, 20% inactive (id % 5 != 0 = active)
UPDATE public.students
SET is_active = (id % 5 != 0);
```

**Result:**
- `is_active = true`:  2,000,000 students (80%)
- `is_active = false`: 500,000 students (20%)

### Partial Index Created

```sql
-- Partial index: only index active students' emails
-- This index covers 2M of 2.5M rows — 80% of the table
CREATE INDEX idx_students_active_email
ON public.students(email)
WHERE is_active = true;
```

### Test A — Query Matching Partial Index Predicate

```sql
-- Query matches partial index predicate (is_active = true)
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE is_active = true
  AND email = 'sunita.kadam174045@outlook.com';
```

```
 Index Scan using idx_students_active_email on students  (cost=0.43..8.45 rows=1 width=61) (actual time=0.048..0.048 rows=1.00 loops=1)
   Index Cond: ((email)::text = 'sunita.kadam174045@outlook.com'::text)
   Index Searches: 1
   Buffers: shared hit=1 read=3
 Planning:
   Buffers: shared hit=183 read=4
 Planning Time: 0.596 ms
 Execution Time: 0.085 ms
```

**Result:** Uses `idx_students_active_email` → **Index Scan, 0.085 ms**  
The partial index is valid for this query because `is_active = true` matches the index predicate.

---

### Test B — Query NOT Matching Partial Index Predicate

```sql
-- Query does NOT match partial index predicate (is_active = false)
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE is_active = false
  AND email = 'sunita.kadam174045@outlook.com';
```

```
 Index Scan using students_email_key on students  (cost=0.56..8.57 rows=1 width=61) (actual time=0.083..0.083 rows=0.00 loops=1)
   Index Cond: ((email)::text = 'sunita.kadam174045@outlook.com'::text)
   Filter: (NOT is_active)
   Rows Removed by Filter: 1
   Index Searches: 1
   Buffers: shared hit=1 read=4
 Planning:
   Buffers: shared hit=187
 Planning Time: 0.506 ms
 Execution Time: 0.121 ms
```

**Result:** Falls back to `students_email_key` (full email unique index) → **Index Scan, 0.121 ms**  
PostgreSQL cannot use `idx_students_active_email` here because `is_active = false` does NOT
satisfy `WHERE is_active = true` — the partial index only covers the active subset.

### Partial Index Comparison

| Query Predicate        | Index Used                      | Execution Time | Rows Found |
|------------------------|---------------------------------|---------------|------------|
| `is_active = true`     | `idx_students_active_email`     | 0.085 ms      | 1          |
| `is_active = false`    | `students_email_key` (full)     | 0.121 ms      | 0          |

### Why Use Partial Indexes?

1. **Smaller index size:** `idx_students_active_email` only indexes 2M of 2.5M rows — smaller,
   faster to maintain, fits more easily in memory cache.
2. **Covers the common case:** If 90%+ of queries target active students, the partial index serves
   exactly the right subset.
3. **Complement:** The full `students_email_key` unique index still serves inactive-student queries.

---

## Exercise 8: Index Cleanup

### Philosophy
> Indexes are not free. They cost storage, write overhead, and maintenance work on every INSERT,
> UPDATE, and DELETE. The goal is: keep what is justified, remove what is not.

### Indexes Dropped

```sql
-- Drop single-column indexes (superseded by composite)
DROP INDEX public.idx_students_city;
DROP INDEX public.idx_students_age;

-- Drop reverse composite (age,city) — (city,age) is preferred for our query workload
DROP INDEX public.idx_students_age_city;
```

### Indexes Kept (Justified)

```sql
-- 1. Primary key (always needed)
-- students_pkey → students(id)

-- 2. Unique email constraint (data integrity + lookup by email)
-- students_email_key → students(email)

-- 3. Composite index for the core query workload (city + age filter)
-- idx_students_city_age → students(city, age)

-- 4. Partial index for active-student email lookups (smaller, targeted)
-- idx_students_active_email → students(email) WHERE is_active = true
```

### Final Index State

```
students_pkey             → students(id)                           [PK, always needed]
students_email_key        → students(email)                        [UNIQUE constraint]
idx_students_city_age     → students(city, age)                    [composite, core query]
idx_students_active_email → students(email) WHERE is_active = true [partial, active users]
```

### Reasoning

| Index Removed            | Why Removed                                                    |
|--------------------------|----------------------------------------------------------------|
| `idx_students_city`      | Superseded by composite `(city, age)` for city+age queries     |
| `idx_students_age`       | Superseded by composite; age-only queries can use composite too |
| `idx_students_age_city`  | Duplicate of (city,age) composite for this query workload      |

---

## Exercise 9: Revisit Day 31 — Final Plan Inspection

### Best-Performing Query

```sql
-- Best-performing query: composite index on (city, age)
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.students
WHERE city = 'Ahmedabad'
  AND age = 30;
```

### Output

```
 Bitmap Heap Scan on students  (cost=40.87..6832.69 rows=1994 width=61) (actual time=5.129..10.339 rows=1900.00 loops=1)
   Recheck Cond: (((city)::text = 'Ahmedabad'::text) AND (age = 30))
   Heap Blocks: exact=3673
   Buffers: shared hit=855 read=2824 written=31
   ->  Bitmap Index Scan on idx_students_city_age  (cost=0.00..40.37 rows=1994 width=0) (actual time=0.325..0.325 rows=3800.00 loops=1)
         Index Cond: (((city)::text = 'Ahmedabad'::text) AND (age = 30))
         Index Searches: 1
         Buffers: shared read=6
 Planning:
   Buffers: shared hit=157
 Planning Time: 0.441 ms
 Execution Time: 10.464 ms
```

### Day 31 + Day 32 Analysis

| Question                           | Answer                                                   |
|------------------------------------|----------------------------------------------------------|
| 1. Which scan is used?             | **Bitmap Heap Scan** (after Bitmap Index Scan)           |
| 2. Is an index used?               | **Yes**                                                  |
| 3. Which index?                    | `idx_students_city_age`                                  |
| 4. Estimated rows?                 | 1,994                                                    |
| 5. Actual rows?                    | 1,900                                                    |
| 6. Execution time?                 | **10.464 ms** (from 142 ms baseline — 13.6x improvement) |
| 7. Significant buffer activity?    | 2,824 pages read, 31 dirtied — moderate disk I/O         |
| 8. Why this plan?                  | See explanation below                                    |

### Why the Planner Chose This Plan

The planner chose **Bitmap Heap Scan** over a direct **Index Scan** because 1,900 rows are
scattered across ~3,673 heap blocks. A Bitmap Heap Scan:
1. First does a Bitmap Index Scan to collect ALL matching tuple IDs
2. Sorts them by physical location
3. Reads heap pages in order — minimizing random I/O (known as "heap block sort")

A direct Index Scan would do 1,900 random heap fetches (one per row). At this row count,
batching them via a bitmap is more efficient.

**Estimated vs Actual:** The planner estimated 1,994 rows and got 1,900 — a very accurate
estimate, showing that ANALYZE kept the statistics fresh.

**Buffer activity:** `shared hit=855, read=2824, written=31`
- 855 pages were already cached (warm cache from previous queries)
- 2,824 pages needed disk reads (the data wasn't fully cached)
- 31 pages were dirtied (likely autovacuum-related hint bit updates)

---

## Exercise 10: Repository Thinking

### Scenario

> Tomorrow we add: `repository.search_students(city, age)`

### Correct Architecture

```
HTTP Request
    |
    v
Router (FastAPI)
    |   /students/search?city=Ahmedabad&age=30
    v
Service Layer
    |   Validates inputs, applies business rules
    v
Repository.search_students(city="Ahmedabad", age=30)
    |   Builds parameterized SQL
    v
PostgreSQL (executes the query)
    |   Uses idx_students_city_age
    v
Results returned up the chain
```

### Where Performance Work Happens

```
Repository SQL query
    |
    v
EXPLAIN ANALYZE (developer investigation — outside application code)
    |
    v
Planner behavior observed
    |
    v
Index design (CREATE INDEX idx_students_city_age ON students(city, age))
    |
    v
Measured improvement confirmed
    |
    v
Index stays in DB — Service layer is unaware of its existence
```

### The Service Should NOT Contain

```python
# WRONG — performance investigation does not belong in service layer
class StudentService:
    async def search_students(self, city: str, age: int):
        await db.execute("EXPLAIN ANALYZE SELECT ...")   # NO
```

```python
# CORRECT — service calls repository, knows nothing about indexes
class StudentService:
    async def search_students(self, city: str, age: int):
        return await self.student_repo.search_students(city=city, age=age)
```

```python
# CORRECT — repository owns the SQL with parameterized query
class StudentRepository:
    async def search_students(self, city: str, age: int):
        # The idx_students_city_age index is used transparently by PostgreSQL
        query = """
            SELECT *
            FROM students
            WHERE city = $1
              AND age = $2
        """
        return await self.db.fetch_all(query, city, age)
```

### Key Principle

The index `idx_students_city_age` is a **persistence implementation detail**.
The Service layer knows it wants students filtered by city and age.
It does NOT need to know how PostgreSQL satisfies that query internally.
Indexes live and are tuned at the PostgreSQL/Repository level — completely transparent to
business logic above.

---

## Full Experiment Summary

### Execution Time Progression (city=Ahmedabad AND age=30)

| Step | Strategy                           | Execution Time | Improvement |
|------|------------------------------------|---------------|-------------|
| 1    | No index → Parallel Seq Scan       | 142.4 ms      | Baseline    |
| 2    | `idx_students_city` only           | 44.9 ms       | 3.2x        |
| 3    | `idx_students_city` + `idx_age`    | 12.0 ms       | 11.9x       |
| 4    | `idx_students_city_age` composite  | **3.991 ms**  | **35.7x**   |

### Final Index Decisions

| Index                         | Kept? | Justification                                  |
|-------------------------------|-------|------------------------------------------------|
| `students_pkey`               | YES   | Primary key — always required                  |
| `students_email_key`          | YES   | UNIQUE constraint + email lookup support       |
| `idx_students_city_age`       | YES   | Core query workload: city+age filter           |
| `idx_students_active_email`   | YES   | Partial index for active-user email lookups    |
| `idx_students_city`           | NO    | Superseded by composite                        |
| `idx_students_age`            | NO    | Superseded by composite                        |
| `idx_students_age_city`       | NO    | Redundant for our query workload               |
