from dataclasses import dataclass


@dataclass
class Student:
    id: int | None = None
    name: str = ""
