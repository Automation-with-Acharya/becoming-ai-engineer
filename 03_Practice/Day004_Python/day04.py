# 1. Creating a Class
# A class is a blueprint for creating objects.

print("=" * 50)
print("Example 1 - Creating a Class")
print("=" * 50)

class Student:
    pass

print(Student)

# Output
# <class '__main__.Student'>

# ======================================================================================================

# 2. Creating Objects
# Objects are instances of a class.

print("\nExample 2 - Creating Objects")

class Student:
    pass

student1 = Student()
student2 = Student()

print(student1)
print(student2)

# Notice that both objects have different memory addresses.

# ======================================================================================================

# 3. Constructor (__init__)
# The constructor automatically executes whenever an object is created.

print("\nExample 3 - Constructor")

class Student:

    def __init__(self):
        print("Student object created!")

student = Student()

# Output
# Student object created!

# ======================================================================================================

# 4. Constructor with Parameters

print("\nExample 4 - Constructor with Parameters")

class Student:

    def __init__(self, student_id, name, age):

        self.student_id = student_id
        self.name = name
        self.age = age

student = Student(101, "Mayank", 27)

print(student.student_id)
print(student.name)
print(student.age)

# ======================================================================================================

# 5. Instance Variables
# Instance variables belong to each object individually.

print("\nExample 5 - Instance Variables")

class Student:

    def __init__(self, name):

        self.name = name

student1 = Student("Mayank")
student2 = Student("Rahul")

print(student1.name)
print(student2.name)

# Each object stores its own value.

# ======================================================================================================

# 6. Methods
# Methods are functions defined inside a class.

print("\nExample 6 - Methods")

class Student:

    def __init__(self, name):

        self.name = name

    def display(self):

        print(f"Student Name : {self.name}")

student = Student("Mayank")

student.display()

# ======================================================================================================

# 7. Multiple Objects

print("\nExample 7 - Multiple Objects")

class Employee:

    def __init__(self, emp_id, name):

        self.emp_id = emp_id
        self.name = name

    def display(self):

        print(f"{self.emp_id} - {self.name}")

employee1 = Employee(1, "Mayank")
employee2 = Employee(2, "Rahul")
employee3 = Employee(3, "Priya")

employee1.display()
employee2.display()
employee3.display()

# Observe that the same class creates completely different objects.

# ======================================================================================================

# 8. Updating Object State
# Objects can change after creation.

print("\nExample 8 - Updating Object State")

class BankAccount:

    def __init__(self, balance):

        self.balance = balance

    def deposit(self, amount):

        self.balance += amount

    def withdraw(self, amount):

        self.balance -= amount

    def display(self):

        print(f"Balance : ₹{self.balance}")

account = BankAccount(1000)

account.display()

account.deposit(500)

account.display()

account.withdraw(300)

account.display()

# Output
# Balance : ₹1000

# Balance : ₹1500

# Balance : ₹1200

# ======================================================================================================

# 9. Complete Example

print("\nExample 9 - Complete Student Class")

class Student:

    def __init__(self, student_id, name, age):

        self.student_id = student_id
        self.name = name
        self.age = age

    def display(self):

        print("-" * 30)
        print(f"ID   : {self.student_id}")
        print(f"Name : {self.name}")
        print(f"Age  : {self.age}")

student1 = Student(101, "Mayank", 27)
student2 = Student(102, "Rahul", 24)

student1.display()
student2.display()

# ======================================================================================================

# 10. Real-Life Example
# This is very close to what we'll build today.

print("\nExample 10 - Student Manager")

class Student:

    def __init__(self, student_id, name):

        self.student_id = student_id
        self.name = name

class StudentManager:

    def __init__(self):

        self.students = []

    def add_student(self, student):

        self.students.append(student)

    def display_students(self):

        for student in self.students:

            print(f"{student.student_id} - {student.name}")

manager = StudentManager()

manager.add_student(Student(1, "Mayank"))
manager.add_student(Student(2, "Rahul"))

manager.display_students()