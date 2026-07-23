"""
Student Schema Module.

This module provides data validation and formatting utilities for student inputs.
Schemas ensure that input data is valid and clean before passing to business logic.
"""


class StudentSchema:
    """
    Validation schema for student input data.
    """

    @staticmethod
    def validate_student_name(name: str) -> str:
        """
        Validate and sanitize student name input.

        Args:
            name (str): Raw student name input.

        Returns:
            str: Cleaned student name.

        Raises:
            ValueError: If student name is empty or whitespace-only.
        """
        if not name:
            raise ValueError("Name cannot be empty.")

        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("Name cannot be empty.")

        return cleaned_name
