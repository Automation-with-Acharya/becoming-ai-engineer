# Requirments:

# Menu
# 1. Add Student
# 2. View Students
# 3. Search Student
# 4. Delete Student
# 5. Exit

# Using,

# Functions
# Lists
# Dictionaries
# Loops
# Input validation

# No classes yet.

# Add Student function should take student name as input and assign a unique ID to the student. The ID should be an integer starting from 1 and incrementing by 1 for each new student added.
def add_student(students):
    name = input("Enter student name: ")
    if len(students) == 0:
        id = 1
    else:
        id = max(students.keys()) + 1
    students[id] = name
    
    print(f"Student {name} added successfully.")

# View Students function should display the list of students with their IDs and names. If there are no students, it should display a message indicating that there are no students.
def view_students(students):
    if not students: # or len(students) == 0
        print("No students found.")
    else:
        print("List of Students:")
        for item in students:
            print(f"ID: {item}, Name: {students[item]}")

    print("\n")

# Search Student function should allow the user to search for a student by ID or name. If the student is found, it should display the student's ID and name. If not found, it should display a message indicating that the student was not found.
def search_student(students):
    user_input = input("Enter student ID or student name to search: ")
    try:
        searched_id = int(user_input)
        if searched_id in students:
            print(f"Student found: ID: {searched_id}, Name: {students[searched_id]}")
        else:
            print("Student not found.")
        
    except:
        searched_name = user_input
        search_results = [k for k, v in students.items() if v == searched_name]
        found_students_count = len(search_results)
        if searched_name in students.values():
            found_id = students.get(searched_name) 
            print(f"{found_students_count} Student(s) found: ID(s): {', '.join(str(id) for id in search_results)} , Name: {searched_name}")
            
        else:
            print("Student not found.")


# Delete Student function should allow the user to delete a student by ID or name. If the student is found and deleted, it should display a message indicating that the student was deleted successfully. If not found, it should display a message indicating that the student was not found.
def delete_student(students):
    user_input = input("Enter student ID or student name to delete: ")
    try:
        delete_id = int(user_input)
        if delete_id in students:
            deleted_name = students.pop(delete_id)
            print(f"Student {deleted_name} with ID {delete_id} deleted successfully.")
        else:
            print("Student not found.")
        
    except:
        delete_name = user_input
        delete_results = [k for k, v in students.items() if v == delete_name]
        found_students_count = len(delete_results)
        if delete_name in students.values():
            for id in delete_results:
                students.pop(id)
            print(f"{found_students_count} Student(s) with Name '{delete_name}' deleted successfully.")
            
        else:
            print("Student not found.")


def main():
    
    students = {}

    while True:
        print("\nMenu:")
        print("1. Add Student")
        print("2. View Students")
        print("3. Search Student")
        print("4. Delete Student")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            add_student(students)
        elif choice == '2':
            view_students(students)
        elif choice == '3':
            search_student(students)
        elif choice == '4':
            delete_student(students)
        elif choice == '5':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")







if __name__ == "__main__":
    print("\n---------- Welcome to Student Management CLI ----------")
    main()

