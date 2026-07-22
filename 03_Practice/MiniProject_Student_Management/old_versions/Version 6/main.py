"""
Main Application Entry Point.

Bootstraps the PostgreSQL Student Management CLI application across all layers:
Database -> Repository -> Service -> Router.
"""

from database.database_helper import DatabaseHelper
from repositories.student_repository import PostgresStudentRepository
from services.student_service import StudentService
from routers.students import StudentRouter


def main():
    """
    Main execution function bootstrapping application components.
    """
    # Step 1: Initialize Database Helper (psycopg PostgreSQL connection)
    db_helper = DatabaseHelper()
    db_helper.connect()
    print("Connected to PostgreSQL successfully.")

    try:
        # Step 2: Initialize Repository Layer
        repository = PostgresStudentRepository(db_helper)

        # Step 3: Initialize Service Layer
        service = StudentService(repository)

        # Step 4: Initialize Router Layer
        router = StudentRouter(service)

        # Step 5: Start CLI interactive menu
        router.start()

    finally:
        # Step 6: Close Database Connection safely on exit
        db_helper.close()


if __name__ == "__main__":
    main()
