# Student Management CLI

## Objective

This project is a simple command-line application for managing student records using Python and PostgreSQL. It helps practice Python concepts such as functions, loops, input handling, and database operations while also introducing basic database integration.

## New Features

- Add a student with an automatically generated unique ID
- View all stored students with their IDs and names
- Search for a student by ID or name
- Improve search to support partial name matching more clearly
- Delete a student by ID or name
- Store student data in a PostgreSQL database instead of a text file
- Use a reusable DatabaseHelper class to keep database code organized
- Use parameterized SQL queries to make database operations safer
- Handle empty input and invalid menu choices gracefully

## Project Structure

```text
MiniProject/
├── Student_Management_CLI.py
├── database_helper.py
├── README.md
```

- Student_Management_CLI.py: Main program with the menu and student operations
- database_helper.py: Reusable helper class for connecting to PostgreSQL and running queries
- README.md: Project overview and usage notes

## How to Run

1. Make sure PostgreSQL is running.
2. Create or use a database named student_db.
3. Run the program:

```bash
python Student_Management_CLI.py
```

## Future Improvements

- Add an option to update or edit existing student information
- Add sorting and filtering options when viewing students
- Add confirmation prompts before deleting a student
- Improve the interface with better validation and clearer messages
