"""
Student Router Module.

This module handles routing user requests and managing CLI user interface interaction.
Delegates requests to StudentService and formats output responses.
"""

from services.student_service import StudentService


class StudentRouter:
    """
    Router class handling CLI interactions and routing commands for Student operations.
    """

    def __init__(self, service: StudentService):
        """
        Initialize StudentRouter with StudentService instance.

        Args:
            service (StudentService): Service instance for business logic.
        """
        self.service = service

    def display_menu(self):
        """Display CLI options menu."""
        print("\nMenu:")
        print("1. Add Student")
        print("2. View Students")
        print("3. Search Student")
        print("4. Delete Student")
        print("5. Exit")

    def handle_add_student(self):
        """Prompt user and process adding a new student."""
        name = input("Enter student name: ").strip()
        try:
            student = self.service.add_student(name)
            print(f"Student {student.name} added successfully.")
        except ValueError as exc:
            print(str(exc))

    def handle_view_students(self):
        """Display list of all registered students."""
        students = self.service.get_all_students()
        if not students:
            print("No students found.")
            return

        print("List of Students:")
        for student in students:
            print(f"ID: {student.id}, Name: {student.name}")

    def handle_search_student(self):
        """Prompt user and search for students by ID or name keyword."""
        query = input("Enter student ID or student name to search: ").strip()
        if query.isdigit():
            student = self.service.get_student_by_id(int(query))
            if student:
                print(f"Student found: ID: {student.id}, Name: {student.name}")
            else:
                print("Student not found.")
            return

        students = self.service.search_students(query)
        if students:
            print(f"{len(students)} Student(s) found:")
            for student in students:
                print(f"ID: {student.id}, Name: {student.name}")
        else:
            print("Student not found.")

    def handle_delete_student(self):
        """Prompt user and delete a student by ID."""
        student_id_input = input("Enter student ID to delete: ").strip()
        if not student_id_input.isdigit():
            print("Please enter a valid numeric student ID.")
            return

        deleted = self.service.delete_student(int(student_id_input))
        if deleted:
            print("Student deleted successfully.")
        else:
            print("Student not found.")

    def start(self):
        """Start the interactive CLI menu loop."""
        print("\n---------- Welcome to Student Management CLI ----------")
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-5): ").strip()

            if choice == "1":
                self.handle_add_student()
            elif choice == "2":
                self.handle_view_students()
            elif choice == "3":
                self.handle_search_student()
            elif choice == "4":
                self.handle_delete_student()
            elif choice == "5":
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please try again.")
