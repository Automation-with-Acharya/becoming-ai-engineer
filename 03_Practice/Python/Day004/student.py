# This file defines the Student class.
# A class is used here to group related data (student_id, name, age)
# and behavior (displaying details, converting to file text) together.


class Student:
    """Represents one student in the system."""

    def __init__(self, student_id, name, age):
        # These are instance variables.
        # Every Student object will have its own copy of these values.
        self.student_id = student_id
        self.name = name
        self.age = age

    def display(self):
        """Print the student's details in a readable format."""
        print("-" * 30)
        print(f"ID   : {self.student_id}")
        print(f"Name : {self.name}")
        print(f"Age  : {self.age}")

    def to_record(self):
        """Convert the student object into a line of text for saving to a file."""
        return f"{self.student_id},{self.name},{self.age}"
