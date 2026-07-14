import psycopg
from database_helper import DatabaseHelper


def print_students(title, rows):
    print(f"\n{title}")
    if not rows:
        print("No students found.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, City: {row[3]}")


def main():
    helper = DatabaseHelper()

    try:
        helper.connect()
        print("✅ Connected to PostgreSQL successfully")

        # Experiment 1: Retrieve all students
        print_students("Experiment 1 - Retrieve all students", helper.fetch_all_students())

        # Experiment 2: Insert a new student
        helper.insert_student(4, "Aisha", 22, "Mumbai")
        print("✅ Experiment 2 - Inserted student with ID 4")

        # Experiment 3: Update a student's city
        helper.update_student_city(2, "Delhi")
        print("✅ Experiment 3 - Updated student 2 city")

        # Experiment 4: Delete a student
        helper.delete_student(4)
        print("✅ Experiment 4 - Deleted student with ID 4")

        # Experiment 5: Retrieve all students again
        print_students("Experiment 5 - Retrieve all students again", helper.fetch_all_students())

        # Experiment 6: Parameterized SQL examples
        print("\nExperiment 6 - Parameterized SQL examples")

        with helper.connection.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE id = %s", (1,))
            print("Parameterized SELECT result:", cur.fetchone())

            cur.execute(
                "SELECT * FROM students WHERE city = %s ORDER BY id",
                ("Delhi",),
            )
            print("Parameterized SELECT by city result:", cur.fetchall())

            cur.execute(
                "INSERT INTO students (id, name, age, city) VALUES (%s, %s, %s, %s)",
                (5, "Zara", 23, "Chennai"),
            )
            helper.connection.commit()
            print("Parameterized INSERT completed")

            cur.execute("DELETE FROM students WHERE id = %s", (5,))
            helper.connection.commit()
            print("Parameterized DELETE completed")

    except Exception as e:
        print(f"❌ Error: {e}")
        if helper.connection is not None:
            helper.connection.rollback()

    finally:
        helper.close()
        print("\n🔒 Connection closed successfully")


if __name__ == "__main__":
    main()
