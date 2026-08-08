# Student Management CLI

## Objective

This project is a command-line student management application rewritten using Clean Architecture and the Repository Pattern. The application is divided into clear layers so the business logic stays separate from the database and UI code.

## Architecture Overview

- Models: defines the Student data structure
- Services: contains business logic
- Repositories: handles data persistence and database access
- Database Helper: manages PostgreSQL connection details
- CLI: handles user interaction

## Project Structure

```text
MiniProject_Student_Management/
├── app.py
├── database_helper.py
├── models/
│   └── student.py
├── repositories/
│   └── student_repository.py
├── services/
│   └── student_service.py
├── tests/
│   └── test_student_service.py
└── README_v5.md
```

## How to Run

1. Make sure PostgreSQL is running.
2. Create or use a database named student_db.
3. Run the program:

```bash
python Student_Management_CLI_v5.py
```

## Features

- Add a student with a generated ID
- View all students
- Search students by ID or name
- Delete a student by ID
- Keep business logic separate from database code

## Benefits of the New Design

- Easier to test
- Easier to extend
- Cleaner separation of responsibilities
- Better for future changes
