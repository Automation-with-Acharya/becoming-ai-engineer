# PostgreSQL Day 007 - Python + PostgreSQL Practice

This folder contains a beginner-friendly PostgreSQL practice project focused on connecting Python to a PostgreSQL database using the `psycopg` library.

## Learning Objectives

By the end of this practice session, you should be able to:

- understand the basic architecture of PostgreSQL,
- connect Python applications to a PostgreSQL database,
- retrieve data from a table using SQL queries,
- print database records in the terminal,
- and close database connections properly.

## Project Overview

This folder demonstrates how a Python script can interact with PostgreSQL using a client/server architecture. The example connects to a local PostgreSQL database named `student_db`, fetches student data from the `students` table, and displays the results.

## Files in This Folder

- `connect_db.py` - A simple script that establishes a basic PostgreSQL connection.
- `database_demo.py` - The main demonstration script that connects to PostgreSQL, retrieves all students, prints them, and closes the connection properly.
- `practice.py` - A small test script to verify that the `psycopg` package is installed and working.
- `README.md` - This documentation file.

## Prerequisites

Before running the scripts, make sure you have:

- PostgreSQL installed and running locally,
- a database named `student_db`,
- a `students` table with sample records,
- and the `psycopg` Python package installed in your environment.

## Database Setup

If you have not created the database and table yet, you can use SQL similar to the following:

```sql
CREATE DATABASE student_db;

CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    city VARCHAR(100)
);

INSERT INTO students VALUES
(1, 'Mayank', 27, 'Gandhinagar'),
(2, 'Rahul', 25, 'Ahmedabad'),
(3, 'Priya', 24, 'Surat');
```

## Install Dependencies

Install the PostgreSQL Python driver using:

```bash
pip install psycopg
```

If you are using a virtual environment, make sure it is activated first.

## Run the Demo

From the project folder, run:

```bash
python database_demo.py
```

You should see output similar to:

```text
✅ Connected to PostgreSQL successfully

📋 Student Records:
ID: 1, Name: Mayank, Age: 27, City: Gandhinagar
ID: 2, Name: Rahul, Age: 26, City: Ahmedabad
...

🔒 Connection closed successfully
```

## Example Code Summary

The main script demonstrates the following steps:

1. Import the `psycopg` library.
2. Connect to the PostgreSQL database using connection parameters.
3. Create a cursor for executing SQL.
4. Run a `SELECT` query to fetch all students.
5. Print each record to the console.
6. Close the connection safely in a `finally` block.

## Notes

- This project is intended for learning and practice.
- Make sure your PostgreSQL server is running before executing the scripts.
- If authentication fails, verify your username, password, host, and port settings.

## Conclusion

This Day 007 exercise helps you understand the basics of connecting Python to PostgreSQL and retrieving data using SQL. It is a solid starting point for building more advanced database-driven applications later.
