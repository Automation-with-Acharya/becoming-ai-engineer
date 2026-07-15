# Practice - Day 006

## Database Design & Relationships

> **Project ₹50L | Day 006**

---

# Goal

Understand how relational databases are designed before working with a real PostgreSQL database.

---

# Example 1 - Students Table

```sql
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    city VARCHAR(100)
);
```

---

# Example 2 - Insert Students

```sql
INSERT INTO students
VALUES
(1, 'Mayank', 27, 'Gandhinagar'),
(2, 'Rahul', 25, 'Ahmedabad'),
(3, 'Priya', 24, 'Surat');
```

---

# Example 3 - Courses Table

```sql
CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100),
    duration INT
);
```

---

# Example 4 - Insert Courses

```sql
INSERT INTO courses
VALUES
(101, 'Python', 30),
(102, 'SQL', 20),
(103, 'FastAPI', 25);
```

---

# Example 5 - Enrollments Table

```sql
CREATE TABLE enrollments (
    enrollment_id INT PRIMARY KEY,
    student_id INT,
    course_id INT,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
);
```

---

# Example 6 - Insert Enrollments

```sql
INSERT INTO enrollments
VALUES
(1, 1, 101),
(2, 1, 102),
(3, 2, 101),
(4, 3, 103);
```

---

# Example 7 - Retrieve Students

```sql
SELECT *
FROM students;
```

---

# Example 8 - Students Older Than 25

```sql
SELECT *
FROM students
WHERE age > 25;
```

---

# Example 9 - Update Student City

```sql
UPDATE students
SET city = 'Ahmedabad'
WHERE student_id = 1;
```

---

# Example 10 - Delete Student

```sql
DELETE FROM students
WHERE student_id = 3;
```

---

# Practice Challenge

Design a small **Library Management Database**.

Create these tables:

- books
- members
- borrow_history

Suggested columns:

### books

- book_id
- title
- author
- price

### members

- member_id
- name
- city

### borrow_history

- borrow_id
- member_id
- book_id
- borrow_date

Then write:

- CREATE TABLE statements
- INSERT statements
- SELECT queries
- UPDATE query
- DELETE query

---

# Self-Check Questions

- Why do we need a Primary Key?
- Why is `student_id` stored in `enrollments` instead of the student's name?
- Why shouldn't course names be stored directly in the `students` table?
- What problem does a Foreign Key solve?
- When would you create a separate table instead of adding more columns?

---

# Revision Checklist

- [ ] Can create related tables.
- [ ] Understand Primary Keys and Foreign Keys.
- [ ] Can identify One-to-One, One-to-Many, and Many-to-Many relationships.
- [ ] Can write basic CRUD operations.
- [ ] Ready to execute these queries in PostgreSQL.
