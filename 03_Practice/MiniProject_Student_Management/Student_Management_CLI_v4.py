from database_helper import DatabaseHelper


def add_student(db):
    # Ask the user for a student name before inserting anything into the database.
    name = input("Enter student name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    # Find the next available student ID by checking the highest existing id.
    next_id_row = db.fetch_one("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM students")
    student_id = next_id_row[0] if next_id_row else 1

    # Insert the new student into the database using a parameterized query.
    db.execute_query(
        "INSERT INTO students (id, name) VALUES (%s, %s)",
        (student_id, name),
        commit=True,
    )
    print(f"Student {name} added successfully.")


def view_students(db):
    # Retrieve every student from the database and display them in a simple list.
    students = db.fetch_all("SELECT id, name FROM students ORDER BY id")
    if not students:
        print("No students found.")
    else:
        print("List of Students:")
        for student_id, name in students:
            print(f"ID: {student_id}, Name: {name}")


def search_student(db):
    # Ask the user whether they want to search by numeric ID or by name.
    user_input = input("Enter student ID or student name to search: ").strip()

    if user_input.isdigit():
        # Search by exact ID.
        student = db.fetch_one("SELECT id, name FROM students WHERE id = %s", (int(user_input),))
        if student:
            print(f"Student found: ID: {student[0]}, Name: {student[1]}")
        else:
            print("Student not found.")
    else:
        # Search by name using a partial match so the user can type part of the name.
        students = db.fetch_all(
            "SELECT id, name FROM students WHERE name ILIKE %s ORDER BY id", # Use ILIKE for case-insensitive search
            (f"%{user_input}%",), # Use wildcards for partial matching => %xyz% will return abcxyzpqr, xyzabc, etc...
        )
        if students:
            print(f"{len(students)} Student(s) found:")
            for student_id, name in students:
                print(f"ID: {student_id}, Name: {name}")
        else:
            print("Student not found.")


def delete_student(db):
    # Ask the user whether they want to delete by numeric ID or by name.
    user_input = input("Enter student ID or student name to delete: ").strip()

    if user_input.isdigit():
        # Delete a single student by ID.
        student = db.fetch_one("SELECT id, name FROM students WHERE id = %s", (int(user_input),))
        if student:
            db.execute_query("DELETE FROM students WHERE id = %s", (student[0],), commit=True)
            print(f"Student {student[1]} with ID {student[0]} deleted successfully.")
        else:
            print("Student not found.")
    else:
        # Delete all students whose names match the given text.
        students = db.fetch_all(
            "SELECT id, name FROM students WHERE name = %s ORDER BY id",
            (user_input,),
        )
        if students:
            for student_id, name in students:
                db.execute_query("DELETE FROM students WHERE id = %s", (student_id,), commit=True)
            print(f"{len(students)} Student(s) with Name '{user_input}' deleted successfully.")
        else:
            print("Student not found.")


def main():
    # Create the helper object once and reuse it for the whole program.
    db = DatabaseHelper()

    try:
        # Connect to the PostgreSQL database when the program starts.
        db.connect()
        print("Connected to PostgreSQL successfully.")

        while True:
            # Show the main menu to the user.
            print("\nMenu:")
            print("1. Add Student")
            print("2. View Students")
            print("3. Search Student")
            print("4. Delete Student")
            print("5. Exit")

            choice = input("Enter your choice (1-5): ").strip()

            # Call the appropriate function based on user input.
            if choice == '1':
                add_student(db)
            elif choice == '2':
                view_students(db)
            elif choice == '3':
                search_student(db)
            elif choice == '4':
                delete_student(db)
            elif choice == '5':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please try again.")
    finally:
        # Always close the connection when the program ends.
        db.close()


if __name__ == "__main__":
    print("\n---------- Welcome to Student Management CLI ----------")
    main()
