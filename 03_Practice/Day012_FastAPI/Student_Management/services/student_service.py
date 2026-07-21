from dataclasses import dataclass, field

try:
    from Student_Management.models import Student_model
except ImportError:  # pragma: no cover - allows running the module directly
    from models.models import Student_model


@dataclass
class StudentService:
    students: list[Student_model] = field(default_factory=list)

    def __post_init__(self):
        if not self.students:
            self.students = [
                Student_model(name="Asha", age=20, city="Ahmedabad"),
                Student_model(name="Vikram", age=22, city="Mumbai"),
                Student_model(name="Leena", age=19, city="Ahmedabad"),
            ]

    def get_all_students(self, city: str | None = None):
        if city is None:
            return self.students
        return [student for student in self.students if student.city.lower() == city.lower()]

    def get_student_by_id(self, student_id: int):
        if 0 <= student_id < len(self.students):
            return self.students[student_id]
        return None

    def add_student(self, student: Student_model):
        self.students.append(student)
        return {"message": "Student Added", **student.model_dump()}


def get_student_service() -> StudentService:
    return StudentService()
