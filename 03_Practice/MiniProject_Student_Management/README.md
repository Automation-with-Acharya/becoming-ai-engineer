# Student Management System

A modular Python application built using **Clean Architecture principles** and the **Repository Pattern** with **psycopg** (PostgreSQL).

---

## 📁 Project Structure

```text
StudentManagement/
│
├── main.py                     # Main application entry point
│
├── routers/
│   └── students.py             # Router layer: CLI menu & user interaction
│
├── services/
│   └── student_service.py      # Service layer: Encapsulates business logic
│
├── repositories/
│   └── student_repository.py   # Repository layer: PostgreSQL persistence using psycopg
│
├── database/
│   └── database_helper.py      # Database helper: Manages PostgreSQL connections & queries
│
├── models/
│   └── student.py              # Domain model: Defines Student entity (id, name)
│
├── schemas/
│   └── student_schema.py       # Schema layer: Validates and cleans student input data
│
└── README.md                   # Project documentation
```

---

## 💡 Architecture Overview

- **Models (`models/student.py`)**: Defines the core `Student` data structure (`id`, `name`).
- **Schemas (`schemas/student_schema.py`)**: Validates input parameters (ensures non-empty names).
- **Database Helper (`database/database_helper.py`)**: Manages PostgreSQL connection details and query execution using `psycopg`.
- **Repositories (`repositories/student_repository.py`)**: Handles PostgreSQL persistence and database access.
- **Services (`services/student_service.py`)**: Contains business logic separating UI from DB logic.
- **Routers (`routers/students.py`)**: Handles CLI user interaction and request dispatching.
- **Main (`main.py`)**: Bootstraps and ties all layers together.

---

## 🚀 How to Run

1. Make sure PostgreSQL is running locally on port 5432.
2. Create or use a database named `student_db`.
3. Run the application:

```bash
python main.py
```

---

## ✨ Features

- ➕ Add a student with a generated ID
- 📋 View all students
- 🔍 Search students by ID or name
- ❌ Delete a student by ID
