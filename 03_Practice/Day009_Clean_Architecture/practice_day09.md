# Day 09 Practice: Clean Architecture Basics

## Exercise 1

### Draw the architecture evolution

#### Day 3

```text
CLI

↓

students.txt
```

#### Day 8

```text
CLI

↓

Database Helper

↓

PostgreSQL
```

#### Day 9

```text
CLI

↓

Service Layer

↓

Repository

↓

Database Helper

↓

PostgreSQL
```

### Explanation

- Day 3: The app was simple and directly used a text file.
- Day 8: The app became more structured by adding a database helper and using PostgreSQL.
- Day 9: The design became cleaner by separating responsibilities into layers.

---

## Exercise 2

For each layer, write:

- Responsibility
- What it should NOT do

### 1. CLI / Presentation Layer

#### Should:

- Take user input
- Display output to the user
- Call the service layer

#### Should NOT:

- Contain business rules
- Connect directly to the database
- Perform complex data logic

### 2. Service Layer

#### Should:

- Handle application logic
- Orchestrate actions between layers
- Validate business rules in a simple way

#### Should NOT:

- Execute raw SQL directly
- Print to the screen
- Talk directly to the user interface

### 3. Repository Layer

#### Should:

- Save and fetch data
- Execute database queries
- Return data to the service layer

#### Should NOT:

- Print to screen
- Ask for user input
- Contain business rules like "student must be above 18"

### 4. Database Helper

#### Should:

- Create connections
- Run database operations
- Help the repository communicate with PostgreSQL

#### Should NOT:

- Decide business logic
- Handle UI tasks
- Replace the repository entirely

---

## Exercise 3

### 1. What is Separation of Concerns?

Separation of Concerns means dividing a program into different parts so each part has one main responsibility. For example, the UI handles input/output, the service layer handles business logic, and the repository handles data access.

### 2. What is Repository Pattern?

The Repository Pattern is a design pattern that provides a clean way to access data. It hides the details of how data is stored and lets the application work with a simple interface.

### 3. Why use a Service Layer?

A Service Layer is used to hold the main business logic and coordinate actions between the UI and data layer. It keeps the code organized and makes it easier to maintain.

### 4. Difference between Repository and Database Helper?

- Repository: focuses on data operations for a specific entity, such as student data.
- Database Helper: focuses on the technical connection and execution support for the database.

In simple words, the repository is more business-oriented, while the database helper is more technical.

### 5. What is Clean Architecture?

Clean Architecture is a way of designing software so that the core business rules stay independent from frameworks, databases, and UI. It makes the code easier to test, modify, and scale.

---

## Exercise 4

### Future project structure

```text
StudentManagement/

├── app.py
├── models/
│   └── student.py
├── services/
│   └── student_service.py
├── repositories/
│   └── student_repository.py
├── database/
│   └── database_helper.py
├── sql/
│   └── schema.sql
└── README.md
```

### Suggested role of each folder

- app.py: main entry point of the program
- models/: defines the Student model or data structure
- services/: contains business logic
- repositories/: handles database operations
- database/: contains database connection helpers
- sql/: stores SQL schema and queries
- README.md: explains how the project works

This is the architecture we will gradually build over the coming days.
