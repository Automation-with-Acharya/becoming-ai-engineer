# Day 004 — Object-Oriented Programming (OOP): Classes & Objects

> **Project ₹50L | 365-Day Career Transformation**
>
> **Date:** 07 July 2026

---

# Learning Objectives

By the end of this chapter, you should be able to:

- Understand Object-Oriented Programming (OOP).
- Differentiate between a Class and an Object.
- Create classes and objects.
- Understand constructors (`__init__`).
- Use instance variables.
- Create and call methods.
- Understand the purpose of `self`.
- Design simple real-world objects.

---

# 1. What is Object-Oriented Programming (OOP)?

## Definition

Object-Oriented Programming (OOP) is a programming paradigm where software is designed using **objects** instead of only functions.

Each object contains:

- Data (Attributes)
- Behaviour (Methods)

Instead of asking:

> "What function should I write?"

Think:

> "What objects exist in my system, and what responsibilities do they have?"

---

# Why OOP?

Without OOP:

- Code becomes difficult to manage.
- Data and functions are separated.
- Large applications become hard to maintain.

With OOP:

- Better organization
- Reusability
- Scalability
- Easier maintenance
- Better modeling of real-world systems

---

# 2. Class

## Definition

A **class** is a blueprint used to create objects.

Think of it as a design or template.

Example:

```python
class Student:
    pass
```

This creates a class named `Student`.

---

# Real-World Analogy

Blueprint → House

Class → Object

A blueprint is not a house.

Using the blueprint, many houses can be built.

Similarly,

A class is not an object.

Objects are created from the class.

---

# 3. Object

## Definition

An **object** is an instance of a class.

```python
student = Student()
```

Here,

- `Student` → Class
- `student` → Object

---

Multiple objects can be created from one class.

```python
student1 = Student()

student2 = Student()

student3 = Student()
```

Each object is independent.

---

# 4. Constructor (`__init__`)

## Definition

A constructor is a special method that automatically executes whenever an object is created.

```python
class Student:

    def __init__(self):
        print("Student Created")
```

Creating an object:

```python
student = Student()
```

Output

```text
Student Created
```

---

# Constructor with Parameters

```python
class Student:

    def __init__(self, student_id, name, age):

        self.student_id = student_id
        self.name = name
        self.age = age
```

Object creation

```python
student = Student(101, "Mayank", 27)
```

---

# Why Constructors?

They initialize object data immediately after creation.

Without constructors, every attribute would need to be assigned manually.

---

# 5. self Keyword

## Definition

`self` refers to the current object.

Whenever a method is called,

Python automatically passes the current object as the first argument.

Example

```python
class Student:

    def display(self):

        print("Hello")
```

Calling

```python
student.display()
```

is internally equivalent to

```python
Student.display(student)
```

---

# Why use `self`?

It allows methods to access and modify the object's own data.

---

# 6. Instance Variables

## Definition

Instance variables store information that belongs to a specific object.

Example

```python
class Student:

    def __init__(self, name):

        self.name = name
```

Each object stores its own value.

```python
student1 = Student("Mayank")

student2 = Student("Rahul")
```

Output

```text
student1.name → Mayank

student2.name → Rahul
```

---

# Instance Variables vs Local Variables

| Instance Variable          | Local Variable                     |
| -------------------------- | ---------------------------------- |
| Stored inside object       | Exists only inside a method        |
| Accessible by all methods  | Accessible only within that method |
| Lifetime = Object lifetime | Lifetime = Method execution        |

---

# 7. Methods

## Definition

Methods are functions defined inside a class.

They describe the behaviour of an object.

Example

```python
class Student:

    def display(self):

        print(self.name)
```

Calling

```python
student.display()
```

---

# Methods Can Modify Object State

```python
class BankAccount:

    def __init__(self, balance):

        self.balance = balance

    def deposit(self, amount):

        self.balance += amount
```

Methods allow objects to change over time.

---

# 8. Multiple Objects

Example

```python
employee1 = Employee(1, "Mayank")

employee2 = Employee(2, "Rahul")

employee3 = Employee(3, "Priya")
```

Each object stores different data while sharing the same class structure.

---

# 9. Updating Object State

Objects are mutable.

Example

```python
student.name = "Acharya"

student.age = 28
```

Or through methods

```python
def birthday(self):

    self.age += 1
```

Using methods is preferred because it keeps object behaviour controlled.

---

# OOP Workflow

```text
Class
   │
Create Object
   │
Constructor Executes
   │
Instance Variables Created
   │
Methods Operate on Object
   │
Object State Changes
```

---

# Best Practices

✅ One class should represent one concept.

Good

```python
Student

Employee

BankAccount

Car
```

Avoid

```python
EverythingManager
```

---

Keep methods short.

Use meaningful class names.

Use meaningful attribute names.

Keep related data and behaviour together.

---

# Common Mistakes

❌ Forgetting `self`.

❌ Accessing instance variables without `self`.

```python
name
```

Instead of

```python
self.name
```

---

❌ Creating unnecessary global variables.

---

❌ Writing one huge class with dozens of responsibilities.

---

# Interview Questions

### Q1. What is OOP?

A programming paradigm based on objects containing data and behaviour.

---

### Q2. Difference between Class and Object?

Class → Blueprint

Object → Instance created from the blueprint.

---

### Q3. What is a Constructor?

A special method (`__init__`) automatically called when an object is created.

---

### Q4. Why is `self` required?

It refers to the current object and allows methods to access instance variables.

---

### Q5. What are Instance Variables?

Variables belonging to a specific object.

Each object has its own copy.

---

### Q6. Difference between Function and Method?

Function

- Independent
- Outside class

Method

- Inside class
- Operates on object data

---

# Real-World Usage

Imagine an online banking system.

Objects:

```text
Customer

Account

Transaction

Card

Loan
```

Each object stores its own data and provides its own behaviour.

For example:

Account

Data

- Account Number
- Balance

Methods

- Deposit
- Withdraw
- Transfer

This mirrors how enterprise software is designed.

---

# Cheat Sheet

```python
class Student:

    def __init__(self, name):

        self.name = name

    def display(self):

        print(self.name)

student = Student("Mayank")

student.display()
```

---

# Key Takeaways

- OOP organizes software around objects.
- A class is a blueprint; an object is an instance.
- Constructors initialize object data.
- `self` refers to the current object.
- Instance variables store object-specific data.
- Methods define object behaviour.
- Objects can maintain and update their own state.
- OOP improves scalability, maintainability, and code organization.

---

# Revision Checklist

- [ ] Can explain OOP in simple words.
- [ ] Know the difference between Class and Object.
- [ ] Can create classes and objects.
- [ ] Understand constructors.
- [ ] Know why `self` is required.
- [ ] Can use instance variables correctly.
- [ ] Can write methods inside classes.
- [ ] Understand how objects maintain state.
- [ ] Can confidently explain these concepts in an interview.

---

# Tomorrow's Preview

- Pillars of OOP
  - Encapsulation
  - Inheritance
  - Polymorphism
  - Abstraction

- Composition vs Inheritance
- Refactoring the Student Management CLI into a more extensible design
- Introduction to professional project architecture
