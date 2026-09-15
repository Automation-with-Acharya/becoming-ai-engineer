"""
Exceptions package — Day 018: Global Exception Handling.

Exposes all custom application exceptions from a single import location.
"""

from .student_exceptions import StudentNotFoundException

__all__ = ["StudentNotFoundException"]
