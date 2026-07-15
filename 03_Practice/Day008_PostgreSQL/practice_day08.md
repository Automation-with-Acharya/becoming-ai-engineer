# Day 008 - PostgreSQL CRUD Practice

## Setup

Create the database and table if it does not exist:

```sql
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    city VARCHAR(100) NOT NULL
);
```

Insert sample records:

```sql
INSERT INTO students (id, name, age, city) VALUES
(1, 'Mayank', 27, 'Gandhinagar'),
(2, 'Rahul', 25, 'Ahmedabad'),
(3, 'Priya', 24, 'Surat')
ON CONFLICT (id) DO NOTHING;
```

## Experiment 1

Connect to PostgreSQL and retrieve all students.

```python
import psycopg

conn = psycopg.connect(
    dbname="student_db",
    user="postgres",
    password="password@postgres",
    host="localhost",
    port="5432",
)

with conn.cursor() as cur:
    cur.execute("SELECT id, name, age, city FROM students ORDER BY id")
    rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()
```

## Experiment 2

Insert a new student.

```python
import psycopg

conn = psycopg.connect(
    dbname="student_db",
    user="postgres",
    password="password@postgres",
    host="localhost",
    port="5432",
)

with conn.cursor() as cur:
    cur.execute(
        "INSERT INTO students (id, name, age, city) VALUES (%s, %s, %s, %s)",
        (4, "Aisha", 22, "Mumbai"),
    )

conn.commit()
conn.close()
```

## Experiment 3

Update a student's city.

```python
import psycopg

conn = psycopg.connect(
    dbname="student_db",
    user="postgres",
    password="password@postgres",
    host="localhost",
    port="5432",
)

with conn.cursor() as cur:
    cur.execute(
        "UPDATE students SET city = %s WHERE id = %s",
        ("Delhi", 2),
    )

conn.commit()
conn.close()
```

## Experiment 4

Delete a student.

```python
import psycopg

conn = psycopg.connect(
    dbname="student_db",
    user="postgres",
    password="password@postgres",
    host="localhost",
    port="5432",
)

with conn.cursor() as cur:
    cur.execute(
        "DELETE FROM students WHERE id = %s",
        (4,),
    )

conn.commit()
conn.close()
```

## Experiment 5

Retrieve all students again.

```python
import psycopg

conn = psycopg.connect(
    dbname="student_db",
    user="postgres",
    password="password@postgres",
    host="localhost",
    port="5432",
)

with conn.cursor() as cur:
    cur.execute("SELECT id, name, age, city FROM students ORDER BY id")
    rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()
```

## Experiment 6

Rewrite each query using parameterized SQL.

```python
import psycopg

conn = psycopg.connect(
    dbname="student_db",
    user="postgres",
    password="password@postgres",
    host="localhost",
    port="5432",
)

with conn.cursor() as cur:
    cur.execute("SELECT * FROM students WHERE id = %s", (1,))
    print(cur.fetchone())

    cur.execute("SELECT * FROM students WHERE city = %s ORDER BY id", ("Delhi",))
    print(cur.fetchall())

    cur.execute(
        "INSERT INTO students (id, name, age, city) VALUES (%s, %s, %s, %s)",
        (5, "Zara", 23, "Chennai"),
    )

    cur.execute("DELETE FROM students WHERE id = %s", (5,))

conn.commit()
conn.close()
```

## Notes

- Always use parameterized SQL with `%s` placeholders.
- Never build SQL using string concatenation.
- Use `conn.commit()` after inserts, updates, and deletes.
