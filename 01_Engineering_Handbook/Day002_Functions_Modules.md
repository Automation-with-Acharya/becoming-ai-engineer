# Day 002 — Functions & Modules

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 04 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand why functions are used.
- Write reusable and modular code.
- Differentiate between parameters and arguments.
- Return values from functions.
- Understand local and global variables.
- Organize code using modules.
- Import modules correctly.
- Explain the purpose of `if __name__ == "__main__":`.

---

# 1. Functions

## Definition

A **function** is a reusable block of code designed to perform a specific task.

Instead of writing the same code multiple times, we write it once inside a function and call it whenever required.

---

## Why Functions?

Without functions:

- Code becomes repetitive.
- Difficult to maintain.
- Harder to debug.
- Poor readability.

With functions:

- Reusable
- Modular
- Easy to test
- Easy to maintain

---

## Syntax

```python
def function_name():
    # code
```

Example

```python
def greet():
    print("Hello Mayank")

greet()
```

---

# 2. Parameters vs Arguments

## Parameter

A variable defined inside the function definition.

```python
def greet(name):
    print(name)
```

`name` is a **parameter**.

---

## Argument

The actual value passed while calling the function.

```python
greet("Mayank")
```

`"Mayank"` is the **argument**.

---

## Multiple Parameters

```python
def add(a, b):
    print(a + b)

add(5, 3)
```

---

# 3. Return Values

Functions should **return** data whenever possible instead of printing everything.

Example

```python
def square(number):
    return number * number

result = square(5)

print(result)
```

---

## Why Return?

Returning values makes functions reusable.

Bad Practice

```python
def add(a, b):
    print(a + b)
```

Good Practice

```python
def add(a, b):
    return a + b
```

---

# 4. Default Parameters

A parameter can have a default value.

```python
def greet(name="Guest"):
    print(f"Hello {name}")

greet()

greet("Mayank")
```

Output

```
Hello Guest

Hello Mayank
```

---

# 5. Keyword Arguments

Arguments can be passed using parameter names.

```python
def employee(name, age):

    print(name, age)

employee(age=27, name="Mayank")
```

Order doesn't matter when using keyword arguments.

---

# 6. Local Variables

Variables created inside a function.

```python
def display():

    city = "Ahmedabad"

    print(city)
```

Characteristics:

- Accessible only inside the function.
- Destroyed after function execution.

---

# 7. Global Variables

Variables declared outside all functions.

```python
company = "Bank of America"

def display():

    print(company)
```

Global variables can be accessed inside functions.

Avoid modifying global variables unless absolutely necessary.

---

# Local vs Global

| Local Variable                  | Global Variable                  |
| ------------------------------- | -------------------------------- |
| Defined inside a function       | Defined outside functions        |
| Accessible only inside function | Accessible throughout the module |
| Temporary                       | Exists until program ends        |

---

# 8. Modules

## Definition

A **module** is simply a Python file containing functions, variables, or classes.

Example

```
math_utils.py
```

---

## Creating a Module

```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
```

---

# 9. Importing Modules

Import entire module

```python
import math_utils

print(math_utils.add(5, 3))
```

---

Import specific function

```python
from math_utils import add

print(add(5, 3))
```

---

Import everything (Not Recommended)

```python
from math_utils import *
```

Avoid this in professional projects because it pollutes the namespace.

---

# 10. if **name** == "**main**"

This is one of the most important concepts in Python.

Example

```python
def main():
    print("Career Transformation")

if __name__ == "__main__":
    main()
```

---

## What does it mean?

Every Python file has a built-in variable:

```python
__name__
```

When you run the file directly,

```python
__name__ == "__main__"
```

When the file is imported into another program,

```python
__name__
```

becomes the module name.

This prevents certain code from executing automatically during imports.

---

## Why is it useful?

Suppose

```
math_utils.py
```

contains

```python
print("Hello")
```

Every import would print "Hello".

Instead

```python
if __name__ == "__main__":
    print("Hello")
```

Now "Hello" appears only when running `math_utils.py` directly.

---

# Best Practices

✅ One function = One responsibility.

✅ Keep functions short.

✅ Use meaningful names.

```python
calculate_salary()

send_email()

validate_input()
```

Avoid

```python
abc()

temp()

x()
```

Prefer returning values over printing.

Write reusable functions.

Avoid global variables whenever possible.

---

# Common Mistakes

❌ Writing everything inside one huge function.

❌ Copy-pasting the same code.

❌ Printing instead of returning.

❌ Using too many global variables.

❌ Creating functions with 100+ lines of code.

---

# Interview Questions

### Q1. Difference between parameter and argument?

**Parameter** → Variable in function definition.

**Argument** → Actual value passed during function call.

---

### Q2. Difference between print() and return?

`print()` displays output.

`return` sends data back to the caller.

---

### Q3. What is a module?

A Python file containing reusable code.

---

### Q4. Why use modules?

- Better organization
- Reusability
- Easier maintenance
- Code separation

---

### Q5. What is `if __name__ == "__main__":`?

It ensures code runs only when the file is executed directly, not when imported as a module.

---

# Real-World Usage

Imagine you're building an online banking system.

```
authentication.py

transactions.py

database.py

notifications.py

reports.py
```

Each file is a module.

Each module contains multiple related functions.

This is exactly how enterprise software is structured.

---

# Cheat Sheet

```python
def function():
    pass

def add(a, b):
    return a + b

def greet(name="Guest"):
    print(name)

import module

from module import function

if __name__ == "__main__":
    main()
```

---

# Key Takeaways

- Functions make code reusable and maintainable.
- Parameters receive values; arguments provide them.
- Prefer `return` over `print`.
- Local variables exist only inside functions.
- Global variables should be used sparingly.
- Modules organize related functionality into separate files.
- Use explicit imports for clarity.
- `if __name__ == "__main__":` is the standard way to define a program's entry point.

---

# Revision Checklist

- [ ] Can create reusable functions.
- [ ] Understand parameter vs argument.
- [ ] Can use return values correctly.
- [ ] Know the difference between local and global variables.
- [ ] Can create and import modules.
- [ ] Understand the purpose of `if __name__ == "__main__":`.
- [ ] Can explain all concepts confidently in an interview.

---

# Tomorrow's Preview

- File Handling
- Exception Handling
- Virtual Environments
- Clean Project Structure
- Building larger modular applications
