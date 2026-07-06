# Day 003 — Exception Handling & File Handling

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 06 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand why exceptions occur.
- Handle runtime errors gracefully.
- Use `try`, `except`, `else`, and `finally`.
- Read, write, and append data to files.
- Use `with open()` correctly.
- Build applications that preserve data permanently.
- Follow Python best practices for file operations.

---

# 1. Exception Handling

## Definition

An **exception** is a runtime error that interrupts the normal execution of a program.

Instead of allowing the program to crash, Python provides mechanisms to catch and handle these errors gracefully.

---

## Why Exception Handling?

Without exception handling:

- Program crashes.
- Poor user experience.
- Data loss is possible.
- Difficult debugging.

With exception handling:

- Program continues safely.
- Better user experience.
- Cleaner error messages.
- Easier maintenance.

---

# 2. try Block

The `try` block contains code that might raise an exception.

```python
try:
    number = int(input("Enter a number: "))
    print(100 / number)
```

If no exception occurs, the program continues normally.

---

# 3. except Block

The `except` block executes only when an exception occurs.

```python
try:
    number = int(input())

except ValueError:
    print("Invalid number.")
```

---

## Multiple Exceptions

```python
try:
    number = int(input())
    print(100 / number)

except ValueError:
    print("Please enter a valid integer.")

except ZeroDivisionError:
    print("Division by zero is not allowed.")
```

Python executes only the first matching exception block.

---

# 4. else Block

The `else` block executes only when **no exception occurs**.

```python
try:
    age = int(input("Age: "))

except ValueError:
    print("Invalid age.")

else:
    print("Age accepted.")
```

---

# 5. finally Block

The `finally` block **always executes**, regardless of whether an exception occurred.

```python
try:
    file = open("students.txt")

except FileNotFoundError:
    print("File not found.")

finally:
    print("Program finished.")
```

Typical uses:

- Closing files
- Closing database connections
- Releasing resources
- Cleanup operations

---

# Exception Flow

```text
try
   │
   ├── No Exception ──► else
   │                     │
   └─────────────────────┘
             │
             ▼
         finally

OR

try
   │
Exception
   │
   ▼
except
   │
   ▼
finally
```

---

# Common Python Exceptions

| Exception         | Cause                                |
| ----------------- | ------------------------------------ |
| ValueError        | Invalid data type conversion         |
| ZeroDivisionError | Division by zero                     |
| IndexError        | Invalid list index                   |
| KeyError          | Dictionary key not found             |
| TypeError         | Invalid operation between data types |
| FileNotFoundError | File does not exist                  |
| PermissionError   | Access denied                        |

---

# Best Practices

✅ Catch specific exceptions.

Good:

```python
except ValueError:
```

Avoid:

```python
except:
```

A bare `except` hides unexpected bugs and makes debugging difficult.

---

# 6. File Handling

## Definition

File handling allows a program to store and retrieve information permanently from the file system.

Without files:

- Data is lost when the program exits.

With files:

- Data persists even after closing the application.

---

# File Modes

| Mode   | Purpose                       |
| ------ | ----------------------------- |
| `"r"`  | Read existing file            |
| `"w"`  | Write (creates or overwrites) |
| `"a"`  | Append to existing file       |
| `"x"`  | Create a new file only        |
| `"r+"` | Read and write                |

---

# Reading a File

```python
file = open("students.txt", "r")

content = file.read()

print(content)

file.close()
```

---

# Writing a File

```python
file = open("students.txt", "w")

file.write("Mayank\n")
file.write("Rahul\n")

file.close()
```

`"w"` overwrites existing content.

Use with caution.

---

# Appending to a File

```python
file = open("students.txt", "a")

file.write("Priya\n")

file.close()
```

`"a"` preserves existing data and adds new content.

---

# Reading Line by Line

```python
with open("students.txt", "r") as file:

    for line in file:
        print(line.strip())
```

Using `strip()` removes trailing newline characters.

---

# 7. with open()

## Preferred Approach

```python
with open("students.txt", "r") as file:
    content = file.read()

print(content)
```

---

## Why use `with`?

Python automatically closes the file after the block finishes, even if an exception occurs.

Benefits:

- Cleaner code
- Safer resource management
- No need to call `close()`
- Recommended in professional projects

---

# Combining File Handling with Exception Handling

```python
filename = input("Enter file name: ")

try:

    with open(filename, "r") as file:
        print(file.read())

except FileNotFoundError:
    print("File not found.")

except PermissionError:
    print("Permission denied.")

finally:
    print("Operation completed.")
```

This is a common real-world pattern.

---

# Best Practices

✅ Always use `with open()`.

✅ Catch only the exceptions you expect.

✅ Use append mode when preserving existing data.

✅ Close resources automatically using context managers.

✅ Store user-facing messages inside exception blocks.

---

# Common Mistakes

❌ Using a bare `except:`.

❌ Forgetting to close files.

❌ Using `"w"` when `"a"` is required.

❌ Assuming a file always exists.

❌ Ignoring possible file permissions.

---

# Interview Questions

### Q1. What is an exception?

A runtime error that interrupts normal program execution.

---

### Q2. Difference between `try`, `except`, `else`, and `finally`?

- `try` → Risky code
- `except` → Handle errors
- `else` → Executes only if no exception occurs
- `finally` → Always executes

---

### Q3. Why use `with open()` instead of `open()`?

Because it automatically closes the file and manages resources safely.

---

### Q4. Difference between `"w"` and `"a"`?

- `"w"` overwrites the file.
- `"a"` appends to the existing file.

---

### Q5. Why should we avoid a bare `except:`?

It catches every exception, including unexpected programming errors, making debugging much harder.

---

# Real-World Usage

Imagine an enterprise banking application.

When a customer transfers money:

- User input must be validated.
- Any errors should be handled gracefully.
- Transaction logs must be saved to permanent storage.
- Files and database connections must always be closed properly.

Exception handling and resource management ensure the application remains stable and reliable.

---

# Cheat Sheet

```python
try:
    ...
except ValueError:
    ...
except FileNotFoundError:
    ...
else:
    ...
finally:
    ...

with open("file.txt", "r") as file:
    data = file.read()

with open("file.txt", "w") as file:
    file.write("Hello")

with open("file.txt", "a") as file:
    file.write("World")
```

---

# Key Takeaways

- Exceptions prevent applications from crashing unexpectedly.
- Handle specific exceptions instead of using a generic `except`.
- `finally` always executes and is ideal for cleanup.
- File handling allows data to persist beyond program execution.
- `"r"` reads, `"w"` overwrites, and `"a"` appends.
- `with open()` is the professional and recommended way to work with files.
- Combining exception handling with file operations makes applications more robust and user-friendly.

---

# Revision Checklist

- [ ] Understand the purpose of exception handling.
- [ ] Know when to use `try`, `except`, `else`, and `finally`.
- [ ] Can identify common Python exceptions.
- [ ] Can read, write, and append files.
- [ ] Always use `with open()` for file operations.
- [ ] Can explain the difference between file modes.
- [ ] Can combine file handling with exception handling confidently.

---

# Tomorrow's Preview

- Object-Oriented Programming (OOP)
- Classes & Objects
- Constructors (`__init__`)
- Instance Variables
- Methods
- Refactoring the Student Management CLI using OOP
