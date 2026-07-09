-- =====================================================
-- Employees Table Management System
-- Purpose: Demonstrates comprehensive SQL operations including
--          CREATE TABLE, INSERT, SELECT (various filters),
--          UPDATE, DELETE, COUNT, and ORDER BY clauses
-- Author: Mayank Acharya
-- Date: Day 005 - SQL Practice Exercises
-- =====================================================

-- =====================================================
-- SECTION 1: CREATE TABLE
-- =====================================================
-- Create a new table called 'employees' to store employee information
-- This table will store comprehensive details about company employees
-- Primary key is employee_id to uniquely identify each employee
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,      -- Unique identifier for each employee (cannot be NULL or duplicate)
    name VARCHAR(100),                -- Employee's full name (maximum 100 characters)
    department VARCHAR(50),           -- Department name where employee works (e.g., HR, IT, Sales)
    salary INT,                       -- Employee's annual salary in numeric format
    city VARCHAR(100)                 -- City where employee is located
);

-- =====================================================
-- SECTION 2: INSERT DATA
-- =====================================================
-- Insert five employee records into the employees table
-- Each INSERT statement adds a new employee with complete information
-- This sample data represents employees from different departments and cities
INSERT INTO employees VALUES
(101, 'Mayank Acharya', 'IT', 75000, 'Gandhinagar'),      -- Employee 1: IT department, salary 75000
(102, 'Rahul Kumar', 'HR', 55000, 'Ahmedabad'),           -- Employee 2: HR department, salary 55000
(103, 'Priya Singh', 'Sales', 62000, 'Surat'),            -- Employee 3: Sales department, salary 62000
(104, 'Amit Patel', 'IT', 80000, 'Bangalore'),            -- Employee 4: IT department, salary 80000
(105, 'Divya Verma', 'Finance', 45000, 'Mumbai');         -- Employee 5: Finance department, salary 45000

-- =====================================================
-- SECTION 3: QUERY 1 - DISPLAY ALL EMPLOYEES
-- =====================================================
-- Retrieve all columns and rows from the employees table
-- The SELECT * statement returns the complete dataset without any filtering
-- Useful for viewing the entire employee database at a glance
SELECT * FROM employees;

-- =====================================================
-- SECTION 4: QUERY 2 - DISPLAY ONLY EMPLOYEE NAMES
-- =====================================================
-- Retrieve only the employee names from the employees table
-- The SELECT name statement returns just one column instead of all columns
-- This demonstrates column-specific selection for focused data retrieval
SELECT name FROM employees;

-- =====================================================
-- SECTION 5: QUERY 3 - FIND EMPLOYEES WITH SALARY > 50000
-- =====================================================
-- Retrieve employees whose salary is greater than 50000
-- The WHERE clause filters records based on a specific condition
-- This query demonstrates salary-based filtering for identifying higher-paid employees
-- Expected results: Mayank (75000), Rahul (55000), Priya (62000), and Amit (80000)
SELECT * FROM employees WHERE salary > 50000;

-- =====================================================
-- SECTION 6: UPDATE - CHANGE EMPLOYEE'S CITY
-- =====================================================
-- Update a specific employee's city information
-- Changing employee_id 105 (Divya Verma) from Mumbai to Pune
-- The WHERE clause ensures only the target employee record is modified
-- This demonstrates how to modify existing records without affecting others
UPDATE employees
SET city = 'Pune'                     -- New city value
WHERE employee_id = 105;              -- Condition: only update where employee_id equals 105 (Divya Verma)

-- =====================================================
-- SECTION 7: DELETE - REMOVE ONE EMPLOYEE
-- =====================================================
-- Delete a specific employee record from the database
-- Removing employee_id 102 (Rahul Kumar) from the employees table
-- The WHERE clause ensures only the target record is deleted
-- After execution, Rahul's complete record will be permanently removed from the database
DELETE FROM employees
WHERE employee_id = 102;              -- Condition: delete only where employee_id equals 102 (Rahul Kumar)

-- =====================================================
-- SECTION 8: COUNT - TOTAL NUMBER OF EMPLOYEES
-- =====================================================
-- Count the total number of employee records in the table
-- The COUNT(*) function counts all rows in the employees table
-- This query returns a single number representing total employees
-- After deleting Rahul (employee_id 102), the count should be 4 remaining employees
SELECT COUNT(*) AS total_employees FROM employees;

-- =====================================================
-- SECTION 9: SORT BY SALARY (HIGHEST FIRST)
-- =====================================================
-- Retrieve all employees sorted by salary in descending order (highest to lowest)
-- The ORDER BY clause arranges results based on the salary column
-- The DESC (descending) keyword ensures highest salaries appear first
-- Useful for identifying top earners or salary distribution within the company
SELECT * FROM employees 
ORDER BY salary DESC;                 -- Sort by salary in descending order (highest first)
