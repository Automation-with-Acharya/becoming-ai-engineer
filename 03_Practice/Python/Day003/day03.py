# 1. try / except
# Example 1 - Division by Zero

print("Example 1 - try / except")

try:
    number = int(input("Enter a number: "))
    result = 100 / number
    print(f"Result: {result}")

except ZeroDivisionError:
    print("❌ Cannot divide by zero.")

except ValueError:
    print("❌ Please enter a valid integer.")


# Example 2 - List Index

print("\nExample 2 - List Index")

numbers = [10, 20, 30]

try:
    index = int(input("Enter index (0-2): "))
    print(numbers[index])

except IndexError:
    print("❌ Index out of range.")

except ValueError:
    print("❌ Please enter a valid integer.")


# 2. try / except / else / finally

print("\nExample 3 - try / except / else / finally")

try:
    age = int(input("Enter your age: "))

except ValueError:
    print("❌ Invalid age.")

else:
    print(f"✅ Age accepted: {age}")

finally:
    print("Program Finished.")


# 3. Writing to a Text File

print("\nExample 4 - Writing to File")

file = open("students.txt", "w")

file.write("Mayank\n")
file.write("Rahul\n")
file.write("Priya\n")

file.close()

print("Data written successfully.")


# 4. Reading a Text File

print("\nExample 5 - Reading File")

file = open("students.txt", "r")

content = file.read()

print(content)

file.close()


# 5. Appending to a Text File

print("\nExample 6 - Append File")

file = open("students.txt", "a")

file.write("Anjali\n")

file.close()

print("Student added.")


# 6. Using with open(...)

# This is the professional way.

print("\nExample 7 - with open")

with open("students.txt", "r") as file:
    content = file.read()

print(content)
# Notice that, There is no need to explicitly close the file when using 'with' statement.


# 7. Reading Line by Line

print("\nExample 8 - Read Line by Line")

with open("students.txt", "r") as file:

    for line in file:
        print(line.strip())
# Why strip()? Without it you'll get extra blank lines because each line already ends with \n.


# 8. File Not Found Exception

print("\nExample 9 - Missing File")

try:

    with open("abc.txt", "r") as file:
        print(file.read())

except FileNotFoundError:
    print("❌ File does not exist.")


# 9. Combining File Handling + Exception Handling

print("\nExample 10 - Safe File Reader")

filename = input("Enter file name: ")

try:

    with open(filename, "r") as file:
        print(file.read())

except FileNotFoundError:
    print("❌ File not found.")

except PermissionError:
    print("❌ Permission denied.")

finally:
    print("Finished reading file.")