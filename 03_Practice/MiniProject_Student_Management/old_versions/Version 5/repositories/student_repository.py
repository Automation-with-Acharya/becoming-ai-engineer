from abc import ABC, abstractmethod

from models.student import Student


class StudentRepository(ABC):
    @abstractmethod
    def add_student(self, student: Student) -> Student:
        raise NotImplementedError

    @abstractmethod
    def get_all_students(self) -> list[Student]:
        raise NotImplementedError

    @abstractmethod
    def get_student_by_id(self, student_id: int) -> Student | None:
        raise NotImplementedError

    @abstractmethod
    def search_students(self, query: str) -> list[Student]:
        raise NotImplementedError

    @abstractmethod
    def delete_student(self, student_id: int) -> bool:
        raise NotImplementedError


class PostgresStudentRepository(StudentRepository):
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def add_student(self, student: Student) -> Student:
        next_id_row = self.db_helper.fetch_one(
            "SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM students"
        )
        student.id = next_id_row[0] if next_id_row else 1

        self.db_helper.execute_query(
            "INSERT INTO students (id, name) VALUES (%s, %s)",
            (student.id, student.name),
            commit=True,
        )
        return student

    def get_all_students(self) -> list[Student]:
        rows = self.db_helper.fetch_all("SELECT id, name FROM students ORDER BY id")
        return [Student(id=row[0], name=row[1]) for row in rows]

    def get_student_by_id(self, student_id: int) -> Student | None:
        row = self.db_helper.fetch_one(
            "SELECT id, name FROM students WHERE id = %s",
            (student_id,),
        )
        if row is None:
            return None
        return Student(id=row[0], name=row[1])

    def search_students(self, query: str) -> list[Student]:
        rows = self.db_helper.fetch_all(
            "SELECT id, name FROM students WHERE name ILIKE %s ORDER BY id",
            (f"%{query}%",),
        )
        return [Student(id=row[0], name=row[1]) for row in rows]

    def delete_student(self, student_id: int) -> bool:
        student = self.get_student_by_id(student_id)
        if student is None:
            return False

        self.db_helper.execute_query(
            "DELETE FROM students WHERE id = %s",
            (student_id,),
            commit=True,
        )
        return True
