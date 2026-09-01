# Day 030: SQL JOINs & Relational Query Design — Answer Sheet

**Completed:** 2026-08-26  
**Database:** `student_db` on PostgreSQL 18.4  
**Practice schema:** `day030_joins`

## Exercise 1 — Inspect the Current Database Schema

The application schema currently contains:

| Table             | Relationship-bearing tables |
| ----------------- | --------------------------- |
| `public.students` | None                        |

The public schema has no foreign-key constraints. Because the mini-project does not yet model courses or enrollments, the exercises were performed in the isolated `day030_joins` practice schema. The production `public.students` table was not modified.

```sql
-- Inspect application tables without changing the application schema.
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Inspect relationship-bearing tables in the application schema.
SELECT table_name, constraint_name
FROM information_schema.table_constraints
WHERE table_schema = 'public' AND constraint_type = 'FOREIGN KEY'
ORDER BY table_name, constraint_name; keys were found.

```

## Exercise 2 — Build a JOIN Dataset

The practice schema is recreated idempotently for this lesson. The foreign keys enforce the relationship chain:

`students.student_id` → `enrollments.student_id` and `courses.course_id` → `enrollments.course_id`.

```sql
-- Recreate only the isolated practice schema used by Day 030.
DROP SCHEMA IF EXISTS day030_joins CASCADE;
CREATE SCHEMA day030_joins;

-- One student can have many enrollment records.
CREATE TABLE day030_joins.students (
	student_id INTEGER PRIMARY KEY,
	name VARCHAR(100) NOT NULL
);

-- One course can appear in many enrollment records.
CREATE TABLE day030_joins.courses (
	course_id INTEGER PRIMARY KEY,
	name VARCHAR(100) NOT NULL
);

-- This junction table represents the many-to-many student/course relationship.
CREATE TABLE day030_joins.enrollments (
	student_id INTEGER NOT NULL REFERENCES day030_joins.students(student_id),
	course_id INTEGER NOT NULL REFERENCES day030_joins.courses(course_id),
	PRIMARY KEY (student_id, course_id)
);

-- Insert the lesson's student, course, and enrollment data.
INSERT INTO day030_joins.students (student_id, name) VALUES
	(1, 'Rahul'),
	(2, 'Priya'),
	(3, 'Mayank'),
	(4, 'Amit');

INSERT INTO day030_joins.courses (course_id, name) VALUES
	(101, 'Python'),
	(102, 'Docker'),
	(103, 'PostgreSQL');

INSERT INTO day030_joins.enrollments (student_id, course_id) VALUES
	(1, 101),
	(1, 102),
	(2, 101),
	(3, 103);

```

**Observed row counts:** `students = 4`, `courses = 3`, `enrollments = 4`.

## Exercise 3 — INNER JOIN

```sql
-- INNER JOIN keeps only students with a matching enrollment and course.
SELECT s.name AS student_name, c.name AS course_name
FROM day030_joins.students AS s
INNER JOIN day030_joins.enrollments AS e ON e.student_id = s.student_id
INNER JOIN day030_joins.courses AS c ON c.course_id = e.course_id
ORDER BY s.student_id, c.course_id;
```

| Student Name | Course Name |
| ------------ | ----------- |
| Rahul        | Python      |
| Rahul        | Docker      |
| Priya        | Python      |
| Mayank       | PostgreSQL  |

## Exercise 4 — LEFT JOIN

```sql
-- LEFT JOIN preserves every student, even when no enrollment matches.
SELECT s.name AS student_name, c.name AS course_name
FROM day030_joins.students AS s
LEFT JOIN day030_joins.enrollments AS e ON e.student_id = s.student_id
LEFT JOIN day030_joins.courses AS c ON c.course_id = e.course_id
ORDER BY s.student_id, c.course_id NULLS LAST;
```

| Student Name | Course Name |
| ------------ | ----------- |
| Rahul        | Python      |
| Rahul        | Docker      |
| Priya        | Python      |
| Mayank       | PostgreSQL  |
| Amit         | `NULL`      |

**Why did Amit appear?** `LEFT JOIN` preserves every row from its left-side table (`students`). Since Amit has no matching row in `enrollments`, the right-side course columns are `NULL`.

## Exercise 5 — Find Students With No Courses

```sql
-- An unmatched left-join row has no enrollment key.
SELECT s.name AS student_name
FROM day030_joins.students AS s
LEFT JOIN day030_joins.enrollments AS e ON e.student_id = s.student_id
WHERE e.student_id IS NULL
ORDER BY s.student_id;
```

| Student Name |
| ------------ |
| Amit         |

This pattern applies to customers with no orders, employees with no assignments, users with no subscriptions, and products with no sales.

## Exercise 6 — Count Enrollments Per Student

```sql
-- Count the nullable enrollment key so an unmatched student receives zero.
SELECT s.name AS student_name, COUNT(e.student_id) AS course_count
FROM day030_joins.students AS s
LEFT JOIN day030_joins.enrollments AS e ON e.student_id = s.student_id
GROUP BY s.student_id, s.name
ORDER BY s.student_id;
```

| Student Name | Course Count |
| ------------ | -----------: |
| Rahul        |            2 |
| Priya        |            1 |
| Mayank       |            1 |
| Amit         |            0 |

## Exercise 7 — HAVING Clause

```sql
-- HAVING filters groups after GROUP BY and COUNT have been evaluated.
SELECT s.name AS student_name
FROM day030_joins.students AS s
INNER JOIN day030_joins.enrollments AS e ON e.student_id = s.student_id
GROUP BY s.student_id, s.name
HAVING COUNT(e.course_id) > 1
ORDER BY s.student_id;
```

| Student Name |
| ------------ |
| Rahul        |

## Exercise 8 — Multi-Table JOIN

```sql
-- Follow the relationship chain: students -> enrollments -> courses.
SELECT s.name AS student_name, c.name AS course_name
FROM day030_joins.students AS s
JOIN day030_joins.enrollments AS e ON s.student_id = e.student_id
JOIN day030_joins.courses AS c ON e.course_id = c.course_id
ORDER BY s.student_id, c.course_id;
```

| Student Name | Course Name |
| ------------ | ----------- |
| Rahul        | Python      |
| Rahul        | Docker      |
| Priya        | Python      |
| Mayank       | PostgreSQL  |

## Exercise 9 — Repository Connection

No mini-project code was changed for this exercise. The exercise sheet explicitly recommends a separate practice schema when the application does not yet contain a suitable relationship table. The current project repository correctly hides SQL behind its repository abstraction, but adding course/enrollment behavior would require a broader domain decision, migrations, models, service methods, and API contracts beyond this SQL lesson.

The conceptual repository method would be:

```python
def get_students_with_courses(self):
	"""Return student/course relationships from the repository layer."""
```

Its SQL would remain inside the repository implementation, while the service would call `get_students_with_courses()` without knowing about JOIN syntax, foreign keys, or grouping.

## Validation

The isolated schema was validated after execution:

- Tables: `day030_joins.students`, `day030_joins.courses`, `day030_joins.enrollments`
- Primary keys: all three tables
- Foreign keys: `enrollments.student_id` → `students.student_id`; `enrollments.course_id` → `courses.course_id`
- All exercise outputs matched the expected results.
