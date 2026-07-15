# Part 2 - SQL Basics

Imagine we have the following table:

## students

| id  | name   | age | city        |
| --- | ------ | --- | ----------- |
| 1   | Mayank | 27  | Gandhinagar |
| 2   | Rahul  | 25  | Ahmedabad   |
| 3   | Priya  | 24  | Surat       |

---

# 1. Create Database

```sql
CREATE DATABASE student_db;
```

---

# 2. Use Database

```sql
USE student_db;
```

---

# 3. Create Table

```sql
CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    city VARCHAR(100)
);
```

---

# 4. Insert Records

```sql
INSERT INTO students
VALUES
(1, 'Mayank', 27, 'Gandhinagar'),
(2, 'Rahul', 25, 'Ahmedabad'),
(3, 'Priya', 24, 'Surat');
```

---

# 5. View All Records

```sql
SELECT * FROM students;
```

---

# 6. View Specific Columns

```sql
SELECT
    name,
    city
FROM students;
```

---

# 7. Filter Records

```sql
SELECT *
FROM students
WHERE age > 25;
```

---

# 8. Update Record

```sql
UPDATE students
SET city = 'Ahmedabad'
WHERE id = 1;
```

---

# 9. Delete Record

```sql
DELETE FROM students
WHERE id = 3;
```

---

# 10. Count Records

```sql
SELECT COUNT(*)
FROM students;
```

---

# Bonus Practice Queries

## Students from Ahmedabad

```sql
SELECT *
FROM students
WHERE city = 'Ahmedabad';
```

---

## Students Older Than 24

```sql
SELECT *
FROM students
WHERE age > 24;
```

---

## Sort by Age

```sql
SELECT *
FROM students
ORDER BY age;
```

---

## Sort by Name

```sql
SELECT *
FROM students
ORDER BY name;
```

---

## Highest Age

```sql
SELECT MAX(age)
FROM students;
```

---

## Lowest Age

```sql
SELECT MIN(age)
FROM students;
```

---

## Average Age

```sql
SELECT AVG(age)
FROM students;
```

---

## Distinct Cities

```sql
SELECT DISTINCT city
FROM students;
```

---

# SQL Keywords Learned Today

- CREATE DATABASE
- USE
- CREATE TABLE
- INSERT
- SELECT
- WHERE
- UPDATE
- DELETE
- ORDER BY
- COUNT
- MAX
- MIN
- AVG
- DISTINCT

---

# Interview Questions

### Q1. What is a database?

A database is an organized collection of data that can be stored, managed, and retrieved efficiently.

---

### Q2. Difference between a table and a database?

- **Database**: A collection of related tables.
- **Table**: A collection of rows and columns storing related data.

---

### Q3. Difference between `DELETE` and `DROP`?

- `DELETE` removes data but keeps the table.
- `DROP` removes the entire table structure and its data.

---

### Q4. What is a Primary Key?

A Primary Key uniquely identifies each row in a table and cannot contain duplicate or `NULL` values.

---

### Q5. Difference between `WHERE` and `ORDER BY`?

- `WHERE` filters rows.
- `ORDER BY` sorts rows.

---

# Practice Challenge

Create a new table called **employees** with the following columns:

- employee_id
- name
- department
- salary
- city

Then write SQL queries to:

1. Insert five employees.
2. Display all employees.
3. Display only employee names.
4. Find employees with salary greater than 50000.
5. Update one employee's city.
6. Delete one employee.
7. Count the total number of employees.
8. Display employees sorted by salary (highest first).
