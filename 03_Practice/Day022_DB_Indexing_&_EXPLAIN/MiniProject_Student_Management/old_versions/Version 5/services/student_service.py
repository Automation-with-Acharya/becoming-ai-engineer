from models.student import Student


class StudentService:
    def __init__(self, repository):
        self.repository = repository

    def add_student(self, name: str) -> Student:
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("Name cannot be empty.")

        student = Student(name=cleaned_name)
        return self.repository.add_student(student)

    def get_all_students(self) -> list[Student]:
        return self.repository.get_all_students()

    def get_student_by_id(self, student_id: int) -> Student | None:
        return self.repository.get_student_by_id(student_id)

    def search_students(self, query: str) -> list[Student]:
        return self.repository.search_students(query.strip())

    def delete_student(self, student_id: int) -> bool:
        return self.repository.delete_student(student_id)
