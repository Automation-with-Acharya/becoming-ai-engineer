"""
Custom Application Exceptions — Day 018 Exercise 2: Custom Exception Class.

Why a custom exception instead of a plain HTTPException?
---------------------------------------------------------
Raising `HTTPException` directly inside the service layer would couple business
logic to the HTTP transport layer — a clean-architecture violation.  The service
has no business knowing what HTTP status code to use; that decision belongs in the
presentation layer (router) or in a dedicated global exception handler.

Instead, we define domain-specific Python exceptions here.  The global exception
handler in main.py converts them to the appropriate HTTP response, keeping each
layer focused on its own responsibility.
"""


# ──────────────────────────────────────────────────────────────────────────────
# Day 018 Exercise 2: Custom Exception — StudentNotFoundException
# ──────────────────────────────────────────────────────────────────────────────

class StudentNotFoundException(Exception):
    """
    Raised when a student lookup by ID yields no result.

    Carries the requested student_id so the exception handler can embed it
    in the error response without having to re-parse the request.

    Usage (service layer):
        raise StudentNotFoundException(student_id=42)

    Caught by (main.py):
        @app.exception_handler(StudentNotFoundException)
    """

    def __init__(self, student_id: int):
        self.student_id = student_id
        # Human-readable message used by str(exc) and logger output
        super().__init__(f"Student with ID {student_id} not found.")
