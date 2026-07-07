# This file manages a collection of Student objects.
# The StudentManager class handles all student-related operations,
# while the Student class only represents one student.

from pathlib import Path

from student import Student


class StudentManager:
    """Handles student operations such as adding, searching, deleting, and saving."""

    def __init__(self, filename):
        # filename stores the location of the text file used for data persistence.
        # We convert it to a Path object so file checks and open() work correctly.
        self.filename = Path(filename)

        # When the manager is created, it immediately loads any existing students.
        self.students = self.load_from_file()

    def add_student(self, name, age):
        """Create a new Student object, add it to the list, and save to file."""
        # Give the new student a unique ID.
        # If there are no students, start from 1.
        # Otherwise, use the last student's ID + 1.
        student_id = 1 if not self.students else self.students[-1].student_id + 1

        # Create a Student object using the class from student.py.
        student = Student(student_id, name, age)

        # Add the new object to the list of students.
        self.students.append(student)

        # Save the updated list to the file.
        self.save_to_file()
        return student

    def search_student(self, search_value):
        """Return a list of students that match the given ID or name."""
        results = []

        # Loop through each student object and compare with the search input.
        for student in self.students:
            if str(student.student_id) == str(search_value) or student.name == str(search_value):
                results.append(student)
        return results

    def delete_student(self, search_value):
        """Delete the first matching student and save the changes to the file."""
        for student in self.students:
            if str(student.student_id) == str(search_value) or student.name == str(search_value):
                self.students.remove(student)
                self.save_to_file()
                return True
        return False

    def view_students(self):
        """Display all students currently stored in memory."""
        if not self.students:
            print("No students found.")
            return []

        print("List of Students:")
        for student in self.students:
            student.display()
        return self.students

    def load_from_file(self):
        """Load student data from the text file into a list of Student objects."""
        students = []

        # If the file does not exist yet, there is nothing to load.
        if not self.filename.exists():
            return students

        with open(self.filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                # Each line is stored like: id,name,age
                student_id, name, age = line.split(",")
                students.append(Student(int(student_id), name, int(age)))
        return students

    def save_to_file(self):
        """Write all students to the file in a simple CSV-style format."""
        with open(self.filename, "w", encoding="utf-8") as file:
            for student in self.students:
                file.write(student.to_record() + "\n")

    def run_cli(self):
        """Start the interactive menu-based command-line interface."""
        while True:
            print("\nMenu:")
            print("1. Add Student")
            print("2. View Students")
            print("3. Search Student")
            print("4. Delete Student")
            print("5. Exit")

            choice = input("Enter your choice (1-5): ").strip()

            # Option 1: add a new student
            if choice == "1":
                name = input("Enter student name: ").strip()
                age_input = input("Enter student age: ").strip()
                try:
                    age = int(age_input)
                except ValueError:
                    print("Age must be a number.")
                    continue

                student = self.add_student(name, age)
                print(f"Student {student.name} added successfully.")

            # Option 2: display all students
            elif choice == "2":
                self.view_students()

            # Option 3: search by ID or name
            elif choice == "3":
                search_value = input("Enter student ID or student name to search: ").strip()
                results = self.search_student(search_value)
                if results:
                    print("Student(s) found:")
                    for student in results:
                        student.display()
                else:
                    print("Student not found.")

            # Option 4: delete by ID or name
            elif choice == "4":
                search_value = input("Enter student ID or student name to delete: ").strip()
                deleted = self.delete_student(search_value)
                if deleted:
                    print("Student deleted successfully.")
                else:
                    print("Student not found.")

            # Option 5: exit the loop and end the program
            elif choice == "5":
                print("Exiting the program.")
                break

            # Any other input is invalid
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Create the manager and point it to the students.txt file.
    # Using the script directory makes the program work even if the current folder changes.
    base_dir = Path(__file__).resolve().parent
    manager = StudentManager(base_dir / "students.txt")
    print("\n---------- Welcome to Student Management CLI ----------")
    manager.run_cli()
