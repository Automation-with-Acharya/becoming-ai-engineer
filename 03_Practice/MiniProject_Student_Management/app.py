from database_helper import DatabaseHelper
from repositories.student_repository import PostgresStudentRepository
from services.student_service import StudentService


class StudentManagementCLI:
    def __init__(self):
        self.db_helper = DatabaseHelper()
        self.repository = PostgresStudentRepository(self.db_helper)
        self.service = StudentService(self.repository)

    def run(self):
        self.db_helper.connect()
        print("Connected to PostgreSQL successfully.")

        while True:
            print("\nMenu:")
            print("1. Add Student")
            print("2. View Students")
            print("3. Search Student")
            print("4. Delete Student")
            print("5. Exit")

            choice = input("Enter your choice (1-5): ").strip()

            if choice == "1":
                self._add_student()
            elif choice == "2":
                self._view_students()
            elif choice == "3":
                self._search_student()
            elif choice == "4":
                self._delete_student()
            elif choice == "5":
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please try again.")

        self.db_helper.close()

    def _add_student(self):
        name = input("Enter student name: ").strip()
        try:
            student = self.service.add_student(name)
            print(f"Student {student.name} added successfully.")
        except ValueError as exc:
            print(str(exc))

    def _view_students(self):
        students = self.service.get_all_students()
        if not students:
            print("No students found.")
            return

        print("List of Students:")
        for student in students:
            print(f"ID: {student.id}, Name: {student.name}")

    def _search_student(self):
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

    def _delete_student(self):
        student_id_input = input("Enter student ID to delete: ").strip()
        if not student_id_input.isdigit():
            print("Please enter a valid numeric student ID.")
            return

        deleted = self.service.delete_student(int(student_id_input))
        if deleted:
            print("Student deleted successfully.")
        else:
            print("Student not found.")


if __name__ == "__main__":
    print("\n---------- Welcome to Student Management CLI ----------")
    StudentManagementCLI().run()
