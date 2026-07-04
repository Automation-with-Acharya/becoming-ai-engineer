# Day 001 --- Python Basics

> **Project ₹50L \| 365-Day Career Transformation**
>
> **Date:** 3 July 2026

---

# Learning Objectives

Today you will:

- Understand Python fundamentals.
- Refresh core syntax.
- Learn the most commonly used built-in data structures.
- Practice writing clean Python code.
- Build a strong foundation for FastAPI and AI engineering.

---

# 1. Variables

## Definition

A variable is a **named reference** to an object in memory.

Python is **dynamically typed**, meaning you do not declare a type
explicitly.

```python
name = "Mayank"
age = 27
salary = 13.0
```

## Naming Rules

### ✅ Valid

```python
employee_name
salary2026
_first_name
```

### ❌ Invalid

```python
1salary
employee-name
class
```

## Best Practices

- Use **snake_case**
- Use meaningful names
- Avoid one-letter variable names except for loop counters

Example:

```python
employee_name = "Mayank"
monthly_salary = 1300000
experience_years = 6
```

### Interview Question

**Does Python require variable declarations?**

**Answer:** No. Variables are created automatically when assigned.

---

# 2. Strings

## Definition

Strings are **immutable sequences of Unicode characters**.

```python
city = "Ahmedabad"
```

## Common Methods

```python
len(city)
city.upper()
city.lower()
city.replace("A", "a")
city.strip()
city.split()
city.find("bad")
city.startswith("Ah")
city.endswith("bad")
```

## String Slicing

```python
city[0]
city[-1]
city[1:4]
city[::-1]
```

### Interview Question

**Why are strings immutable?**

- Better performance
- Safe hashing
- Thread safety

---

# 3. Lists

## Definition

Lists are:

- Ordered
- Mutable
- Allow duplicates

```python
skills = ["Python", "React"]
```

## Common Methods

```python
append()
extend()
insert()
remove()
pop()
sort()
reverse()
clear()
copy()
```

## List Comprehension

```python
squares = [x * x for x in range(10)]
```

---

# 4. Tuples

Tuples are:

- Ordered
- Immutable
- Allow duplicates

```python
point = (10, 20)
```

Use tuples when data should never change.

---

# 5. Sets

Sets are:

- Unordered
- Mutable
- Store unique values only

```python
numbers = {1, 2, 3}
```

## Common Methods

```python
add()
remove()
union()
intersection()
difference()
```

---

# 6. Dictionaries

Store data as **key-value pairs**.

```python
employee = {
    "name": "Mayank",
    "experience": 6,
    "company": "Bank of America"
}
```

## Common Methods

```python
keys()
values()
items()
get()
update()
pop()
```

### Best Practice

Prefer:

```python
employee.get("name")
```

instead of

```python
employee["name"]
```

when a key may not exist.

---

# 7. if Statement

```python
salary = 13

if salary < 25:
    print("Need Career Transformation")
```

---

# 8. for Loop

```python
skills = ["Python", "React"]

for skill in skills:
    print(skill)
```

---

# 9. while Loop

```python
count = 1

while count <= 5:
    print(count)
    count += 1
```

---

# 10. Functions

```python
def greet(name):
    return f"Hello {name}"

print(greet("Mayank"))
```

---

# Mutable vs Immutable

Mutable Immutable

---

List String
Dictionary Tuple
Set Integer
Set Float

---

# Time Complexity Cheat Sheet

Operation Complexity

---

List append O(1)
List search O(n)
Dictionary lookup O(1)
Set lookup O(1)

---

# Common Beginner Mistakes

❌

```python
my_list = list()
```

✅

```python
my_list = []
```

---

Avoid this unless the key definitely exists:

```python
employee["salary"]
```

Prefer:

```python
employee.get("salary")
```

---

# Interview Questions

1.  Difference between List and Tuple?
2.  Difference between Set and Dictionary?
3.  Mutable vs Immutable?
4.  Why is dictionary lookup generally O(1)? => Both Dictionary (Dict) and Set lookups achieve O(1) average time complexity because they are implemented using an underlying data structure called a Hash Table. step1 = The Hash Function: When you look up a key in a dictionary or an item in a set, the system passes that item into a mathematical function called a hash function. This function instantly converts the item into a unique integer (the hash value). step2 = Direct Array Indexing: The hash table allocates a contiguous block of memory (an array) under the hood. The system takes the hash value and maps it to a specific index in that array. step3 =Constant Time Access: Since computers can access any random index of a contiguous array in constant O(1) time via basic pointer arithmetic, the system jumps straight to the exact location of your item without scanning anything else.
5.  Difference between `==` and `is`?

---

# Python Cheat Sheet

```python
len()
type()
print()
range()
enumerate()
zip()
sorted()
sum()
min()
max()
any()
all()
```

---

# Key Takeaways

- Python is dynamically typed.
- Strings are immutable.
- Lists are ordered and mutable.
- Tuples are immutable.
- Sets remove duplicates.
- Dictionaries provide fast lookups.
- Functions improve code reuse.
- Prefer readable code over clever code.

---

# Day 1 Deliverables

- [ ] Read official Python tutorial sections
- [ ] Watch CS50P Lecture 0 & 1 (selected portions)
- [ ] Solve 10 Python problems
- [ ] Commit code to GitHub
- [ ] Complete `day01.py`
