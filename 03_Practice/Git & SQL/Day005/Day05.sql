-- =====================================================
-- Student Database Management Script
-- Purpose: Demonstrates basic SQL operations including 
--          CREATE, INSERT, SELECT, UPDATE, and DELETE
-- Author: Mayank Acharya
-- Date: Day 005 - Git & SQL Fundamentals
-- =====================================================

-- Step 1: Create the database named 'student_db'
-- This creates a new database container to store all related tables and data
CREATE DATABASE student_db;

-- Step 2: Select the 'student_db' database for use
-- All subsequent SQL commands will execute within this database context
USE student_db;

-- Step 3: Create the 'students' table structure
-- This defines the schema with 4 columns to store student information
-- - id: Primary key (unique identifier for each student, cannot be NULL or duplicate)
-- - name: Variable character field (up to 100 characters) to store student names
-- - age: Integer field to store student age
-- - city: Variable character field (up to 100 characters) to store student city
CREATE TABLE students (
    id INT primary key,               -- Unique identifier for each student record
    name VARCHAR (100),               -- Student's full name (max 100 characters)
    age INT,                          -- Student's age in years
    city VARCHAR (100)                -- Student's residential city (max 100 characters)
);

-- Step 4: Insert initial student records into the table
-- Adding 3 student records with their respective details
-- These are sample data entries for testing and demonstration purposes
INSERT INTO students VALUES
(1, 'Mayank', 27, 'Gandhinagar'),     -- Record 1: Mayank, age 27, from Gandhinagar
(2, 'Rahul', 25, 'Ahmedabad'),        -- Record 2: Rahul, age 25, from Ahmedabad
(3, 'Priya', 24, 'Surat');            -- Record 3: Priya, age 24, from Surat

-- Step 5: Retrieve and display all records from the students table
-- This SELECT statement without WHERE clause returns the entire table contents
-- Useful for verification and inspection of all stored data
SELECT * FROM students;

-- Step 6: Query students with age greater than 25
-- This demonstrates the WHERE clause for filtering records based on conditions
-- Returns only students whose age is strictly greater than 25
-- In this case: Mayank (27) and Rahul (25 - NOT included, needs > not >=)
SELECT * FROM students WHERE age > 25;

-- Step 7: Update a specific student's age
-- This demonstrates the UPDATE statement for modifying existing records
-- The WHERE clause ensures only the target record (id = 2, Rahul) is modified
-- Rahul's age is changed from 25 to 26
UPDATE students
SET age = 26                          -- New value for the age column
WHERE id = 2;                         -- Condition: only update where id equals 2 (Rahul)

-- Step 8: Insert additional student records into the table
-- Adding 3 more student records with similar structure to previous INSERT
-- These records demonstrate handling of repeated/duplicate-like data
INSERT INTO students VALUES
(4, 'abc', 27, 'Gandhinagar'),        -- Record 4: Student 'abc', age 27, from Gandhinagar
(5, 'xyz', 25, 'Ahmedabad'),          -- Record 5: Student 'xyz', age 25, from Ahmedabad
(6, 'ABC', 24, 'Surat');              -- Record 6: Student 'ABC', age 24, from Surat

-- Step 9: Delete a specific student record from the table
-- This demonstrates the DELETE statement for removing records
-- The WHERE clause ensures only the target record (id = 4, 'abc') is deleted
-- After this operation, the 'abc' record will be completely removed from the database
DELETE FROM students
WHERE id = 4;                         -- Condition: delete only the record where id equals 4


