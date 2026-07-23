# Student Management CLI

## Objective

This project is a simple command-line application for managing student records. It helps practice Python concepts such as functions, dictionaries, loops, input handling, file operations, and basic error handling.

## New Features

- Add a student with an automatically generated unique ID
- View all stored students with their IDs and names
- Search for a student by ID or name
- Delete a student by ID or name
- Save student data to a file so records persist between program runs
- Use a menu-driven interface for easy navigation
- Handle invalid input and missing files gracefully

## File Structure

```text
MiniProject/
├── Student_Management_CLI.py
├── README.md
└── students.txt
```

- Student_Management_CLI.py: Main program with all menu options and student operations
- README.md: Project overview and usage notes
- students.txt: File used to store student data persistently

## Future Improvements

- Add an option to update or edit existing student information
- Improve search to support partial name matching
- Add sorting options when viewing students
- Add confirmation prompts before deleting a student
- Improve the interface with better validation and clearer messages
