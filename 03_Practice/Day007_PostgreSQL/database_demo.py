import psycopg


def main():
    # Initialize connection variable
    conn = None

    try:
        # Connect to the PostgreSQL database
        conn = psycopg.connect(
            dbname="student_db",              # Name of the database
            user="postgres",                  # PostgreSQL username
            password="password@postgres",     # Password for the user
            host="localhost",                 # Database host
            port="5432",                      # Default PostgreSQL port
        )
        print("✅ Connected to PostgreSQL successfully")

        # Create a cursor to execute SQL queries
        with conn.cursor() as cur:
            # Fetch all student records from the students table
            cur.execute("SELECT id, name, age, city FROM students ORDER BY id")
            rows = cur.fetchall() # Fetch all rows from the executed query - returns a list of tuples, where each tuple represents a row in the result set.
            # rows = [(1, 'Mayank', 27, 'Gandhinagar'), (2, 'Rahul', 26, 'Ahmedabad'), (3, 'Priya', 24, 'Surat'), (5, 'xyz', 25, 'Ahmedabad'), (6, 'ABC', 24, 'Surat')]

        print("\n📋 Student Records:")

        # Print the retrieved student records
        if not rows:
            print("No student records found.")
        else:
            for row in rows:
                print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, City: {row[3]}")

    except Exception as e:
        # Handle any errors that occur during the process
        print(f"❌ Error: {e}")

    finally:
        # Ensure the connection is closed even if an error occurs
        if conn is not None:
            conn.close()
            print("\n🔒 Connection closed successfully")


if __name__ == "__main__":
    main()
