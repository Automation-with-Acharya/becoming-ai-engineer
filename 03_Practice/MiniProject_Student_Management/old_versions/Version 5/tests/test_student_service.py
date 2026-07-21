import unittest

from services.student_service import StudentService
from models.student import Student


class FakeStudentRepository:
    def __init__(self):
        self.students = []
        self.next_id = 1

    def add_student(self, student):
        student.id = self.next_id
        self.students.append(Student(id=student.id, name=student.name))
        self.next_id += 1
        return student

    def get_all_students(self):
        return list(self.students)

    def get_student_by_id(self, student_id):
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def search_students(self, query):
        query = query.lower()
        return [
            student
            for student in self.students
            if query in student.name.lower()
        ]

    def delete_student(self, student_id):
        for index, student in enumerate(self.students):
            if student.id == student_id:
                del self.students[index]
                return True
        return False


class StudentServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakeStudentRepository()
        self.service = StudentService(self.repository)

    def test_add_student_trims_name_and_assigns_id(self):
        student = self.service.add_student("  Alice  ")

        self.assertEqual(student.name, "Alice")
        self.assertEqual(student.id, 1)

    def test_add_student_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            self.service.add_student("   ")

    def test_search_students_is_case_insensitive(self):
        self.service.add_student("Bob")
        self.service.add_student("Alice")

        results = self.service.search_students("bo")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Bob")


if __name__ == "__main__":
    unittest.main()
