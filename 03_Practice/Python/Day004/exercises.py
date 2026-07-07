# Day 004 - OOP Practice Exercises
# These examples are intentionally simple to help understand object-oriented thinking.


class Car:
    """Represents a car with basic details."""

    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year

    def display(self):
        """Print the car details."""
        print(f"Car: {self.brand} {self.model} ({self.year})")


# 2. Create three Employee objects with different values.
class Employee:
    """Represents an employee."""

    def __init__(self, employee_id, name, salary):
        self.employee_id = employee_id
        self.name = name
        self.salary = salary

    def display(self):
        """Print employee details."""
        print(f"ID: {self.employee_id}, Name: {self.name}, Salary: {self.salary}")


# 3. Create a simple Calculator class.
class Calculator:
    """Performs basic arithmetic operations."""

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            return "Cannot divide by zero"
        return a / b


# 4. Create a BankAccount class with deposit and withdraw methods.
class BankAccount:
    """Represents a simple bank account."""

    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount > self.balance:
            return "Insufficient balance"
        self.balance -= amount
        return self.balance


# 5. Create a Rectangle class that calculates area and perimeter.
class Rectangle:
    """Represents a rectangle and calculates its area and perimeter."""

    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width

    def perimeter(self):
        return 2 * (self.length + self.width)


# Example usage
if __name__ == "__main__":
    print("Car example")
    car1 = Car("Toyota", "Corolla", 2022)
    car1.display()

    print("\nEmployee example")
    emp1 = Employee(101, "Aman", 50000)
    emp2 = Employee(102, "Neha", 60000)
    emp3 = Employee(103, "Ravi", 55000)

    emp1.display()
    emp2.display()
    emp3.display()

    print("\nCalculator example")
    calc = Calculator()
    print("Add:", calc.add(10, 5))
    print("Subtract:", calc.subtract(10, 5))
    print("Multiply:", calc.multiply(10, 5))
    print("Divide:", calc.divide(10, 5))

    print("\nBank account example")
    account = BankAccount(1000)
    print("Deposit:", account.deposit(500))
    print("Withdraw:", account.withdraw(200))

    print("\nRectangle example")
    rect = Rectangle(6, 4)
    print("Area:", rect.area())
    print("Perimeter:", rect.perimeter())
