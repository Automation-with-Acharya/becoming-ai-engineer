
-- ==================================================
-- DATABASE SETUP
-- ==================================================
-- CREATE DATABASE student_db;
-- USE student_db;

-- ==================================================
-- STUDENTS TABLE: Store student information
-- ==================================================
CREATE TABLE students (
    id INT primary key,               -- Unique identifier for each student record
    name VARCHAR (100),               -- Student's full name (max 100 characters)
    age INT,                          -- Student's age in years
    city VARCHAR (100)                -- Student's residential city (max 100 characters)
);

-- Initial student records
INSERT INTO students VALUES
(1, 'Mayank', 27, 'Gandhinagar'),     -- Record 1: Mayank, age 27, from Gandhinagar
(2, 'Rahul', 25, 'Ahmedabad'),        -- Record 2: Rahul, age 25, from Ahmedabad
(3, 'Priya', 24, 'Surat');            -- Record 3: Priya, age 24, from Surat


SELECT * FROM students;

-- Additional student records
INSERT INTO students VALUES
(4, 'abc', 27, 'Gandhinagar'),        -- Record 4: Student 'abc', age 27, from Gandhinagar
(5, 'xyz', 25, 'Ahmedabad'),          -- Record 5: Student 'xyz', age 25, from Ahmedabad
(6, 'ABC', 24, 'Surat');              -- Record 6: Student 'ABC', age 24, from Surat

SELECT * FROM students;

-- ==================================================
-- COURSES TABLE: Store course information
-- ==================================================
CREATE TABLE courses (
    course_id INT primary key,         -- Unique identifier for each course record
    course_name VARCHAR (100),         -- Name of the course (max 100 characters)
    duration INT                       -- Duration of the course in weeks
);

-- Course catalog
INSERT INTO courses VALUES
(1, 'Python Programming', 12),        -- Course 1: Python Programming, duration 12 weeks
(2, 'Data Science', 16),              -- Course 2: Data Science, duration 16 weeks
(3, 'Web Development', 10);           -- Course 3: Web Development, duration 10 weeks

SELECT * FROM Courses;

-- ==================================================
-- ENROLLMENTS TABLE: Link students to courses
-- ==================================================
CREATE TABLE enrollments (
    enrollment_id INT primary key,      -- Unique identifier for each enrollment record
    student_id INT,                     -- Foreign key referencing the students table
    course_id INT,                      -- Foreign key referencing the courses table
    enrollment_date DATE,               -- Date of enrollment in the course
    FOREIGN KEY (student_id) REFERENCES students(id),  -- Establishing relationship with students table
    FOREIGN KEY (course_id) REFERENCES courses(course_id)  -- Establishing relationship with courses table
);

-- Enrollment records linking students to courses
INSERT INTO enrollments VALUES
(1, 1, 1, '2024-01-15'),               -- Enrollment 1: Mayank enrolled in Python Programming on Jan 15, 2024
(2, 2, 2, '2024-02-20'),               -- Enrollment 2: Rahul enrolled in Data Science on Feb 20, 2024
(3, 3, 3, '2024-03-10'),               -- Enrollment 3: Priya enrolled in Web Development on Mar 10, 2024
(4, 1, 2, '2024-04-05'),               -- Enrollment 4: Mayank enrolled in Data Science on Apr 5, 2024
(5, 2, 3, '2024-05-12'),               -- Enrollment 5: Rahul enrolled in Web Development on May 12, 2024
(6, 3, 1, '2024-06-18');               -- Enrollment 6: Priya enrolled in Python Programming on Jun 18, 2024


SELECT * FROM enrollments;

-- ==================================================
-- DATA MODIFICATION EXAMPLES
-- ==================================================
-- Update example: Modify student age
UPDATE students
SET age = 26                          -- New value for the age column
WHERE id = 2;                         -- Condition: only update where id equals 2 (Rahul)

-- Delete example: Remove student record
DELETE FROM students
WHERE id = 4;                         -- Condition: delete only the record where id equals 4

