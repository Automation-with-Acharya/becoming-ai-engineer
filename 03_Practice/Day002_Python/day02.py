# Example 1
# Function
def greet():
    print("Hello Mayank")

greet()


# Example 2

# Parameters

def greet(name):
    print(f"Hello {name}")

greet("Mayank")


# Example 3

# Return

def square(number):
    return number * number

result = square(5)

print(result)


# Example 4

# Default Parameter

def greet(name="Guest"):
    print(name)

greet()

greet("Mayank")


# Example 5

# Global

company = "Bank of America"

def display():
    print(company)

display()


# Example 6

# Local

def display():
    company = "OpenAI"
    print(company)

display()


# Example 7

# Module

# Create

# math_utils.py
# def add(a,b):
#     return a+b


import math_utils

print(math_utils.add(5,3))


# Example 8

# Another Import

from math_utils import add

print(add(5,3))


# Example 9

# Main

def main():
    print("Career Transformation")

if __name__ == "__main__":
    main()